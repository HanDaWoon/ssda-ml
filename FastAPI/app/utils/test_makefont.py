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
    # ANS : 뭔가 concate하는 걸로보아 content_type을 이용해서 연산을 하는것 같은데, 잘 모르겠음.
    trn_dset, loader = get_dset_loader(
        hdf5_data, meta['train']['fonts'], meta['train']['chars'], 
        transform, True, cfg,
        content_font=content_font
    )
    
    # TODO : val_loader 역할?
    val_loaders = setup_cv_dset_loader(
        hdf5_data, meta, transform, n_comp_types, content_font, cfg
    )
    
    g_kwargs = cfg.get('g_args', {})    
    gen = MACore(1, cfg['C'], 1, **g_kwargs, n_comps=n_comps, n_comp_types=n_comp_types, language=cfg['language'])
    gen.cuda()
    
    torch.cuda.empty_cache()
    ckpt = torch.load(cfg['resume'])
    logger.info("Use EMA generator as default")
    gen.load_state_dict(ckpt['generator_ema'])
    
    step = ckpt['epoch']
    loss = ckpt['loss']
    logger.info("Resumed checkpoint from {} (Step {}, Loss {:7.3f})".format(cfg['resume'], step, loss))
    
    writer = utils.DiskWriter(os.path.join(cfg['save_dir'], cfg['name'])) # ./output에 sample image를 저장함.
    
    evaluator = Evaluator(
        hdf5_data, trn_dset.avails, logger, writer, cfg['batch_size'],
        content_font=content_font, transform=transform, language=cfg['language'],
        val_loaders=val_loaders, meta=meta
    )
    