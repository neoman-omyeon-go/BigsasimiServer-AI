# builtin_module
import os, shutil
import asyncio
import uvicorn
import time

# module
from src.util import timeCheck_function, TimeCheck

# fast
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from typing import Union
from fastapi import FastAPI, File, UploadFile

# AI
# from src.AI import AI, AI_TEST
from src.AI import AI


app = FastAPI()
app.mount("/static", StaticFiles(directory="images"), name="images")

@app.get("/")
def read_root():
    return {"Hello": "World"}


async def save_file(file:UploadFile):
    try:
        os.makedirs("images", exist_ok=True)
        result = dict()
        if file.filename in ['test.png']:
            raise Exception("이미지 파일명이 잘못되었습니다.")
        # 이미지 파일 저장
        with open(os.path.join("images", file.filename), "wb") as buffer:
            result["name"]=file.filename
            result["path"]=buffer.name
            shutil.copyfileobj(file.file, buffer)
        result["message"] = "이미지가 성공적으로 업로드되었습니다."
        # return JSONResponse(content=result)
        return result

    except Exception as e:
        return {"error": str(e)}


@app.post("/imageupload/")
async def store_file(file: UploadFile = File(...)):
    result = await save_file(file)
    return JSONResponse(content=result)


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

######################################################################
######################################################################


def sync_save_file(file:UploadFile):
    try:
        os.makedirs("images", exist_ok=True)
        result = dict()
        if file.filename in ['test.png']:
            raise Exception("이미지 파일명이 잘못되었습니다.")
        # 이미지 파일 저장
        with open(os.path.join("images", file.filename), "wb") as buffer:
            result["name"]=file.filename
            result["path"]=buffer.name
            shutil.copyfileobj(file.file, buffer)
        result["message"] = "이미지가 성공적으로 업로드되었습니다."
        # return JSONResponse(content=result)
        return result

    except Exception as e:
        return {"error": str(e)}


@app.post("/ai/test/")
def AI_Test(file: UploadFile, index: int = 1):
    start_time = time.time()
    
    # file save
    file_path = sync_save_file(file)
    
    hyper_params = [(0.5,0.2,0.1),(0.4,0.3,0.5),(0.6,0.37,0.1),(0.3, 0.3, 0.1)]
    a,b,c = hyper_params[index]
    print("idx:",hyper_params[index],"a:",a, "b:",b, "c:",c)
    
    # model run
    a:dict = AI(file.filename, a,b,c)
    
    # a["image_path"] = result
    print(type(a), ':' , a)

    end_time = time.time()
    sec = end_time - start_time
    

    result = {"msg" : f"this is demo API : you submit {file.filename}, Function subexecuted in {sec} seconds.",
              "data" : a}
    
    return JSONResponse(content=result)


if __name__ == "__main__":
    # python main.py --host 127.0.0.1 --port 8000
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=False,)
