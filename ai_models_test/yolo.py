from PIL import Image
from ultralytics import YOLO
import cv2
import matplotlib.pyplot as plt
import numpy as np


model = YOLO('yolov8n.pt')

async def yolov8(img:Image) -> list:
    results = model.predict(img)
    cropped_images = []

    for result in results:
        boxes = result.boxes
        for box in boxes:
            x_center, y_center, width, height = box.xywh[0][0].cpu().numpy(), box.xywh[0][1].cpu().numpy(), box.xywh[0][
                2].cpu().numpy(), box.xywh[0][3].cpu().numpy()
            left = x_center - (width / 2)
            top = y_center - (height / 2)
            right = x_center + (width / 2)
            bottom = y_center + (height / 2)
            cropped_img = img.crop((left, top, right, bottom))
            cropped_images.append(cropped_img)

    return cropped_images

