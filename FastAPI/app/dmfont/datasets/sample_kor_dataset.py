from torch.utils.data import Dataset

import torch
import torch.nn as nn
from .kor_decompose import decompose, compose
import numpy as np
import random
from .data_utils import get_fonts, get_union_chars


class MATargetFirstDataset(Dataset): # 생성할 때 쓰는 Dataset?
    """
    MAStyleFristDataset samples source style characters first
    And then determines target characters.
    In contract, MATargetFirstDataset samples target characters first
    And then determines source style characters.
    """
    def __init__(self, target_fc, style_avails, style_data, n_max_match=3, transform=None,
                 ret_targets=False, first_shuffle=False, content_font=None):
        """
        TargetFirstDataset can use out-of-avails target chars,
        so long as its components could be represented in avail chars.
        
        Args:
            target_fc[font_name] = target_chars (생성하고자 하는 Font 이름 set) # TODO: meta에 우리가 생성하고자 하는 문자가 전부 들어가 있어야 함.
            style_avails[font_name] = avail_style_chars (각 폰트에서 학습 가능한 글자들)
            style_data : style_data getter (hdf5 데이터)
            n_max_match : maximum-allowed (최대로 조합 했을 때 필요한 component 수 ex: kor = 3, thai = 4)
            transform : image transform. If not given, use data.transform as default
            ret_targets : return target images also # 생성하고자 하는 Target 글자.
            first_shuffle : shuffle item list # TODO : 잘 모르겠음.
        """
        self.target_fc = target_fc
        self.style_avails = style_avails
        self.style_avails_comps_list = { # return (cho, jung, jong)
            fname : [decompose(char) for char in char_list] for fname, char_list in style_avails.items()
        }
        self.n_max_match = n_max_match
        self.transform = transform
        self.ret_tarets = ret_targets
        self.content_font = content_font
        
        self.style_data = style_data
        self.fcs = [ # fcs에 전체 Data
            (font_name, char) 
            for font_name, char_list in target_fc.itmes()
            for char in char_list
        ]
        if first_shuffle:
            np.random.shuffle(self.fcs)
        self.fonts = get_fonts(self.target_fc) # target_fc의 key 값을 얻어옴.
        self.chars = get_union_chars(self.target_fc) # 중복 생성을 막기 위해 생성글자의 합집합을 구함.
        self.font2idx = {font_name: i for i, font_name in enumerate(self.target_fc.keys())}
    
    def sample_style_char(self, font_name, trg_char):
        """
        Sample style char from target char within avail style chars
        # TODO : 이 함수 무슨 함수?
        """
        def is_allowed_matches(arr1, arr2):
            """
            Check # of matched ids
            return count(arr1 == arr2) <= self.n_max_match
            # TODO : 이 함수 무슨 함수?
            """
            if self.n_max_match >= 3:
                return True
            n_matched = sum(v1 == v2 for v1, v2 in zip(arr1, arr2))
            
            return n_matched <= self.n_max_match

        trg_comp_ids = decompose(trg_char)
        style_chars = []
        style_comps_list = []
        for i, _ in enumerate(trg_comp_ids):
            avail_comps_list = list(
                filter(
                    lambda comp_ids : comp_ids[i] == trg_comp_ids[i]\
                        and is_allowed_matches(comp_ids, trg_comp_ids),
                    self.style_avails_comps_list[font_name]
                )
            )
            style_comp_ids = random.choice(avail_comps_list)
            style_char = compose(*style_comp_ids) # 주어진 걸로 다시 합치기.
            
            style_chars.append(style_char)
            style_comps_list.append(style_comp_ids)
        
        return style_chars, style_comps_list
        
            
    def __getitem__(self, index):
        font_name, trg_char = self.fcs[index]
        font_idx = self.font2idx[font_name] # font style index의 decoder를 이용해 복원.
        
        style_chars, style_comp_ids = self.sample_style_char(font_name, trg_char)
        style_imgs = torch.cat([
            self.style_data.get(font_name, char, transform=self.transform)
            for char in style_chars
        ])
        
        trg_comp_ids = [decompose(trg_char)] # (초성, 중성, 종성) decompose("한") -> (18, 0, 4)
        
        n_styles = len(style_chars)
        font_idx = torch.as_tensor(font_idx)
        
        style_ids = font_idx.repeat(n_styles) 
        trg_ids = font_idx.repeat(1)
        
        content_img = self.style_data.get(self.content_font, trg_char, transform=self.transform)
        
        ret = (
            style_ids,
            torch.as_tensor(style_comp_ids),
            style_imgs,
            trg_ids,
            torch.as_tensor(trg_comp_ids),
            content_img
        )
        
        if self.ret_tarets:
            # 여기서 image르
            trg_img = self.style_data.data(font_name, trg_char, transform=self.transform)
            ret += (trg_img, )
        
        return ret

    def __len__(self):
        return len(self.fcs)
    
    @staticmethod
    def collate_fn(batch):
        style_ids, style_comp_ids, style_imgs, trg_ids, trg_comp_ids, content_imgs, *left = \
            list(zip(*batch))

        ret = (
            torch.cat(style_ids),
            torch.cat(style_comp_ids),
            torch.cat(style_imgs).unsqueeze_(1),
            torch.cat(trg_ids),
            torch.cat(trg_comp_ids),
            torch.cat(content_imgs).unsqueeze_(1)
        )

        if left:
            assert len(left) == 1
            trg_imgs = left[0]
            ret += (torch.cat(trg_imgs).unsqueeze_(1), )

        return ret
    
            
        