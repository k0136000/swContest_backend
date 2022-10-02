"""
서버 구동 방법
uvicorn main:app --reload
--reload: 서버가 자동을 리로딩

포스트맨 같은거
http://127.0.0.1:8000/docs

api 문서 확인
http://127.0.0.1:8000/redoc
"""
from typing import Union

from fastapi import FastAPI, UploadFile,File
from fastapi.responses import FileResponse
from pydantic import BaseModel
import cv2
import run_cv
import uuid 
import os
import sys
import io
from starlette.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI ()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/test")
def test():
    print("테스트 성공")
    return "success!"
#이미지 불러 오기
@app.get("/convert/readimg")
def get_note(path:str):
    img = FileResponse(path)
    # os.remove(path)
    return img

@app.post("/convert/upload/")

async def conver_note(file: UploadFile):
    UPLOAD_DIR  = "./photo"

    content = await file.read()
    
    #uuid로 유니크한 파일명으로 변경
    filename = f"{str(uuid.uuid4())}.jpg"

    with open(os.path.join(UPLOAD_DIR, filename), "wb") as fp:
        #서버 로컬 스토리지에 이미지 저장.
        fp.write(content)

    img_path = f"./photo/{filename}"
    img=run_cv.run(img_path)
    res,im_png = cv2.imencode(".png",img)
    # convert_img_path = f"/home/ubuntu/swContest_backend/photo/{filename}"
    # cv2.imwrite(convert_img_path,img)
    # cv2.imwrite(img_path,img)
    return StreamingResponse(io.BytesIO(im_png.tobytes()),media_type="image/png")
    # return {"filename":filename, "path":convert_img_path}
    # return {"filename":filename, "path":img_path}
