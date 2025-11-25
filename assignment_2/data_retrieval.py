"""
Data retrieval module
-------

Contains functions to retrieve data from the musicbrainzngs API.
"""
<<<<<<< HEAD

import musicbrainzngs as mb


countries_map = {
    'Italia': 'IT'
=======
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
>>>>>>> 2936192c117c9f8f4d83052392831d521ec8c7ce
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

<<<<<<< HEAD
# def escape_lucene(s: str) -> str:
#     """
#     Escape Lucene special characters.
#     """
#     if s is None:
#         return None
#     return re.sub(r'([+\-!(){}[\]^"~*?:\\/])', r'\\\1', s)


def build_query(artist: dict) -> str:
    """
    Starting from artist dict, builds a Lucene query with the available data.
=======
# ARTISTS


def query_args_artist(artist: dict) -> list:
    """
    Starting from artist dict, builds a list of Lucene clauses with the available data.
>>>>>>> 2936192c117c9f8f4d83052392831d521ec8c7ce
    
    Parameters
    ----------
    artist: dict
        Dictionary representing an artist.
        
    Returns
    -------
<<<<<<< HEAD
    str
        Lucene query containing the artist's info.
=======
    list
        List of artist info, formatted for building a Lucene query.
>>>>>>> 2936192c117c9f8f4d83052392831d521ec8c7ce
    """
    clauses = []

    # Name
<<<<<<< HEAD
    if artist.get("name"):
        name = artist["name"]
        clauses.append(f'name:"{name}"')

    # Country / nationality
    if artist.get("country"):
        country = artist["country"]
=======
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
>>>>>>> 2936192c117c9f8f4d83052392831d521ec8c7ce
        country = countries_map[country]
        clauses.append(f'country:"{country}"')
    else: clauses.append('country:"IT"')

<<<<<<< HEAD
    return " AND ".join(clauses)


def update_artist_from_mb(artist: dict, mb: dict, overwrite: bool = False) -> dict:
    """
    Update an existing internal artist dictionary with data obtained from a
    MusicBrainz NGS artist record.

    Parameters
    ----------
    artist : dict
        The internal artist object to update.
    mb : dict
        A dictionary returned by musicbrainzngs representing a single artist.
    overwrite : bool, optional
        If True, MusicBrainz fields overwrite existing non-null values in the
        internal artist object. Defaults to False.

    Returns
    -------
    dict
        The new modified dictionary.
    """

    def set_field(key: str, value):
        """
        Set field only if overwrite=True or current value is None/empty.

        Parameters
        ----------
        key: str
            The key to be modified.

        value: str
            The new value.
        """
        if value is None:
            return
        if overwrite or artist.get(key) in (None, "", []):
            artist[key] = value

    # --- Basic fields ---
    set_field("id_author", mb.get("id"))
    set_field("name", mb.get("name"))

    # Gender normalization
    gender = mb.get("gender")
    if gender:
        normalized = "M" if gender.lower() == "male" else "F" if gender.lower() == "female" else None
        set_field("gender", normalized)

    # --- Life span ---
    ls = mb.get("life-span", {})

    # birth date = life-span.begin
    set_field("birth_date", ls.get("begin"))

    # active_start: prefer your existing value, but MB can fill missing
    set_field("active_start", ls.get("begin"))

    # active_end: MB: ended="false" means still active
    ended = ls.get("ended")
    if ended not in ("false", False, None):
        set_field("active_end", ended)

    # --- Area (country) ---
    if "area" in mb:
        set_field("country", mb["area"].get("name"))

    # --- Birthplace (begin-area) ---
    if "begin-area" in mb:
        set_field("birth_place", mb["begin-area"].get("name"))

    # --- Tags → description ---
    if "tag-list" in mb:
        tags = [t["name"] for t in mb["tag-list"]]
        if tags:
            set_field("description", ", ".join(tags))

    # --- Alias → nationality (Italian example) ---
    for a in mb.get("alias-list", []):
        if a.get("locale", "").startswith("it"):
            set_field("nationality", "Italia")

    return artist
=======
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
        else:       # more than one artist returned
            answer = curr_ans
    return answer
>>>>>>> 2936192c117c9f8f4d83052392831d521ec8c7ce
