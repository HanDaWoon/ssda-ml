import os
from os.path import  splitext, basename
from pathlib import Path
from functools import reduce

# from ..dmfont.logger import Logger

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import fire
import json
import h5py as h5
from glob import glob
from pprint import pprint
import unicodedata as uni
from tqdm.auto import tqdm
from fontTools.ttLib import TTFont
input_chars = sorted(["가", "긧", "깩", "낐", "냒", "댕", "댻", "땾", "떤", "랯", "렍", "멐", "멶", "벹", "볟", "뽈", "셮", "솱", "쇎", "쏗", "욃", "죬", "쭕", "춾", "퀧", "튐", "퓹", "흢"],key=lambda x : ord(uni.normalize('NFC', x)))

CODE_RANGE = {
    'kor': [[0x0021, 0x007E], [0x3131, 0x3163], [0xAC00, 0xD7A3]],
    'thai': [[0x0E01, 0x0E3A], [0x0E3F, 0x0E5B]]
}

def get_code_points(language):
    codes = set()
    code_range = CODE_RANGE[language]
    for rangemin, rangemax in code_range:
        for codepoint in range(rangemin, rangemax+1):
            codes.add(chr(codepoint))

    return codes


def dump_to_hdf5(dump_path, font_name, images, chars, compression=None):
    with h5.File(dump_path, 'w') as f:
        dset = f.create_group('dataset')
        dset.attrs['font_name'] = font_name
        N = len(images)
        dset.create_dataset('images', (N, 128, 128), np.uint8, compression=compression,
                            data=np.stack(images))
        data = np.array(chars)
        dset.create_dataset('chars', data.shape, np.int32, compression=compression,
                            data=np.array(chars))
        
        
class FontProcessor(object):
    def __init__(self, language, root_dir = '../DB', resize_method="bilinear", font_size_factor=2, sample_size=128):
        if language != "kor":
            assert False, 'Please input Korean language'
        
        # self.logger = Logger.get(file_path='preparedata.log', level='error')
        
        self.language = language
        self.targetcodes = get_code_points(self.language)
        if resize_method == 'bilinear':
            self.resize_method = Image.BILINEAR
        else:
            raise ValueError('Invalid resize method: {}'.format(resize_method))
        self.sample_size = sample_size
        self.font_size = self.sample_size * font_size_factor
        self.root_dir = root_dir
        
    def ord(self, char):
        if self.language == 'kor':
            return ord(char)
        else:
            raise ValueError(self.language)
    
    def is_renderable_char(self, font, ch):
        ch = self.fix_char_order_if_thai(ch)
        try:
            size = reduce(lambda x, y: x * y, font.getsize(ch))
        except OSError:
            self.logger.warning('{}, "{}" ({}) cannot be opened'.format(font, ch, self.ord(ch)))
            return False
        if not size:
            self.logger.warning('{}, "{}" ({}) has size {}'.format(
                font, ch, self.ord(ch), font.getsize(ch))
            )
            return False

        return True
    
    def avail_chars(self, targetfontpath, pilfont):
        ttfont = TTFont(targetfontpath)
        existing_chars = {chr(key) for table in ttfont['cmap'].tables for key in table.cmap.keys()}
        rendercheckedchars = {ch for ch in existing_chars if self.is_renderable_char(pilfont, ch)}

        return rendercheckedchars

    def get_charsize(self, char, font):
        char = self.fix_char_order_if_thai(char)
        size_x, size_y = font.getsize(char)
        offset_x, offset_y = font.getoffset(char)

        return size_x-offset_x, size_y-offset_y
    
    def render_center_no_offset(self, char, font, fontmaxsize, size=128, margin=0):
        char = self.fix_char_order_if_thai(char)
        size_x, size_y = font.getsize(char)
        offset_x, offset_y = font.getoffset(char)
        roi_w = size_x-offset_x
        roi_h = size_y-offset_y
        img = Image.open()

        return img
    
    
    def dump_fonts(self, user, font_name, compression=None):        
        dump_path = os.path.join(self.root_dir, user, font_name)
        os.makedirs(dump_path, exist_ok=True)
        # assert dump_path.is_dir(), "Please check dump_dir"
        
        """
            TODO : 이미 폰트가 존재할 때의 exception 과정 필요
            if dump_path.exists():
        """
        char_paths = sorted(glob(os.path.join(self.root, user, font_name, "original_split", '*')))
        # pprint(char_paths)
        # print(len(char_paths)) 
        # print()
        # pprint(input_chars)
        # print(len(input_chars))
        images = []
        chars = []
        for char_path, char in tqdm(zip(char_paths, input_chars)):
            print(char_path)
            img = Image.open(char_path).convert("L")
            img = img.resize((128,128), 2)
            images.append(img)
            chars.append(self.ord(uni.normalize('NFC', char)))
            
        dump_to_hdf5(os.path.join(dump_path, f"{font_name}.hdf5"), font_name, images, chars, compression=compression)
            
        
def main(language, user, font_name):
    processor = FontProcessor(language)
    processor.dump_fonts(user, font_name)


if __name__ == '__main__':
    fire.Fire(main)
      
