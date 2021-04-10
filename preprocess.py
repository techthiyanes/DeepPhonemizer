from multiprocessing.pool import Pool
from pathlib import Path
from random import Random
from typing import Iterable, Tuple

import tqdm
import pickle
import argparse

from dp.text import Preprocessor
from dp.utils import read_config, pickle_binary


def get_data(file: str):
    with open(file, 'rb') as f:
        df = pickle.load(f)
    tuples = df[['title', 'pronunciation']]
    tuples = [tuple(x) for x in tuples.to_numpy()]
    data_set = {w for w, _ in tuples}
    train_data = []
    max_len = 50
    all_phons = set()
    for word, phon in tuples:
        all_phons.update(set(phon))
        if 0 < len(phon) < max_len and ' ' not in word and 0 < len(word) < max_len:
            train_data.append(('de', word, phon))
            if word.lower() not in data_set:
                word_ = word.lower()
                train_data.append(('de', word_, phon))
            if word.title() not in data_set:
                word_ = word.title()
                train_data.append(('de', word_, phon))

    return train_data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Preprocessing for DeepForcedAligner.')
    parser.add_argument('--config', '-c', default='config.yaml', help='Points to the config file.')
    parser.add_argument('--checkpoint', '-cp', default=None, help='Points to the a model file to restore.')
    parser.add_argument('--path', '-p', help='Points to the a file with data.')

    args = parser.parse_args()

    config = read_config(args.config)
    data_dir = Path(config['paths']['data_dir'])
    token_dir = data_dir / 'tokens'
    data_dir.mkdir(parents=True, exist_ok=True)
    token_dir.mkdir(parents=True, exist_ok=True)

    raw_data = get_data(args.path   )

    random = Random(42)
    random.shuffle(raw_data)

    train_data = raw_data[config['preprocessing']['n_val']]
    val_data = raw_data[:config['preprocessing']['n_val']]

    preprocessor = Preprocessor.from_config(config)

    train_dataset = []
    for i, (lang, text, phonemes) in enumerate(tqdm.tqdm(train_data, total=len(raw_data))):
        tokens = preprocessor((lang, text, phonemes))
        item_id = f'{i}_{lang}_train'
        train_dataset.append((item_id, len(phonemes)))
        pickle_binary(tokens, token_dir / f'{item_id}.pkl')

    val_dataset = []
    for i, (lang, text, phonemes) in enumerate(tqdm.tqdm(val_data, total=len(raw_data))):
        tokens = preprocessor((lang, text, phonemes))
        item_id = f'{i}_{lang}_val'
        val_dataset.append((item_id, len(phonemes)))
        pickle_binary(tokens, token_dir / f'{item_id}.pkl')

    pickle_binary(train_dataset, data_dir / 'train_dataset.pkl')
    pickle_binary(val_dataset, data_dir / 'val_dataset.pkl')
