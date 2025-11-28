"""
Integration module
------------------

Contains functions to integrate obtained data with
the original dataset.
"""
from difflib import SequenceMatcher
from math import sqrt, exp


countries_map = {
    'Italia' : 'IT'
}

gender_map = {
    'M' : 'male',
    'F' : 'female'
}


def compute_match_scores(data_og: dict, data_retrieved: dict) -> dict:
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
        Dictionary of objects with their matching score attached.
    """
    if data_retrieved.get('recording-list'):
        flag = True
    else:
        flag = False
    for item in data_retrieved['recording-list' if flag else 'artist-list']:
        item['matching-score'] = (
            matching_score_track(data_og, item) if flag
            else matching_score_artist(data_og, item)
        )
    
    return data_retrieved


def soft_penalty(factors: list[float], order_weighted: bool = False) -> float:
    """
    Computes a softened penalty based on a list of multiplicative factors.
    Longer lists get penalized less, and optionally earlier elements
    contribute more heavily.

    Parameters
    ----------
    factors : list of float
        List of penalty multipliers (typically between 0 and 1).
    order_weighted : bool, optional
        If True, earlier elements get more influence.
        If False, all elements are weighted equally.

    Returns
    -------
    float
        Adjusted penalty score with softening for longer lists.
    """
    n = len(factors)
    if n == 0:
        return 0.0

    # order-based weighting
    if order_weighted:
        # earlier elements get higher weights
        weights = [exp(- i / n) for i in range(n)]
        total_weight = sum(weights)
        weighted_product = 1.0
        for w, f in zip(weights, factors):
            weighted_product *= f ** (w / total_weight)
    else:
        weighted_product = 1.0
        for f in factors:
            weighted_product *= f

    # length-based softening 
    soften = 1 / sqrt(n)
    
    adjusted = 1 - (1 - weighted_product) * soften

    return adjusted


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
    factors = []
    
    # title
    factors.append(
        SequenceMatcher(None,
                        track_og['title'].lower(),
                        track_retrieved['title'].lower()).ratio())
    
    # artist
    if track_og.get('primary_artist'):
        idx = len(track_retrieved.get('artist-credit')) + 1
        if ' feat. ' in track_retrieved.get('artist-credit'):
            idx = track_retrieved.get('artist-credit').index(' feat. ')
        elif ' Feat ' in track_retrieved.get('artist-credit'):
            idx = track_retrieved.get('artist-credit').index(' Feat ')
        primary_artists = track_retrieved.get('artist-credit')[:idx]
        primary_artists = [artist for artist in primary_artists
                           if isinstance(artist, dict)]
        penalty = max([SequenceMatcher(None,
                                       track_og['primary_artist'].lower(),
                                       artist['name'].lower()).ratio()
                       for artist in primary_artists])
        factors.append(penalty)
    
    # featured artists
    if track_og.get('featured_artists') and ' feat. ' in track_retrieved.get('artist-credit'):
        artists_retrieved = track_retrieved.get('artist-credit')
        artists_retrieved = [artist for artist in artists_retrieved
                                      if isinstance(artist, dict)]
        featured_artists_og = track_og['featured_artists'].split(', ')
        # takes best match for each featured artist in the og dataset
        factors.append(soft_penalty([max([
            SequenceMatcher(None,
                            artist_og.lower(),
                            artist_retrieved['name'].lower()).ratio()
                    for artist_retrieved in artists_retrieved])
                for artist_og in featured_artists_og]))
        
    
    # album
    if track_og.get('album_name') and track_retrieved.get('release-list'):
        album_name_og = track_og.get('album_name')
        factors.append(max([SequenceMatcher(None,
                                album_name_og.lower(),
                                release['title'].lower()).ratio()
                           for release in track_retrieved['release-list']]))
    
    return soft_penalty(factors, True)


# cut at 0.7
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
    factors = []

    # name
    og_name = artist_og.get('name')
    ret_name = artist_retrieved.get('name')
    factors.append(SequenceMatcher(None,
                                   og_name.lower().replace('_', '\''),
                                   ret_name.lower()).ratio())

    # gender
    og_gender = artist_og.get('gender')
    if og_gender:
        og_gender = gender_map[og_gender]
        ret_gender = artist_retrieved.get('gender')
        if ret_gender:
            ret_gender = ret_gender.lower()
        if og_gender and ret_gender:
            factors.append(1.0 if og_gender == ret_gender else 0.6)

    # country
    og_country = artist_og.get('country')
    mb_country = artist_retrieved.get('country')
    if og_country and mb_country and countries_map[og_country] != mb_country:
        factors.append(0.8)

    # birth date
    def extract_year(d):
        if not d:
            return None
        s = str(d)
        return int(s[:4]) if s[:4].isdigit() else None

    og_birth = extract_year(artist_og.get('birth_date'))
    mb_birth = artist_retrieved.get('life-span', {}).get('begin')
    if mb_birth and not str(mb_birth)[:4].isdigit():
        mb_birth = None
    mb_birth = extract_year(mb_birth)
    if og_birth and mb_birth:
        diff = abs(og_birth - mb_birth)
        steepness = 0.8
        max_penalty = 0.6
        penalty = max_penalty * (1 - exp(-steepness * diff))
        factors.append(1 - penalty)

    # birth place
    og_place = artist_og.get('birth_place')
    mb_place = artist_retrieved.get('begin-area', {}).get('name')
    if og_place and mb_place:
        factors.append(
            SequenceMatcher(None,
                            og_place.lower(),
                            mb_place.lower()).ratio())

    return soft_penalty(factors, True)