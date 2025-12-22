"""
Full assignment 2 script
"""
from support import read_json, save_data
import os
import data_retrieval as dr


###########
# LOAD DATA
###########

parent_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))

# musicbrainz credentials file
data_file = os.path.abspath(os.path.join(
    parent_dir, os.pardir, 'data.txt'
))

artists = read_json('artists.json')
tracks = read_json('tracks.json')


###############
# RETRIEVE DATA
###############

mb_artists = list()

for artist in artists:
    # get arguments, then interrogate
    args = dr.query_args_artist(artist)
    mb_artists.append(dr.artist_interrog(args))


mb_tracks = list()

for track in tracks:
    # get arguments, then interrogate
    args = dr.query_args_recordings(track)
    mb_tracks.append(dr.recording_interrog(args))

    
# save retrieved data
save_data(mb_tracks, 'mb', 'mb_tracks.json')
save_data(mb_artists, 'mb', 'mb_artists.json')


#############
# INTEGRATION
#############

from integration import compute_all_matching_scores
import fill

# compute best matching artists and tracks
mb_tracks = compute_all_matching_scores(tracks, mb_tracks)
mb_artists = compute_all_matching_scores(artists, mb_artists)


# fill datasets
tracks = fill.fill_tracks(tracks, mb_tracks)

artists = fill.fill_artists(artists, mb_artists)


##################
# GENERATE NEW IDS
##################

from uuid import uuid4

ids = set()

for artist in artists:
    new_id = str(uuid4())
    while new_id in ids:
        new_id = str(uuid4())
    ids.add(new_id)
    artist['new_id_artist'] = new_id
    
ids = set()

for track in tracks:
    new_id = str(uuid4())
    while new_id in ids:
        new_id = str(uuid4())
    ids.add(new_id)
    track['new_track_id'] = new_id
    for artist in artists:
        if artist['id_author'] == track['id_artist']:
            track['new_id_artist'] = artist['new_id_artist']
    

# save data
save_data(tracks, 'correct_ids', 'tracks.json')
save_data(artists, 'correct_ids', 'artists.json')



################
# PARTICIPATIONS
################

from support import clean_artist
from difflib import SequenceMatcher


participations = list()

for track in tracks:
    # add primary artist participation
    participations.append({
        'new_id_artist': track['new_id_artist'],
        'new_track_id': track['new_track_id'],
        'IsPrimary': 1
    })

    # handle feats
    if track.get('featured_artists'):
        featured = track['featured_artists'].split(',')

        for f in featured:
            f = clean_artist(f)
            flag = False
            
            # check in artists
            for artist in artists:
                if SequenceMatcher(None, artist['name'].lower(), f).ratio() > 0.8:
                    participations.append({
                        'new_id_artist': artist['new_id_artist'],
                        'new_track_id': track['new_track_id'],
                        'IsPrimary': 0
                    })
                    flag = True
                    break

            # check in artists_ret (with alias)
            if not flag:
                for i in range(len(mb_artists)):
                    # direct match
                    if SequenceMatcher(None, mb_artists[i]['name'].lower(), f).ratio() > 0.8:
                        participations.append({
                            'new_id_artist': artists[i]['new_id_artist'],
                            'new_track_id': track['new_track_id'],
                            'IsPrimary': 0
                        })
                        flag = True
                        break

                    # alias match
                    if mb_artists[i].get('alias-list'):
                        for alias in mb_artists[i]['alias-list']:
                            if SequenceMatcher(None, alias['alias'].lower(), f).ratio() > 0.8:
                                participations.append({
                                    'new_id_artist': artists[i]['new_id_artist'],
                                    'new_track_id': track['new_track_id'],
                                    'IsPrimary': 0
                                })
                                flag = True
                                break

                        if flag:
                            break


save_data(participations, 'correct_ids', 'participations.json')



################
# CORRECT ALBUMS
################

from support import build_albums


albums = list()
ids = set()

for track in tracks:
    curr_album = build_albums(track)
    flag = False

    # check whether album is in the known albums or not
    for album in albums:
        if (album['album_name'] == curr_album['album_name'] and
            album['album_release_date'] == curr_album['album_release_date']
        ):
            flag = True
            break

    # if album was not already present, form new id, add it to
    # known albums
    if not flag:
        new_id = str(uuid4())
        while new_id in ids:
            new_id = str(uuid4())
        
        ids.add(new_id)
        curr_album['id_album'] = new_id
        albums.append(curr_album)
        track['new_id_album'] = new_id
        
        
save_data(albums, 'correct_ids', 'albums.json')



###########
# FIX DATES
###########

dates = []
ids = set()

for track in tracks:
    new_date = {
        'year': None,
        'month': None,
        'day': None,
    }
    
    if (track.get('year') and
        track.get('month') and
        track.get('day')
    ):
        new_date = {
            'year': int(track['year']),
            'month': int(track['month']),
            'day': int(track['day']),
        }
    # only year, month
    elif (track.get('year') and
        track.get('month')
    ):
        new_date = {
            'year': int(track['year']),
            'month': int(track['month']),
            'day': None
        }
    # only year
    elif track.get('year'):
        new_date = {
            'year': int(track['year']),
            'month': None,
            'day': None
        }

    # check whether date is in the known dates or not
    flag = False
    for date in dates:
        if (date['year'] == new_date['year'] and
            date['month'] == new_date['month'] and
            date['day'] == new_date['day']
        ):
            new_date['date_id'] = date['date_id']
            track['date_id'] = date['date_id']
            flag = True
            break
    
    # if date was not already present, form new id, add it to
    # known dates
    if not flag:
        new_id = str(uuid4())
        while new_id in ids:
            new_id = str(uuid4())
        ids.add(new_id)
        new_date['date_id'] = new_id
        dates.append(new_date)
        track['date_id'] = new_id

save_data(dates, 'correct_ids', 'dates.json')



#####
# GEO
#####

from fill import geo_query
import time


geo = list()
ids = set()

for artist in artists:
    ans = None
    while not ans:
        try:
            if artist.get('birth_place'):
                time.sleep(0.3)
                ans = geo_query(artist['birth_place'])[0]
                if ans['address'].get('county'):
                    artist['province'] = ans['address']['county']
                if ans['address'].get('state'):
                    artist['region'] = ans['address']['state']
                artist['country'] = ans['address']['country']
                artist['latitude'] = ans['lat']
                artist['longitude'] = ans['lon']
            else:
                break
        except Exception as e:
            print(e)
            print(ans)

    flag = False
    for place in geo:
        # all match
        if (artist['birth_place'] == place['birth_place'] and
            artist['province'] == place['province'] and
            artist['region'] == place['region'] and
            artist['country'] == place['country']
        ):
            artist['geo_id'] = place['geo_id']
            artist['latitude'] = place['latitude']
            artist['longitude'] = place['longitude']
            flag = True
            break
    if not flag:
        new_id = str(uuid4())
        while new_id in ids:
            new_id = str(uuid4())
        ids.add(new_id)
        artist['geo_id'] = new_id
        geo.append({
            'geo_id': new_id,
            'birth_place': artist['birth_place'],
            'province': artist['province'],
            'region': artist['region'],
            'country': artist['country'],
            'latitude': artist['latitude'],
            'longitude': artist['longitude']
        })
        

save_data(geo, 'correct_ids', 'geo.json')