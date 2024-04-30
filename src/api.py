from ai_models_test.yolo import yolov8
from PIL import Image


def test():
    dest = Image.open(r"C:\Users\rlawl\Desktop\Capstone\BigsasimiServer-AI\images\test1.jpg")
    return yolov8(dest)
