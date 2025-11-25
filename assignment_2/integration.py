"""
Integration module
------------------

Contains functions to integrate obtained data with
the original dataset.
"""
from difflib import SequenceMatcher


def best_match_tracks(data_og: dict, data_retrieved: dict) -> dict:
    """
    Computes matching score between original and retrieved items.
    
    Parameters
    ----------
    data_og: dict
        Data object from the original dataset.
    data_retrieved: dict
        Data object from the retrieved data.
    
    Returns
    -------
    dict
        Dictionary of objects ordered by their matching score.
    """
    if data_retrieved.get('recording-list'):
        flag = True
    else:
        flag = False
    for item in data_retrieved['recording-list' if flag else 'artist_list']:
        item['matching-score'] = (
            matching_score_artist(data_og, item) if flag
            else matching_score_track(data_og, item)
        )
    
    return data_retrieved


def matching_score_track(track_og: dict, track_retrieved: dict) -> float:
    """
    Computes matching score between original and retrieved tracks.

    Parameters
    ----------
    track_og: dict
        Track object from the original dataset.
    track_retrieved: dict
        Track item from the retrieved data.
    
    Returns
    -------
    float
        Matching score between original and retrieved tracks.
    """
    match = 1.0
    
    # title
    match *= SequenceMatcher(None, track_og['title'].lower(), track_retrieved['title'].lower()).ratio()
    
    # artist
    if track_og.get('primary_artist'):
        idx = len(track_retrieved.get('artist-credit')) + 1
        if ' feat. ' in track_retrieved.get('artist-credit'):
            idx = track_retrieved.get('artist-credit').index(' feat. ')
        primary_artists = track_retrieved.get('artist-credit')[:idx]
        primary_artists = [artist for artist in primary_artists if artist != ' & ']
        match *= max([
            SequenceMatcher(None, track_og.get('primary_artist').lower(), artist['name'].lower())
            for artist in primary_artists
        ])
    
    # featured artists
    if track_og.get('featured_artists') and ' feat. ' in track_retrieved.get('artist-credit'):
        idx = track_retrieved.get('artist-credit').index(' feat. ')
        featured_artists = track_retrieved.get('artist-credit')[:idx]
        featured_artists = [artist for artist in featured_artists if artist != ' & ']
        match *= max([
            SequenceMatcher(None, track_og.get('primary_artist').lower(), artist['name'].lower())
            for artist in featured_artists
        ])
    
    # language
    
    # album
    
    # release, album release
    
    return match


def matching_score_artist(artist_og: dict, artist_retrieved: dict) -> float:
    """
    Computes matching score between original and retrieved artists.

    Parameters
    ----------
    artist_og: dict
        Artist object from the original dataset.
    artist_retrieved: dict
        Artist item from the retrieved data.
    
    Returns
    -------
    float
        Matching score between original and retrieved artists.
    """
    match = 1.0
    
    # name

    # gender
    
    # country
    
    # birth, death

    # places
    
    return