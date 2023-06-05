import os
import sys
import json
import torch
import random
import requests
import numpy as np

from sconf import Config
from pathlib import Path
from dmfont.models import MACore
from dmfont.evaluator import Evaluator
from torchvision import transforms

from dmfont.logger import Logger
from dmfont.train import (
        setup_language_dependent, setup_data, setup_cv_dset_loader,
        get_dset_loader
    )
from dmfont import utils

sys.path.append("./dmfont")

def make_font(name, font_name):
    cfg = Config("./dmfont/cfgs/kor_custom_test.yaml")
    logger = Logger.get()
    cfg['name'] = name
    cfg['font_name'] = font_name
    cfg['data_dir'] = Path(os.path.join(cfg['data_dir'], name, font_name))
    
    np.random.seed(cfg['seed'])
    torch.manual_seed(cfg['seed'])
    random.seed(cfg['seed'])
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    content_font, n_comp_types, n_comps = setup_language_dependent(cfg)
    
    # setup transform
    transform = transforms.Compose([
      transforms.ToTensor(),
      transforms.Normalize([0.5], [0.5])
    ])
    
    # Return 
    #   - ./dmfont/DB/user/font_name/hdf5_dataset.hdf5, 
    #   - default style, target font가 있는 meta/~~~.json
    hdf5_data, meta = setup_data(cfg, transform)
    
    # TODO : content_Type = True인 이유 
    trn_dset, loader = get_dset_loader(
        hdf5_data, meta['train']['fonts'], meta['train']['chars'], 
        transform, True, cfg,
        content_font=content_font
    )
    
    