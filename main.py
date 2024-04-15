from typing import Union
from fastapi import FastAPI, File, UploadFile
from src.api import test, test1

import asyncio
import time

from src.util import timeCheck_function
import os, shutil
from fastapi.responses import JSONResponse


app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/ai/{sleep}")
@timeCheck_function
def test_delay_and_model(sleep: int, q: Union[str, None] = None):
    task1=test()
    time.sleep(sleep)
    return {"sleep": sleep, "q": q}

@app.post("/files/")
async def create_file(file: bytes = File(...)):
    return {"file_size": len(file)}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    return {"filename": file.filename}

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