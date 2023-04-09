import os
import subprocess
from glob import glob
from tqdm import tqdm
from threading import Thread, Lock

def png2svgs(image_path):
    char_name = image_path.split("/")[-1][:8]
    subprocess.run(["potracer", image_path, "-o", f"/home/software/CHJ/FastAPI/app/dmfont/output/SVGS/CHJ/{char_name}.svg"])

def png2svg_multithread():
    image_dir = "/home/software/CHJ/FastAPI/app/dmfont/output/CHJ-200000/CHJ"
    images = glob(os.path.join(image_dir, "*.png"))
    lock = Lock()

    def worker():
        while True:
            with lock:
                try:
                    image_path = next(iterator)
                except StopIteration:
                    break
            png2svgs(image_path)

    iterator = iter(images)
    threads = [Thread(target=worker) for _ in range(10)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()




