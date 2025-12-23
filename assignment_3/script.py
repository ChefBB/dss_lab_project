"""
Creates categories based off of lyrics.
"""

import json
import os

parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
dataset_dir = f'{parent_dir}/dataset'

with open(f'{dataset_dir}/correct_ids/tracks.json') as f:
    tracks = json.load(f)
    

texts = list()

for track in tracks:
    texts.append(track['lyrics'])