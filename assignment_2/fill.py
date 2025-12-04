"""
Fill module
-----------

Contains functions to fill missing values for both artists and tracks.
"""
import requests


def mb_lookup(entity: str, mbid: str, inc=None):
    """
    Requests an entity from musicbrainz.
    
    Parameters
    ----------
    entity: 
    """
    base = f'https://musicbrainz.org/ws/2/{entity}/{mbid}'
    params = {'fmt': 'json'}
    if inc:
        params['inc'] = inc
    r = requests.get(base, params=params, headers={
        'User-Agent': 'MyMusicApp/1.0 ( your_email@example.com )'
    })
    return r.json()


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
    for t_og, t_ret in (
        (t_og, t_ret)
        for t_og, t_ret in zip(tracks_og, tracks_retrieved)
        if t_ret['matching-score'] >= 0.8
    ):
        data = None
        track_data = None
        
        # album
        if not t_og.get('album_name') and t_og.get('album'):
            t_og['album_name'] = t_og['album']
            
        elif (
            not t_og.get('album_name') and
            not t_og.get('album') and
            t_ret.get('release_list')
        ):
            for release in t_ret['release_list']:
                release_data = None
                while not release_data:
                    try:
                        release_data = mb_lookup(
                            'release', release['id'],
                            inc='recordings+artist-credits'
                        )
                    except Exception:
                        print('failure; retrying...')
                if (release_data and (
                        not data or
                        data['date'] > release_data['date'])
                ):
                    data = release_data
        
        # get album data
        if not data and t_ret.get('release-list'):
            for release in t_ret['release-list']:
                if (
                    t_og.get('album_name') and
                    release.get('title').lower() == t_og.get('album_name')
                ):
                    data = None
                    while not data:
                        try:
                            data = mb_lookup('release', release['id'], inc='recordings')
                        except Exception:
                            print('failure; retrying...')
        
        # get track data
        if (
            not track_data and
            data and
            data.get('media')
        ):
            for track in data['media'][0]['tracks']:
                if track['title'].lower() == t_og['title'].lower():
                    track_data = track
                    break
                    

        # fill album data
        if data:
            if not t_og.get('album_name'):
                t_og['album_name'] = data['title']
                
            # album release date
            if not t_og.get('album_release_date') and data.get('date'):
                t_og['album_release_date'] = data['date']
        
            # album type: not found
            
            # disc number: not found

        # fill track data
        if not track_data:
            track_data = t_ret
            
        # year month day
        if (
            track_data.get('recording') and
            track_data['recording'].get('first-release-date')
        ):
            date = track_data['recording']['first-release-date'].split('-')
            if len(date) == 3:
                t_og['year'] = date[0]
                t_og['month'] = date[1]
                t_og['day'] = date[2]
            elif len(date) == 1:
                t_og['year'] = date[0]
                
        # track number
        if track_data.get('number'):
            t_og['track_number'] = track_data['number']
        
        # duration ms
        if (
            not t_og.get('duration_ms') and
            track_data.get('length')
        ):
            t_og['duration_ms'] = track_data['length']

        # primary artist + id_artist
        if (
            not t_og.get('primary_artist') and
            track_data.get('artist-credit')
        ):
            t_og['primary_artist'] = track_data['artist_credit']['name']

        # feat
        if not t_og.get('featured_artists') and track_data.get('artist-credit'):
            featured_artists = ''
            for artist in track_data.get('artist-credit', [])[1:]:
                if isinstance(artist, dict):
                    featured_artists += f', {artist['name']}'
    
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