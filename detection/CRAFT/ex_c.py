"""  
Copyright (c) 2019-present NAVER Corp.
MIT License
"""
import os
# os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID" # 서버적용 코드
# os.environ["CUDA_VISIBLE_DEVICES"]= "1"
from .test1 import copyStateDict, str2bool, test_net

from torchvision import models
vgg16_bn = models.vgg16_bn(pretrained=True)

# -*- coding: utf-8 -*-
import sys
import os
import time
import argparse

import torch
import torch.nn as nn
import torch.backends.cudnn as cudnn
from torch.autograd import Variable

from PIL import Image

import cv2
from skimage import io
import numpy as np
from detection.CRAFT import craft_utils
from detection.CRAFT import imgproc
from detection.CRAFT import file_utils
import json
import zipfile

from detection.CRAFT.craft import CRAFT

from collections import OrderedDict
def copyStateDict(state_dict):
    if list(state_dict.keys())[0].startswith("module"):
        start_idx = 1
    else:
        start_idx = 0
    new_state_dict = OrderedDict()
    for k, v in state_dict.items():
        name = ".".join(k.split(".")[start_idx:])
        new_state_dict[name] = v
    return new_state_dict

def str2bool(v):
    return v.lower() in ("yes", "y", "true", "t", "1")





""" For test images in a folder """


def craft_crop(object_image_folder,crop_result_folder, a=0.3, b=0.3, c=0.1):
    print("a:",a, "b:",b, "c:",c)
    weight_path = f"{os.getcwd()}/detection/CRAFT/weight/craft_mlt_25k.pth"
    parser = argparse.ArgumentParser(description='CRAFT Text Detection')
    # parser.add_argument('--trained_model', type=str, help='pretrained model', default = '/home/mmc/disk3/ljh/detection/CRAFT/weight/craft_mlt_25k.pth')
    parser.add_argument('--trained_model', type=str, help='pretrained model', default = weight_path)
    parser.add_argument('--text_threshold', default=a, type=float, help='text confidence threshold') # default = 0.7, 0.4, 0.4, 0.3, 0.3, 0.3, 0.3
    parser.add_argument('--low_text', default=b, type=float, help='text low-bound score') # default = 0.4, 0.4, 0.5, 0.5, 0.3, 0.3, 0.3
    parser.add_argument('--link_threshold', default=c, type=float, help='link confidence threshold') # default = 0.4, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0
    parser.add_argument('--cuda', default=False, type=str2bool, help='Use cuda for inference')
    parser.add_argument('--canvas_size', default=1280, type=int, help='image size for inference')
    parser.add_argument('--mag_ratio', default=2.5, type=float, help='image magnification ratio') # default = 1.5, 1.5, 2.0, 2.5, 2.5, 2.5, 2.5
    parser.add_argument('--poly', default=False, action='store_true', help='enable polygon type')
    parser.add_argument('--show_time', default=False, action='store_true', help='show processing time')
    parser.add_argument('--test_folder', type=str, help='folder path to input images', default = '/home/mmc/disk3/ljh/result/result_obejct') # /home/eslab/osh/CapStone/yolo/yolov5/runs/detect, /home/eslab/osh/CapStone/data12
    parser.add_argument('--refine', default=False, action='store_true', help='enable link refiner')
    parser.add_argument('--refiner_model', default='weight/craft_refiner_CTW1500.pth', type=str, help='pretrained refiner model')

    args = parser.parse_args()

    image_list, _, _ = file_utils.get_files(object_image_folder)
    result_folder = crop_result_folder
    if not os.path.isdir(result_folder):
        os.mkdir(result_folder)

    def test_net(net, image, text_threshold, link_threshold, low_text, cuda, poly, refine_net=None):
        h, w, _ = image.shape
        print('h : ', h)
        print('w : ', w)
        if min(h, w) < 10:
            print('To small remove image')
            return [], [], None

        t0 = time.time()

        # resize
        img_resized, target_ratio, size_heatmap = imgproc.resize_aspect_ratio(image, args.canvas_size, interpolation=cv2.INTER_LINEAR, mag_ratio=args.mag_ratio)
        ratio_h = ratio_w = 1 / target_ratio

        # preprocessing
        x = imgproc.normalizeMeanVariance(img_resized)
        x = torch.from_numpy(x).permute(2, 0, 1)    # [h, w, c] to [c, h, w]
        x = Variable(x.unsqueeze(0))                # [c, h, w] to [b, c, h, w]
        if cuda:
            x = x.cuda()

        # forward pass
        with torch.no_grad():
            y, feature = net(x)

        # make score and link map
        score_text = y[0,:,:,0].cpu().data.numpy()
        score_link = y[0,:,:,1].cpu().data.numpy()

        # refine link
        if refine_net is not None:
            with torch.no_grad():
                y_refiner = refine_net(y, feature)
            score_link = y_refiner[0,:,:,0].cpu().data.numpy()

        t0 = time.time() - t0
        t1 = time.time()

        # Post-processing
        boxes, polys = craft_utils.getDetBoxes(score_text, score_link, text_threshold, link_threshold, low_text, poly)

        # coordinate adjustment
        boxes = craft_utils.adjustResultCoordinates(boxes, ratio_w, ratio_h)
        polys = craft_utils.adjustResultCoordinates(polys, ratio_w, ratio_h)
        for k in range(len(polys)):
            if polys[k] is None: polys[k] = boxes[k]

        t1 = time.time() - t1

        # render results (optional)
        render_img = score_text.copy()
        render_img = np.hstack((render_img, score_link))
        ret_score_text = imgproc.cvt2HeatmapImg(render_img)

        if args.show_time : print("\ninfer/postproc time : {:.3f}/{:.3f}".format(t0, t1))

        return boxes, polys, ret_score_text

    net = CRAFT()     # initialize

    print('Loading weights from checkpoint (' + args.trained_model + ')')
    if args.cuda:
        net.load_state_dict(copyStateDict(torch.load(args.trained_model)))
    else:
        net.load_state_dict(copyStateDict(torch.load(args.trained_model, map_location='cpu')))

    if args.cuda:
        net = net.cuda()
        net = torch.nn.DataParallel(net)
        cudnn.benchmark = False

    net.eval()

    # LinkRefiner
    refine_net = None
    if args.refine:
        from refinenet import RefineNet
        refine_net = RefineNet()
        print('Loading weights of refiner from checkpoint (' + args.refiner_model + ')')
        if args.cuda:
            refine_net.load_state_dict(copyStateDict(torch.load(args.refiner_model)))
            refine_net = refine_net.cuda()
            refine_net = torch.nn.DataParallel(refine_net)
        else:
            refine_net.load_state_dict(copyStateDict(torch.load(args.refiner_model, map_location='cpu')))

        refine_net.eval()
        args.poly = True

    t = time.time()

    # load data
    for k, image_path in enumerate(image_list):
        print("Test image {:d}/{:d}: {:s}".format(k+1, len(image_list), image_path), end='\r')
        image = imgproc.loadImage(image_path)

        bboxes, polys, score_text = test_net(net, image, args.text_threshold, args.link_threshold, args.low_text, args.cuda, args.poly, refine_net)

        # save score text
        filename, file_ext = os.path.splitext(os.path.basename(image_path))
        mask_file = result_folder + filename + '_mask.jpg'
        cv2.imwrite(mask_file, score_text)

        file_utils.saveResult(image_path, image[:,:,::-1] ,polys, dirname=result_folder)

    print("elapsed time : {}s".format(time.time() - t))
    return None
