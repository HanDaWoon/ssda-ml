import cv2
import subprocess
import tempfile
import numpy as np
from glob import glob
import os
from tqdm.auto import tqdm
from multiprocessing import Pool

def make_svg(st):
    image_dir = "/home/software/CHJ/FastAPI/app/dmfont/output/CHJ-200000/CHJ"
    images = glob(os.path.join(image_dir, "*.png"))
    for image_path in tqdm(images[st::10]):
    # Numpy 배열을 임시 파일로 저장
        char_name = image_path.split("/")[-1][:8]
        subprocess.run(["potracer",image_path, "-o", f"/home/software/CHJ/FastAPI/app/dmfont/output/SVGS/CHJ/{char_name}.svg"])
def png2svg():
    if not os.path.exists("/home/software/CHJ/FastAPI/app/dmfont/output/SVGS/CHJ"):
        os.makedirs("/home/software/CHJ/FastAPI/app/dmfont/output/SVGS/CHJ")
    Step = 10
    pool = Pool(processes=10)
    pool.map(make_svg, range(10))
    pool.close()
    pool.join()
# MultiProcessing (실험적으로 step=160으로 했을 때 4분 30초 정도 소요됨.)
