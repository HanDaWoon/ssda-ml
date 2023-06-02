from io import BytesIO
from zipfile import ZipFile
from typing import Union

from PIL import Image
import base64


from fastapi import FastAPI, Response, status
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse, HTMLResponse
from pydantic import BaseModel
from utils import make_font, from_image_to_bytes, png2svg

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


class ImageData(BaseModel):
    imagebase64: str

@app.post("/font_generation_with_total_image/{name}")
async def svg_translation(name : str, image_data:ImageData) :
    image_bytes = base64.b64decode(image_data.imagebase64)
    image = Image.open(BytesIO(image_bytes)) 
    image_width, image_height = image.size
    subimage_width = image_width // 7
    subimage_height = image_height // 4

    for row in range(4):
        for col in range(7):
            left = col * subimage_width
            top = row * subimage_height
            right = left + subimage_width
            bottom = top + subimage_height

            subimage = image.crop((left, top, right, bottom))
            subimage.save(f"./dmfont/custom_generate_image/test/subimage_{row}_{col}.png")

    return {"message" : "success"}


    
    

