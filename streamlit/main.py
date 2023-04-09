from io import BytesIO
import streamlit as st
import pandas as pd
import numpy as np
import requests
from zipfile import ZipFile
from PIL import Image
import json
import base64


button1 = st.button("button1")

inputs = {
  "name": "Foo",
  "description": "A very nice Item",
  "price": 35.4,
  "tax": 3.2
}

if button1:
    response = requests.get("http://localhost:8000/font_generation", stream=True)
    url = "http://localhost:8000/font_generation/images"
    # 요청
    result = requests.get(url)
    # 딕셔너리 변환
    res = json.loads(result.content)
    # 이미지 Bytes 리스트
    bytes_list = dict(map(lambda x: (x[0], base64.b64decode(x[1])), res.items()))
    # 이미지 Pillow Image 리스트
    images = dict(map(lambda x: (chr(int(x[0], 16)), Image.open(BytesIO(x[1]))), bytes_list.items()))
    st.image(images["가"])

button2 = st.button("button2")

if button2:
    response = requests.get("http://localhost:8000/font_generation/png2svg", stream=True)
    res = json.loads(response.content)
    st.text(res)
    # svg_bytes = res['image1'].encode('utf-8')
    # image = Image.open(BytesIO(svg_bytes))
    # st.image(image, caption="SVG Image")

button3 = st.button("png2svg")
if button3:
  response = requests.get("http://localhost:8000/font_generation/png2svg")
  result = requests.get(response)
  st.text(result)
    