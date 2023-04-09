import numpy as np
import requests
import json
import torch
from dmfont.models import MACore
from sconf import Config
from pathlib import Path
import numpy as np
import random
from dmfont.evaluator import Evaluator
from torchvision import transforms

from dmfont.logger import Logger
from dmfont.train import (
        setup_language_dependent, setup_data, setup_cv_dset_loader,
        get_dset_loader
    )
from dmfont import utils


def make_font():
    cfg = Config("./dmfont/cfgs/kor_custom.yaml")
    logger = Logger.get()
    cfg['data_dir'] = Path(cfg['data_dir'])
    np.random.seed(cfg['seed'])
    torch.manual_seed(cfg['seed'])
    random.seed(cfg['seed'])
    
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
    print(torch.cuda.is_available(), "- isavaliable")
    gen.cuda()
    
    torch.cuda.empty_cache()
    ckpt = torch.load(cfg['resume'])
    logger.info("Use EMA generator as default")
    gen.load_state_dict(ckpt['generator_ema'])
    
    step = ckpt['epoch']
    loss = ckpt['loss']
    logger.info("Resumed checkpoint from {} (Step {}, Loss {:7.3f})".format(cfg['resume'], step, loss))
    
    writer = utils.DiskWriter(cfg['img_dir']) # ./output에 sample image를 저장함.
    
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
    save_dir = Path(cfg['img_dir']) / "{}-{}".format(cfg['name'], step)
    evaluator.handwritten_validation_2stage(
      gen,step, fonts, style_chars, target_chars, comparable=True, save_dir=save_dir
    )