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
    st, step, name = st_step_name_tuple
    image_dir = Path(f"./dmfont/output/images/{name}")
    images = glob(os.path.join(image_dir, "*.png"))
    for image_path in tqdm(images[st::step]):
    # Numpy 배열을 임시 파일로 저장
        char_name = image_path.split("/")[-1][:8]
        subprocess.run(["potracer",image_path, "-o", f"./dmfont/output/svgs/{name}/{char_name}.svg"])
def png2svg(name):
    if not os.path.exists(Path(f"./dmfont/output/svgs/{name}")):
        os.makedirs(Path(f"./dmfont/output/svgs/{name}"))
    Step = 40
    pool = Pool(processes=Step)
    pool.map(make_svg, zip(range(Step), [Step] * Step , [name] * Step))
    pool.close()
    pool.join()
    return {"message" : "Sucess"}
# MultiProcessing (실험적으로 step=160으로 했을 때 4분 30초 정도 소요됨.)
