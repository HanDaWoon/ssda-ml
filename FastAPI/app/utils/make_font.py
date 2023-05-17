import sys
sys.path.append("./dmfont")
print(sys.path)
import numpy as np
import requests
import json
import torch
from models import MACore
from sconf import Config
from pathlib import Path
import numpy as np
import random
from evaluator import Evaluator
from torchvision import transforms

from logger import Logger
from train import (
        setup_language_dependent, setup_data, setup_cv_dset_loader,
        get_dset_loader
    )
from dmfont import utils
import os


def make_font(name):
    # cfg = Config("./dmfont/cfgs/kor_custom.yaml") # Full Character Generation
    cfg = Config("./dmfont/cfgs/kor_custom_test.yaml")
    logger = Logger.get()
    cfg['data_dir'] = Path(os.path.join(cfg['data_dir'], cfg['name']))
    cfg['name'] = name
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
    
    hdf5_data, meta = setup_data(cfg, transform)
    
    # setup dataset
    trn_dset, loader = get_dset_loader(
        hdf5_data, meta['train']['fonts'], meta['train']['chars'], transform, True, cfg,
        content_font=content_font
    )
    # TODO : val_loader 역할?
    val_loaders = setup_cv_dset_loader(
        hdf5_data, meta, transform, n_comp_types, content_font, cfg
    )
    
    # setup dataset
    g_kwargs = cfg.get('g_args', {})    
    gen = MACore(1, cfg['C'], 1, **g_kwargs, n_comps=n_comps, n_comp_types=n_comp_types, language=cfg['language'])
    gen.to(device)
    
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
    meta = json.load(open(Path(cfg['data_meta'])))
    target_chars = meta['target_chars']
    style_chars = meta['style_chars']
    fonts = meta['train']['fonts']
    logger.info("Start generation & saving kor-unrefined ...")
    save_dir = Path(cfg['save_dir'])
    evaluator.handwritten_validation_2stage(
      gen,step, fonts, style_chars, target_chars, comparable=True, save_dir=save_dir
    )
    
if __name__ == "__main__":
    make_font("CHJ")