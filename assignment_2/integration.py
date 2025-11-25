"""
Integration module
------------------

Contains functions to integrate obtained data with
the original dataset.
"""


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
    if track_og['title'].lower() != track_retrieved['title'].lower():
        match *= 0.3
    
    # artist
    # TODO deal with ' & '
    if (
        track_og.get('primary_artist') and
        track_retrieved['artist-credit'][0]['name'].lower() not in track_og.get('primary_artist').lower()):
        match *= 0.6
    
    # featured artists
    # deal with ' feat. '
    
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