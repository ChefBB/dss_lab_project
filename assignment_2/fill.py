"""
Fill module
-----------

Contains functions to fill missing values for both artists and tracks.
"""
import requests


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

    return tracks_og


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
    for a_og, a_ret in (
        (a_og, a_ret)
        for a_og, a_ret in zip(artists_og, artists_retrieved)
        if a_ret['matching-score'] >= 0.7
    ):
        # type
        a_og['type'] = a_ret.get('type')
        
        # gender
        if not a_og.get('gender') and a_ret.get('gender'):
            a_og['gender'] = a_ret['gender']

        # active_end
        if (not a_og.get('active-end') and
            a_ret.get('life-span')
        ):
            a_og['active-end'] = a_ret['life-span'].get('ended')
        
        search = None
        
        # begin area
        if a_ret.get('begin-area'):
            if a_ret['begin-area']['type'] == 'Country':
                a_og['country'] = a_ret['begin-area']['name']
                search = a_og['country']
            elif a_ret['begin-area']['type'] == 'Region':
                a_og['region'] = a_ret['begin-area']['name']
                search = a_og['region']
            else:
                a_og['birth_place'] = a_ret['begin-area']['name']
                search = a_og['birth_place']
        
        elif a_ret.get('area'):
            if a_ret['area']['type'] == 'Country':
                a_og['country'] = a_ret['area']['name']
                search = a_og['country']
            elif a_ret['area']['type'] == 'Region':
                a_og['region'] = a_ret['area']['name']
                search = a_og['region']
            else:
                a_og['birth_place'] = a_ret['area']['name']
                search = a_og['birth_place']
        
        if search:
            # geo interrog
            resp = geo_query(search)[0]
            if resp and resp.get('address'):
                # country
                if resp.get('address').get('country'):
                    a_og['country'] = resp['address']['country']
                # region
                if resp.get('address').get('state'):
                    a_og['region'] = resp['address']['state']
                # province
                if resp.get('address').get('county'):
                    a_og['province'] = resp['address']['county']
            # latitude/longitude
            if resp.get('lat') and resp.get('lon'):
                a_og['latitude'] = resp.get('lat')
                a_og['longitude'] = resp.get('lon')
        
        # person-specific
        if a_og.get('type') == 'Person':
            # birth_date
            # replacement: the original dataset often involves
            # simplifications (e.g. 1st jan)
            if (a_ret.get('life-span') and
                a_ret.get('life-span').get('begin')
            ):
                a_og['birth_date'] = a_ret['life-span']['begin']
            # ative end
            if (a_ret.get('life-span') and
                a_ret.get('life-span').get('end')
            ):
                a_og['active_end'] = a_ret['life-span']['end']

        # group-specific
        elif a_og.get('type') == 'Group':
            # active start
            if (a_ret.get('life-span') and
                a_ret.get('life-span').get('begin')
            ):
                a_og['active_start'] = a_ret['life-span']['begin']
            
            # ative end
            if (a_ret.get('life-span') and
                a_ret.get('life-span').get('end')
            ):
                a_og['active_end'] = a_ret['life-span']['end']
        
    return artists_og


# GEO INTERROGATION

URL = "https://nominatim.openstreetmap.org/search"


def geo_query(place:str) -> dict | None:
    """
    Interrogates openstreetmap to get info about birthplace of artists.
    
    Parameters
    ----------
    place: str
        The place to search for (can be country, region, city).
        
    Returns
    -------
    dict | None
        Response from the server, as a dictionary, or None if an error occurred.
    """
    try:
        params = {
            "q": place,
            "format": "json",
            "addressdetails": 1,
            "limit": 1
        }

        headers = {
            "User-Agent": "MyResearchProject/1.0 (b.barbieri7@studenti.unipi.it)"
        }


        response = requests.get(URL, params=params, headers=headers)
        return response.json()
    except Exception:
        return None