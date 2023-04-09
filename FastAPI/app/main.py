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

image_dir = "/home/software/CHJ/FastAPI/app/dmfont/output/CHJ-200000/CHJ"


@app.get("/")
async def root():
    return {"message": "Hello, World!"}


@app.get("/font_generation/images")
async def font_generation():
    make_font()
    image_paths = glob(os.path.join(image_dir,"*.png"))
    print(image_paths[:5])
    img_list = {}
    
    for image_path in image_paths:
        char_name = str(image_path.split('_')[-1][:4])
        img_list[char_name] = from_image_to_bytes(Image.open(image_path))
    return JSONResponse(img_list)

@app.get("/font_generation/png2svg")
async def svg_translation():
    png2svg()    

@app.get("/font_generation/png2svgs")
async def svg_translation():
    png2svgs()  


    
@app.get("/svg_images")
async def get_svg_images():
    svg_images = {
        "image1": "<svg viewBox='0 0 100 100'><circle cx='50' cy='50' r='40' fill='red'/></svg>",
        "image2": "<svg viewBox='0 0 100 100'><rect x='10' y='10' width='80' height='80' fill='blue'/></svg>",
        "image3": "<svg viewBox='0 0 100 100'><ellipse cx='50' cy='50' rx='40' ry='30' fill='green'/></svg>"
    }
    return JSONResponse(svg_images)
    

