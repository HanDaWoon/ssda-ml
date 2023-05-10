from io import BytesIO
from zipfile import ZipFile
from typing import Union

from PIL import Image


from fastapi import FastAPI, Response, status
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse, HTMLResponse
from utils import *

from glob import glob
import os

app = FastAPI()

image_dir = "./dmfont/output/images"


@app.get("/")
async def root():
    return {"message": "Hello, World!"}

# TODO: 나중에는 이 name이 uuid 같은 hash 값으로 변경되면 됨.
@app.get("/font_generation/images/{name}") 
async def font_generation(name:str):
    make_font(name)
    print(os.path.abspath(image_dir))
    image_paths = glob(os.path.join(image_dir , name,"*.png"))
    print(image_paths[:5])
    img_list = {}
    
    for image_path in image_paths:
        char_name = str(image_path.split('_')[-1][:4])
        img_list[char_name] = from_image_to_bytes(Image.open(image_path))
    return JSONResponse(img_list)
  

@app.get("/font_generation/png2svg/{name}")
async def svg_translation(name: str):
    print(name)
    png2svg(name)
    return {"message" : "Success"}  


    
    

