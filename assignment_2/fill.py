"""
Fill module
-----------

Contains functions to fill missing values for both artists and tracks.
"""


def fill_tracks(tracks_og: list, tracks_retrieved: list) -> list:
    """
    Fills the original track list with data taken from
    retreived tracks, given the match between the two is good enough.

    Parameters
    ----------
    tracks_og: list
        Original tracks.
    tracks_retrieved: list
        Retrieved tracks.
        
    Returns
    -------
    list
        Original dataset with filled values.
    """
    return


def fill_artists(artists_og: list, artists_retrieved: list) -> list:
    """
    Fills the original artist list with data taken from
    retreived artists, given the match between the two is good enough.

    Parameters
    ----------
    artists_og: list
        Original artists.
    artists_retrieved: list
        Retrieved artists.
        
    Returns
    -------
    list
        Original dataset with filled values.
    """
    for artist_og, artist_retrieved in (
        (a_og, a_ret)
        for a_og, a_ret in zip(artists_og, artists_retrieved)
        if a_ret['matching-score'] >= 0.7
    ):
        # type
        artist_og['type'] = artist_retrieved.get('type')
        
        # gender
        if not artist_og.get('gender') and artist_retrieved.get('gender'):
            artist_og['gender'] = artist_retrieved['gender']

        # active_end
        if (not artist_og.get('active-end') and
            artist_retrieved.get('life-span')
        ):
            artist_og['active-end'] = artist_retrieved['life-span'].get('ended')
        
        # person-specific
        if artist_og.get('type') == 'Person':
            # birth_date
            # replacement: the original dataset often involves
            # simplifications (e.g. 1st jan)
            if (artist_retrieved.get('life-span') and
                artist_retrieved.get('life-span').get('begin')
            ):
                artist_og['birth_date'] = artist_retrieved['life-span']['begin']
            
            # birth_place

        # group-specific
        elif artist_og.get('type') == 'Group':
            # active start
            return
        
    return artists_og