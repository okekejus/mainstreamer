# if a client clicks log in with spotify, you'd want this to be used.

import pandas as pd
import json 
import os 
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import time 
from spotipy.exceptions import SpotifyException
import numpy as np
import datetime as dt 
import requests 

scope = "user-library-read playlist-read-private playlist-read-collaborative"
sp = spotipy.Spotify(auth_manager = SpotifyOAuth(scope=scope))
rundate = str(dt.date.today()) # runs daily at 11:59 PM


def get_user_tracks(user): 

  """ Getting ALL tracks within the current user's library""" 
    try:
        results = user.current_user_saved_tracks(limit=50)
        tracks = results['items']
        while results['next']:
            results = user.next(results)
            tracks.extend(results['items'])
            time.sleep(1)
        my_songs_df = pd.DataFrame(tracks)

        song_titles = [value.get('name') for value in my_songs_df['track'].values]
        song_release = [track['album']['release_date'] for track in my_songs_df['track']]
        song_popularity = [value.get('popularity') for value in my_songs_df['track'].values]
        song_ids = [value.get('id') for value in my_songs_df['track'].values]
        song_duration = [round(value.get('duration_ms')/60000, 2) for value in my_songs_df['track'].values]
        extracts = pd.DataFrame({'song_name': song_titles, 'song_id':song_ids, 'song_popularity': song_popularity, 'song_release': song_release, 'song_duration': song_duration})

        return extracts
    except (spotipy.exceptions.SpotifyBaseException, KeyboardInterrupt) as e: 
        print(f"Process was interrupted due to the following error: {e}")

def get_user_top_tracks(user):
  """ Getting the user's most listened tracks, over a long term period - defined as 1 year by Spotify"""
   try:
    results = user.current_user_top_tracks(limit=50, time_range="long_term")
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
        time.sleep(1)
    top_tracks = pd.DataFrame(tracks)[['id', 'name', 'popularity']]
    return top_tracks
   except (spotipy.exceptions.SpotifyBaseException, KeyboardInterrupt) as e: 
        print(f"Process was interrupted due to the following error: {e}")


def gather():
  """ Uses gathered songs to determine popularity scores for current user """

    my_songs = get_user_tracks(sp)
    my_songs = my_songs.astype({'song_popularity': int})
    user_popularity_score = np.average(my_songs['song_popularity'])
    # getting the tracks a user most frequently listens to 
    top_tracks = get_user_top_tracks(sp)
    most_listened_pop_score = round(np.average(top_tracks['popularity'][0:100]),2)
    med_song_duration = round(np.average(my_songs['song_duration'][0:100]),2)
    d = {"run_date": [rundate], 
        "total_songs": [len(my_songs['song_name'])], 
        "popularity_score": [user_popularity_score], 
        "most_listened_pop_score": [most_listened_pop_score], 
        "avg_song_duration": [med_song_duration]}

    addon = pd.DataFrame(d)
    return addon
    

def main():
    gather()


if __name__ == "__main__": 
    main()

__all__ = ["get_user_top_tracks", "get_user_tracks", "gather", "scope"]
