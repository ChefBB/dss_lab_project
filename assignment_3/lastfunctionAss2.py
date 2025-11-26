from difflib import SequenceMatcher

def matching_score_artist(artist_og: dict, artist_retrieved: dict) -> float:

    match = 1.0

    # ========= NAME SCORE =========
    og_name = artist_og.get("name")
    ret_name = artist_retrieved.get("name")

    if not og_name or not ret_name:
        return 0.0

    og_name = " ".join(og_name.lower().replace("_", " ").split())
    ret_name = " ".join(ret_name.lower().split())

    name_score = SequenceMatcher(None, og_name, ret_name).ratio()
    match *= name_score

    # ========= GENDER SCORE =========
    og_gender = artist_og.get("gender")
    if og_gender == "M":
        og_gender = "male"
    elif og_gender == "F":
        og_gender = "female"
    else:
        og_gender = None

    ret_gender = artist_retrieved.get("gender")
    if ret_gender:
        ret_gender = ret_gender.lower()

    if og_gender and ret_gender:
        gender_score = 1.0 if og_gender == ret_gender else 0.0
    else:
        gender_score = 0.5

    match *= gender_score

    # ========= COUNTRY SCORE =========
    def normalize_country(c):
        if not c or c == "(missing)":
            return None
        c = c.strip().lower()
        if c in ("italia", "italy", "it"):
            return "IT"
        if len(c) == 2:
            return c.upper()
        return c.upper()

    og_country = normalize_country(artist_og.get("country"))
    mb_country = normalize_country(artist_retrieved.get("country"))

    if og_country is None and mb_country is None:
        country_score = 1.0
    elif og_country is None:
        country_score = 1.0
    elif mb_country is None:
        country_score = 0.7
    else:
        country_score = 1.0 if og_country == mb_country else 0.0

    match *= country_score

    # ========= BIRTH SCORE =========
    def extract_year(d):
        if not d:
            return None
        s = str(d)
        return int(s[:4]) if s[:4].isdigit() else None

    og_birth = extract_year(artist_og.get("birth_date"))

    mb_birth = artist_retrieved.get("life-span", {}).get("begin")
    if mb_birth and not str(mb_birth)[:4].isdigit():
        mb_birth = None
    mb_birth = extract_year(mb_birth)

    if og_birth is None and mb_birth is None:
        birth_score = 1.0
    elif og_birth is None:
        birth_score = 0.8
    elif mb_birth is None:
        birth_score = 0.7
    else:
        diff = abs(og_birth - mb_birth)
        if diff == 0:
            birth_score = 1.0
        elif diff == 1:
            birth_score = 0.9
        elif diff <= 2:
            birth_score = 0.7
        else:
            birth_score = 0.0

    match *= birth_score

    # ========= PLACE SCORE =========
    og_place = artist_og.get("birth_place")
    mb_place = artist_retrieved.get("begin-area", {}).get("name")

    # normalizza → lowercase e strip
    def norm_place(p):
        if not p:
            return None
        return p.strip().lower()

    og_place = norm_place(og_place)
    mb_place = norm_place(mb_place)

    if og_place is None and mb_place is None:
        place_score = 1.0
    elif og_place is None:
        place_score = 0.8
    elif mb_place is None:
        place_score = 0.7
    else:
        if og_place == mb_place:
            place_score = 1.0
        else:
            # città diverse → penalizzazione moderata
            place_score = 0.7

    match *= place_score

    return match
