import os
import re
from io import BytesIO
from zipfile import ZipFile
from typing import Union

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

    kor_list = ["가", "긧", "깩", "낐", "냒", "댕", "댻", "땾", "떤", "랯", "렍", "멐", "멶",
                "벹", "볟", "뽈", "셮", "솱", "쇎", "쏗", "욃", "죬", "쭕", "춾", "퀧", "튐", "퓹", "흢"]
    os.makedirs(
        f"./DB//{user_name}/{font_name}/original_splitted", exist_ok=True)
    os.makedirs(
        f"./DB//{user_name}/{font_name}/png", exist_ok=True)
    os.makedirs(
        f"./DB//{user_name}/{font_name}/pnm", exist_ok=True)
    os.makedirs(
        f"./DB//{user_name}/{font_name}/svg", exist_ok=True)
    for idx, kor in zip(range(28), kor_list):
        row = idx // 7
        col = idx % 7
        print(row, col, "-row,col")
        left = col * subimage_width
        top = row * subimage_height
        right = left + subimage_width
        bottom = top + subimage_height

        subimage = image.crop((left, top, right, bottom))
        kor = unicodedata.normalize('NFC', kor)  # ~~~/가
        subimage.save(
            f"./DB/{user_name}/{font_name}/original_splitted/{user_name}_{ord(kor):04X}.png")
    preprocessing.make_splitted_images(user_name, font_name)  
    # make_splitted_images 끝났음을 알리는 백엔드 서버로의 post 혹은 get request 문 추가.
    make_font(user_name, font_name)
    # make_font 끝났음을 알리는 백엔드 서버로의 post 혹은 get request 문 추가.
    print(os.path.abspath(image_dir), "image_dir")
    image_paths = glob(os.path.join(image_dir, user_name, "*.png"))
    print(image_paths[:5])
    img_list = {}
    png2svg(user_name, font_name)
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
                print(svg_match)
                ret_list.append(svg_match)

    print(ret_list)
    ret = "\n".join(ret_list)
    with open("./output.svg", "w") as f:
        f.write(ret)
    return {"message": ret}



@app.get("/font_generation/png2svg/{name}")
async def svg_translation(name: str):
    print(name)
    png2svg(name)
    return {"message": "Success"}




@app.post("/font_generation_with_total_image/{name}/{font_name}")
async def svg_translation(font_name: str, name: str, image_data: ImageData):
    image_bytes = base64.b64decode(image_data.imagebase64)
    image = Image.open(BytesIO(image_bytes))
    image_width, image_height = image.size
    subimage_width = image_width // 7
    subimage_height = image_height // 4

    kor_list = ["가", "긧", "깩", "낐", "냒", "댕", "댻", "땾", "떤", "랯", "렍", "멐", "멶",
                "벹", "볟", "뽈", "셮", "솱", "쇎", "쏗", "욃", "죬", "쭕", "춾", "퀧", "튐", "퓹", "흢"]
    os.makedirs(
        f"./dmfont/custom_generate_image/{name}/{font_name}/png", exist_ok=True)
    os.makedirs(
        f"./dmfont/custom_generate_image/{name}/{font_name}/pnm", exist_ok=True)
    os.makedirs(
        f"./dmfont/custom_generate_image/{name}/{font_name}/svg", exist_ok=True)
    for idx, kor in zip(range(28), kor_list):
        row = idx // 7
        col = idx % 4
        left = col * subimage_width
        top = row * subimage_height
        right = left + subimage_width
        bottom = top + subimage_height

        subimage = image.crop((left, top, right, bottom))
        kor = unicodedata.normalize('NFC', kor)  # ~~~/가
        subimage.save(
            f"./dmfont/custom_generate_image/{name}/{font_name}/sp/{name}_{ord(kor):04X}.png")

    # make_font(name, font_name)
    png2svg(name, font_name)
    ret_list = []
    for png_path in glob(os.path.join(f"./DB/{name}/{font_name}/svg", "*")):
        with open(png_path, "r") as f:
            svg_content = f.read()
            #
            pattern = r'<svg.*?</svg>'
            match = re.search(pattern, svg_content, re.DOTALL)
            if match:
                svg_match = match.group()
                print(svg_match)
                ret_list.append(svg_match)

    print(ret_list)
    ret = "\n".join(ret_list)
    with open("./output.svg", "w") as f:
        f.write(ret)
    return {"message": ret}

@app.post("/sentence_request/{name}/{font_name}")
async def svg_translation(name: str, font_name:str, sentence: str):
    ret = []
    for character in sentence:
        with open(f"./DB/{name}/{font_name}/svg/{font_name}_{ord(character):04X}.svg", 'r') as f:
            svg_string = f.read()
        ret.append(svg_string)
    ret = "\n".join(ret)
    print(ret)
    return jsonable_encoder({"sentence" : ret})
