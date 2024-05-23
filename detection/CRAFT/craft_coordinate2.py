# import cv2
# import numpy as np
# import re
# import shutil
# from itertools import chain
# from pathlib import Path
# import json
# import os
# def extract_boxes(text_content):
#     return re.findall(r'(\d+),(\d+),(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)', text_content)

# def crop_text_areas(img_path, txt_path, base_save_dir):
#     image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']

#     # 이미지 파일 경로 리스트 컴프리헨션으로 생성
#     image_files = [os.path.join(img_path, f) for f in os.listdir(img_path) 
#                    if any(f.endswith(ext) for ext in image_extensions)]
#     img = cv2.imread(str(image_files[0]))
#     text_path = [os.path.join(txt_path, f) for f in os.listdir(txt_path) if f.endswith('.txt')]

#     with open(text_path[0], 'r') as file:
#         text_content = file.read()
    
#     boxes = extract_boxes(text_content)
#     images_details = []

#     # save_dir = base_save_dir / f"image{img_index}"
#     save_dir = base_save_dir
#     # save_dir.mkdir(parents=True, exist_ok=True)
#     os.makedirs(save_dir,exist_ok=True)
    
#     for idx, box in enumerate(boxes):
#         x_coords = [int(box[i]) for i in range(0, 8, 2)]
#         y_coords = [int(box[i]) for i in range(1, 8, 2)]
#         min_x, max_x = min(x_coords), max(x_coords)
#         min_y, max_y = min(y_coords), max(y_coords)
#         width = max_x - min_x
#         height = max_y - min_y
#         cropped_img = img[min_y:max_y, min_x:max_x]
#         img_name = f'text_{idx}.png'
#         cv2.imwrite(str(save_dir + '/result_crop'+img_name), cropped_img)
#         # images_details[img_name] = {'x': min_x, 'y': min_y, 'w': width, 'h': height}
#         image_details_info = {'filename' : img_name, 'x' : min_x, 'y' : min_y, 'w' : width, 'h' : height}
#         images_details.append(image_details_info)

#     # details_txt_path = save_dir / f"image{img_index}_details.txt"
#     # with open(details_txt_path, 'w') as file:
#     #     file.write(json.dumps(images_details, indent=4))
        
#     # shutil.copy(txt_path, save_dir / txt_path.name)
    
#     return images_details

# base_dir = Path('/home/eslab/osh/CapStone/OCR/CRAFT-pytorch/result_c/')
# img_dir = Path('/home/mmc/disk3/ljh/result/result_crop/') # /home/eslab/osh/CapStone/yolo/yolov5/runs/detect1/object_result/crops/table  /home/eslab/osh/CapStone/detect1/object_result/
# base_save_dir = img_dir / 'crop_image'
# base_save_dir.mkdir(parents=True, exist_ok=True)

# patterns = ['*.png', '*.jpg']
# files = chain.from_iterable(img_dir.glob(pattern) for pattern in patterns)

# img_index = 0

# for img_path in files:
#     txt_filename = f"res_{img_path.stem}.txt"
#     txt_path = base_dir / txt_filename
#     if txt_path.exists():
#         images_details = crop_text_areas(img_path, txt_path, base_save_dir, img_index)
#         print(f"Processed {img_path.name}: {images_details}")
#         img_index += 1


import cv2
import re
from itertools import chain
from pathlib import Path
import os


image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']

def extract_boxes(text_content):
    return re.findall(r'(\d+),(\d+),(\d+),(\d+),(\d+),(\d+),(\d+),(\d+)', text_content)

def calculate_center(box):
    x_coords = [int(box[i]) for i in range(0, 8, 2)]
    y_coords = [int(box[i]) for i in range(1, 8, 2)]
    center_x = sum(x_coords) / len(x_coords)
    center_y = sum(y_coords) / len(y_coords)
    return center_x, center_y

def is_same_line(box1, box2):
    _, center_y1 = calculate_center(box1)
    y_coords2 = [int(box2[i]) for i in range(1, 8, 2)]
    return min(y_coords2) <= center_y1 <= max(y_coords2)

def crop_text_areas(img_path, txt_path, base_save_dir):
    
    image_files = [os.path.join(img_path, f) for f in os.listdir(img_path) 
                   if any(f.endswith(ext) for ext in image_extensions)]
    img = cv2.imread(str(image_files[0]))
    text_path = [os.path.join(txt_path, f) for f in os.listdir(txt_path) if f.endswith('.txt')]
    # img = cv2.imread(str(img_path)+'2.jpg')

    with open(text_path[0], 'r') as file:
        text_content = file.read()

    boxes = extract_boxes(text_content)
    
    # 각 박스의 중심점을 계산합니다.
    centers = [(calculate_center(box), box) for box in boxes]

    # 중앙값에 따라 정렬
    centers.sort(key=lambda x: (x[0][1], x[0][0]))

    sorted_boxes = []
    while centers:
        current_center, current_box = centers.pop(0)
        sorted_boxes.append(current_box)
        same_line = []
        for center, box in centers:
            if is_same_line(current_box, box):
                same_line.append((center, box))
        for item in same_line:
            centers.remove(item)
        same_line = sorted(same_line, key=lambda x: x[0][0])  # x 좌표 기준으로 정렬
        sorted_boxes.extend([box for _, box in same_line])

    # 자른 이미지 저장 및 단어 결합
    save_dir = base_save_dir
    os.makedirs(save_dir, exist_ok=True)
    
    images_details = []
    for idx, box in enumerate(sorted_boxes):
        x_coords = [int(box[i]) for i in range(0, 8, 2)]
        y_coords = [int(box[i]) for i in range(1, 8, 2)]
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        width = max_x - min_x
        height = max_y - min_y
        cropped_img = img[min_y:max_y, min_x:max_x]
        img_name = f'text_{idx}.png'
        cv2.imwrite(str(save_dir +'/'+ img_name), cropped_img)
        image_details_info = {'filename': img_name, 'x': min_x, 'y': min_y, 'w': width, 'h': height}
        images_details.append(image_details_info)
    
    return images_details