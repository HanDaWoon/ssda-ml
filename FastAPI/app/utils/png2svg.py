import cv2
import subprocess
import tempfile
import numpy as np
from glob import glob
import os
from tqdm.auto import tqdm
from multiprocessing import Pool
from pathlib import Path

def make_svg(st_step_name_tuple):
    st, step, name, font_name = st_step_name_tuple
    image_dir = Path(f"./DB/{name}/{font_name}/png")
    print(image_dir, "png2svg.make_svg.image_dir")
    images = glob(os.path.join(image_dir, "*.png"))
    images = [image_path.rsplit("/", 2) for image_path in images]
    
    for image_path, png, char_name in tqdm(images[st::step]):
        
    # Numpy 배열을 임시 파일로 저장
        char_name = char_name[:len(name) + 5]
        png_path = os.path.join(image_path, "png", f"{char_name}.png")
        pnm_path = os.path.join(image_path, "pnm", f"{char_name}.pnm")
        svg_path = os.path.join(image_path, "svg", f"{char_name}.svg")
        print(png_path)
        print(pnm_path)
        print(svg_path)
        print(char_name)
        subprocess.run(["convert", png_path, pnm_path])
        subprocess.run(["potrace",pnm_path, "-s", "-o", svg_path])
def png2svg(name, font_name):
    os.makedirs(Path(f"./DB/{name}/{font_name}/png/"), exist_ok=True)
    os.makedirs(Path(f"./DB/{name}/{font_name}/pnm/"), exist_ok=True)
    os.makedirs(Path(f"./DB/{name}/{font_name}/svg/"), exist_ok=True)
    Step = 3
    pool = Pool(processes=Step)
    print(pool, "이거 풀임")
    pool.map(make_svg, zip(range(Step), [Step] * Step , [name] * Step, [font_name] * Step))
    pool.close()
    pool.join()
    return {"message" : "Sucess"}
# MultiProcessing (실험적으로 step=160으로 했을 때 4분 30초 정도 소요됨.)
