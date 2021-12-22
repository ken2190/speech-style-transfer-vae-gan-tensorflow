"""
Philip Anastassiou (pja2114)
COMS 6998: Fundamentals of Speech Recognition
Professor Homayoon Beigi
Columbia University
Due: December 19th, 2021

Citations for original authors of this file:

@misc{sammutbonnici2021timbre,
      title={Timbre Transfer with Variational Auto Encoding and Cycle-Consistent Adversarial Networks},
      author={Russell Sammut Bonnici and Charalampos Saitis and Martin Benning},
      year={2021},
      eprint={2109.02096},
      archivePrefix={arXiv},
      primaryClass={cs.SD}
}

@inproceedings{AlBadawy2020,
  author={Ehab A. AlBadawy and Siwei Lyu},
  title={{Voice Conversion Using Speech-to-Speech Neuro-Style Transfer}},
  year=2020,
  booktitle={Proc. Interspeech 2020},
  pages={4726--4730},
  doi={10.21437/Interspeech.2020-3056},
  url={http://dx.doi.org/10.21437/Interspeech.2020-3056}
}
"""

import argparse
import pickle
from tqdm import tqdm
from params import num_samples
from utils import ls, preprocess_wav, melspectrogram
from sklearn.model_selection import train_test_split
from collections import defaultdict

parser = argparse.ArgumentParser()
parser.add_argument("--dataset", type=str, default="data", help="path to dataset") # pja2114: Added default relative path
parser.add_argument("--test_size", type=float, default=0.1, help="path to dataset")
parser.add_argument("--eval_size", type=float, default=0.1, help="path to dataset")
parser.add_argument("--n_spkrs", type=int, default=2, help="number of speakers for conversion")

opt = parser.parse_args()
print(opt)

not_train_size = opt.test_size + opt.eval_size

# Stores preprocessed spectrograms
train_feats = defaultdict(list)
eval_feats = defaultdict(list)
test_feats = defaultdict(list)

# Stores corresponding wav filenames
train_refs = {}
eval_refs = {}
test_refs = {}


def get_spect(wav):
    sample = preprocess_wav('%s/spkr_%s/%s'%(opt.dataset, spkr+1, wav))
    return melspectrogram(sample)


for spkr in range(opt.n_spkrs):
    wavs = ls('%s/spkr_%s | grep .wav'%(opt.dataset, spkr+1))

    # Prepares reference filenames from train/eval/test split
    train_refs[spkr], temp_refs = train_test_split(wavs, test_size=(not_train_size))
    eval_refs[spkr], test_refs[spkr] = train_test_split(temp_refs, test_size=(opt.test_size/not_train_size))

    for wav in tqdm(train_refs[spkr], total=len(train_refs[spkr]), desc="spkr_%d_train"%(spkr+1)):
        spect = get_spect(wav)
        if spect.shape[1] >= num_samples: train_feats[spkr].append(spect)

    for wav in tqdm(eval_refs[spkr], total=len(eval_refs[spkr]), desc="spkr_%d_eval"%(spkr+1)):
        spect = get_spect(wav)
        if spect.shape[1] >= num_samples: eval_feats[spkr].append(spect)

    for wav in tqdm(test_refs[spkr], total=len(test_refs[spkr]), desc="spkr_%d_test"%(spkr+1)):
        spect = get_spect(wav)
        if spect.shape[1] >= num_samples: test_feats[spkr].append(spect)


# Saving preprocessed spectrograms
pickle.dump(train_feats,open('%s/data_train.pickle'%(opt.dataset),'wb'))
pickle.dump(eval_feats,open('%s/data_eval.pickle'%(opt.dataset),'wb'))
pickle.dump(test_feats,open('%s/data_test.pickle'%(opt.dataset),'wb'))

# Saving corresponding filenames
pickle.dump(train_refs,open('%s/refs_train.pickle'%(opt.dataset),'wb'))
pickle.dump(eval_refs,open('%s/refs_eval.pickle'%(opt.dataset),'wb'))
pickle.dump(test_refs,open('%s/refs_test.pickle'%(opt.dataset),'wb'))