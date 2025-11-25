"""
Data retrieval module
-------

Contains functions to retrieve data from the musicbrainzngs API.
"""
import musicbrainzngs as mb
import re
import time
from random import uniform

DATE_RE = re.compile(r'^\d{4}(-\d{2}){0,2}$')

countries_map = {
    'Italia' : 'IT'
}

gender_map = {
    'M' : 'male',
    'F' : 'female'
}


def setup(name: str, pwd: str, app: str):
    """
    Configure authentication and user-agent for the backend client.
    
    Parameters
    ----------
    name : str
        Username or client identifier used for authentication.
    pwd : str
        Password or secret used for authentication. Treat this value as sensitive
        and avoid hardcoding it in source; prefer environment variables or a
        secret manager.
    app : str
        Application name to include in the user-agent header.
    """
    mb.auth(name, pwd)
    mb.set_useragent(app=app, version='0.1')
    



# INTERROGATION FUNCTIONS

# ARTISTS


def query_args_artist(artist: dict) -> list:
    """
    Starting from artist dict, builds a list of Lucene clauses with the available data.
    
    Parameters
    ----------
    artist: dict
        Dictionary representing an artist.
        
    Returns
    -------
    list
        List of artist info, formatted for building a Lucene query.
    """
    clauses = []

    # Name
    if artist.get('name'):
        name = artist['name']
        # replace _ with \'
        # (dargen d_amico)
        if "_" in name:
            name = name.replace('_', '\'')
        clauses.append(f'name:"{name}"')

    desc = artist.get('description')
    
    # gender
    if artist.get('gender') and desc and not 'gruppo' in desc:
        gender = artist['gender']
        gender = gender_map[gender]
        clauses.append(f'gender:"{gender}"')
    
    # birth/begin date
    begin = artist.get('birth_date')
    # for single people, musicbrainz only has birth date
    # active_start is useful when searching for groups
    if begin is None and desc and 'gruppo' in desc:
        begin = artist.get('active_start')

    if begin and DATE_RE.match(begin):
        # only consider year
        begin = begin.split('-')[0]
        clauses.append(f'begin:"{begin}"')
        
    # Country / nationality
    if artist.get('country'):
        country = artist['country']
        country = countries_map[country]
        clauses.append(f'country:"{country}"')
    else: clauses.append('country:"IT"')

    return clauses


def artist_interrog(args: list) -> dict:
    """
    Starting from args list, iteratively interrogates Musicbrainz, adding
    clauses.
    
    Parameters
    ----------
    args: list
        List of clauses.
        
    Returns
    -------
    dict
        Musicbrainz's last non-emtpy answer.
    """
    answer = []
    query = None
    for arg in args:
        if not query:
            query = arg
        else:
            query = ' AND '.join([query, arg])
        curr_ans = None
        # iter interrogations until an answer is given
        while curr_ans is None:
            try:
                curr_ans = mb.search_artists(query, limit=10)
            except Exception:
                time.sleep(uniform(0.5, 1))
        
        if curr_ans['artist-count'] == 0:
            if answer == []:
                return curr_ans
            return answer
        elif curr_ans['artist-count'] == 1:
            return curr_ans
        else:       # more than one artist returned
            answer = curr_ans
    return answer


# SONGS RETRIEVAL


def query_args_recordings(song: dict) -> list:
    """
    Starting from song dict, builds a list of Lucene clauses with the available data.
    
    Parameters
    ----------
    song: dict
        Dictionary representing a song.
        
    Returns
    -------
    list
        List of recording info, formatted for building a Lucene query.
    """
    clauses = []
    
    # title
    if song.get('title'):
        title = song['title']
        clauses.append(f'title:"{title}"')
        
    # artist
    if song.get('primary_artist'):
        artist = song['primary_artist']
        clauses.append(artist)
    
    # albums + album_name
    albums = None
    if song.get('album'):
        albums = f'"{song['album']}"'
    album_name = song.get('album_name')
    if album_name and (not albums or song != album_name):
        if not albums:
            albums = album_name
        else:
            albums = f'({albums} OR "{album_name}")'
    if albums:
        clauses.append(albums)
    
    # date
    dates = None
    if song.get('year'):
        dates = str(int(song['year']))
    alb_rel_date = song.get('album_release_date')
    if alb_rel_date and (not dates or dates[0] != alb_rel_date):
        if not dates:
            dates = dates
        else:
            dates = f'({dates} OR "{alb_rel_date}")'
    if dates:
        clauses.append(dates)
    
    return clauses


def recording_interrog(args: list) -> dict:
    """
    Starting from args list, iteratively interrogates Musicbrainz, adding
    clauses.
    
    Parameters
    ----------
    args: list
        List of clauses.
        
    Returns
    -------
    dict
        Musicbrainz's last non-emtpy answer.
    """
    answer = []
    query = None
    for arg in args:
        if not query:
            query = arg
        else:
            query = ' AND '.join([query, arg])
        curr_ans = None
        # iter interrogations until an answer is given
        while curr_ans is None:
            try:
                curr_ans = mb.search_recordings(query, limit=10)
            except Exception:
                time.sleep(uniform(0.5, 1))
        
        if curr_ans['recording-count'] == 0:
            if answer == []:
                return curr_ans
            return answer
        elif curr_ans['recording-count'] == 1:
            return curr_ans
        else:
            answer = curr_ans
    return answer