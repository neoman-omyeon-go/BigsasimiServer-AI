# builtin_module
import os, shutil
import asyncio

# module
from src.api import test
from src.util import timeCheck_function

# fast
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from typing import Union
from fastapi import FastAPI, File, UploadFile

app = FastAPI()
app.mount("/static", StaticFiles(directory="images"), name="images")

@app.get("/")
def read_root():
    return {"Hello": "World"}


async def save_file(file:UploadFile):
    try:
        os.makedirs("images", exist_ok=True)
        result = dict()
        if file.filename in ['test1.jpg', 'test2.jpg']:
            raise Exception("이미지 파일명이 잘못되었습니다.")
        # 이미지 파일 저장
        with open(os.path.join("images", file.filename), "wb") as buffer:
            result["name"]=file.filename
            result["path"]=buffer.name
            shutil.copyfileobj(file.file, buffer)
        result["message"] = "이미지가 성공적으로 업로드되었습니다."
        return JSONResponse(content=result)
    
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@app.post("/imageupload/")
async def store_file(file: UploadFile = File(...)):
    result = await save_file(file)
    return result


async def sleep_test(t:int):
    print("시작")
    for i in range(t):
        await asyncio.sleep(1)
    print("끝")
    return {"sleep": t}


@app.get("/test/{sleep}")
async def test_delay_and_model(sleep: int):
    result = await sleep_test(sleep)
    return result