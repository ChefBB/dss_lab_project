"""
Support module

Contains common functions for supporting other scripts.
"""
import re
import os
import json

# get dataset dir
dataset_dir = os.path.abspath(os.path.join(
    os.getcwd(), os.pardir, 'dataset'
))

def read_json(*path: str) -> list:
    """
    Reads a JSON file from the dataset directory.

    Parameters
    ----------
    *path : str
        Path components relative to dataset_dir.

    Returns
    -------
    list
        Content of the JSON file.
    """
    file_name = os.path.join(dataset_dir, *path)

    with open(file_name) as f:
        return json.load(f)


def save_data(data: list | dict, *path: str) -> None:
    """
    Saves data to a JSON file inside the dataset directory.
    In case data size exceeds 90MB, it is split into different files.

    Parameters
    ----------
    data : list | dict
        Data to be serialized and written to disk.

    *path : str
        Path components relative to dataset_dir.
    """
    MAX_SIZE = 90 * 1024 * 1024  # 90 MB
    file_name = os.path.join(dataset_dir, *path)

    serialized = json.dumps(data)
    size = len(serialized.encode('utf-8'))

    # Case 1: fits in a single file
    if size <= MAX_SIZE:
        with open(file_name, 'w') as f:
            json.dump(data, f)
        return

    # Case 2: needs splitting
    base, ext = os.path.splitext(file_name)
    chunk = []
    chunk_size = 0
    part = 1

    for item in data:
        item_json = json.dumps(item)
        item_size = len(item_json.encode('utf-8'))

        if chunk_size + item_size > MAX_SIZE and chunk:
            with open(f'{base}_{part}{ext}', 'w') as f:
                json.dump(chunk, f)
            part += 1
            chunk = []
            chunk_size = 0

        chunk.append(item)
        chunk_size += item_size

    # write final chunk
    if chunk:
        with open(f'{base}_{part}{ext}', 'w') as f:
            json.dump(chunk, f)
            
            
def build_albums(track: dict) -> dict:
    """
    Starting from a track dictionary, build an album dictionary with its info.
    
    Parameters
    ----------
    track: dict
        A dictionary representing the track.
        
    Returns
    -------
    dict
        A dictionary representing the album.
    """
    album = dict()
    
    # album_name
    album['album_name'] = track['album_name'].lower() if track['album_name'] else None
    
    # album_release_date
    album['album_release_date'] = track['album_release_date']
    
    # album_type
    album['album_type'] = track['album_type']
    
    return album


def clean_artist(name: str) -> str:
    """
    Cleans the artist's name.
    
    Parameters
    ----------
    name:str
        The artist's name
    
    Returns
    -------
    str
        The artist's clean name
    """
    return re.sub(r"\s*\(.*?\)$", "", name).strip().lower()