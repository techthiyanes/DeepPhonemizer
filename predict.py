import pickle
import argparse
import random
from collections import Counter
from typing import List, Tuple

import tqdm
import torch
from dp.dataset import new_dataloader
from dp.model import TransformerModel
from dp.text import Tokenizer
from dp.trainer import Trainer
from dp.utils import read_config


if __name__ == '__main__':

    checkpoint_path = 'checkpoints/latest_model.pt'
    checkpoint = torch.load(checkpoint_path, map_location=torch.device('cpu'))
    model = TransformerModel.from_config(checkpoint['config']['model'])
    model.load_state_dict(checkpoint['model'])

    text_tok = checkpoint['text_tokenizer']
    phon_tok = checkpoint['phoneme_tokenizer']

    print(f'Restored model with step {model.get_step()}')

    text = 'raketenwerk'

    tokens = checkpoint['text_tokenizer'](text) + [0] * 10
    pred = model.generate(torch.tensor(tokens).unsqueeze(0))
    pred_decoded = checkpoint['phoneme_tokenizer'].decode(pred, remove_special_tokens=True)
    pred_decoded = ''.join(pred_decoded)
    print(f'{text} | {pred_decoded}')
