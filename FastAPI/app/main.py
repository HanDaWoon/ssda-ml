import os
import re
from io import BytesIO
from zipfile import ZipFile
from typing import Union
import shutil

from PIL import Image
import base64
import unicodedata

from fastapi import FastAPI, Response, status
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse, HTMLResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from utils import make_font, from_image_to_bytes, png2svg, preprocessing

from glob import glob

app = FastAPI()

image_dir = "./DB"


@app.get("/")
async def root():
    return {"message": "Hello, World!"}

# TODO: 나중에는 이 name이 uuid 같은 hash 값으로 변경되면 됨.


class ImageData(BaseModel):
    imagebase64: str

@app.post("/font_generation/images/{user_name}/{font_name}")
async def font_generation(user_name: str, font_name : str, image_data: ImageData):
    image_bytes = base64.b64decode(image_data.imagebase64)
    image = Image.open(BytesIO(image_bytes))
    image_width, image_height = image.size
    subimage_width = image_width // 7
    subimage_height = image_height // 4

    kor_list = ["가", "긧", "깩", "낐", "냒", "댕", "댻", "땾", "떤", "춾", "렍", "멐", "멶",
                "벹", "볟", "뽈", "셮", "솱", "쇎", "쏗", "욃", "죬", "쭕", "퀧", "튐", "퓹", "흢", "챷"]
    os.makedirs(
        f"./DB/{user_name}/{font_name}/original_splitted", exist_ok=True)
    os.makedirs(
        f"./DB/{user_name}/{font_name}/original_splitted_name", exist_ok=True)
    os.makedirs(
        f"./DB/{user_name}/{font_name}/png", exist_ok=True)
    os.makedirs(
        f"./DB/{user_name}/{font_name}/pnm", exist_ok=True)
    os.makedirs(
        f"./DB/{user_name}/{font_name}/svg", exist_ok=True)
    for idx, kor in zip(range(28), kor_list):
        row = idx // 7
        col = idx % 7
        left = col * subimage_width
        top = row * subimage_height
        right = left + subimage_width
        bottom = top + subimage_height

        subimage = image.crop((left, top, right, bottom))
        kor = unicodedata.normalize('NFC', kor)  # ~~~/가
        subimage.save(
            f"./DB/{user_name}/{font_name}/original_splitted/{user_name}_{ord(kor):04X}.png")
        subimage.save(
            f"./DB/{user_name}/{font_name}/original_splitted_name/{user_name}_{kor}.png")
    preprocessing.make_splitted_images(user_name, font_name)  
    # make_splitted_images 끝났음을 알리는 백엔드 서버로의 post 혹은 get request 문 추가.
    make_font(user_name, font_name)
    # make_font 끝났음을 알리는 백엔드 서버로의 post 혹은 get request 문 추가.
    img_list = {}
    png2svg(user_name, font_name)
    shutil.copy(f'./DB/0020.svg', f'./DB/{user_name}/{font_name}/svg/{font_name}_0020.svg')
    # png2svg 끝났음을 알리는 백엔드 서버로의 post 혹은 get request 문 추가.
    ret_list = []
    for png_path in glob(os.path.join(f"./DB/{user_name}/{font_name}/svg", "*")):
        with open(png_path, "r") as f:
            svg_content = f.read()
            #
            pattern = r'<svg.*?</svg>'
            match = re.search(pattern, svg_content, re.DOTALL)
            if match:
                svg_match = match.group()
                ret_list.append(svg_match)

    return {"message": "Font Generate Success!"}
 


@app.get("/font_generation/png2svg/{user_name}")
async def svg_translation(user_name: str):
    print(user_name)
    png2svg(user_name)
    return {"message": "Success"}

@app.post("/sentence_request/{user_name}/{font_name}")
async def svg_translation(user_name: str, font_name:str, sentence: str):
    ret = []
    for character in sentence:
        with open(f"./DB/{user_name}/{font_name}/svg/{font_name}_{ord(character):04X}.svg", 'r') as f:
            svg_string = f.read()
        ret.append(svg_string)
    ret = "\n".join(ret)
    print(ret)
    return ret

@app.get("/font_user_exist/{user_name}/{font_name}")
async def svg_translation(user_name: str, font_name:str) -> bool:
    if os.path.exists(f'./DB/{user_name}/{font_name}'):
        return True
    return False
