from .ai_models_test.yolo import yolov8
from PIL import Image
import asyncio


def test():
    dest = Image.open(r"C:\Users\rlawl\Desktop\Capstone\BigsasimiServer-AI\images\test1.jpg")
    return yolov8(dest)


async def test1(sleep):
    print("!")
    await asyncio.sleep(sleep)
    return sleep