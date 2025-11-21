"""
Data retrieval module
-------

Contains functions to retrieve data from the musicbrainzngs API.
"""

import musicbrainzngs as mb


countries_map = {
    'Italia': 'IT'
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
    
    Parameters
    ----------
    artist: dict
        Dictionary representing an artist.
        
    Returns
    -------
    str
        Lucene query containing the artist's info.
    """
    clauses = []

    # Name
    if artist.get("name"):
        name = artist["name"]
        clauses.append(f'name:"{name}"')

    # Country / nationality
    if artist.get("country"):
        country = artist["country"]
        country = countries_map[country]
        clauses.append(f'country:"{country}"')
    else: clauses.append('country:"IT"')

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