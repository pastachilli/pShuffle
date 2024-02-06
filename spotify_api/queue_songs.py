import configparser
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials
from shuffle import shuffle_functions as sf
xml_file = "../xml_files/playlist_5X13HtrTfhv5JpnTeMtL0D.xml"  # Your XML data goes here

# Parse XML data
songs = sf.parse_xml(xml_file)

# Weights dictionary (customize as needed)
attribute_keys = ['danceability',
                  'energy',
                  'loudness',
                  'speechiness',
                  'acousticness',
                  'instrumentalness',
                  'liveness',
                  'valence',
                  'tempo'
                  ]

weights = {
    'danceability': 1.2,
    'energy': 1.5,
    'loudness': 1,
    'speechiness': 1,
    'acousticness': 1.2,
    'instrumentalness': 1.2,
    'liveness': 1,
    'valence': 0.8,
    'tempo': 0
}

# weights = {
#     'danceability': 1.5,
#     'energy': 3,
#     'loudness': 2,
#     'speechiness': 1,
#     'acousticness': 2,
#     'instrumentalness': 3,
#     'liveness': 1,
#     'valence': 1,
#     'tempo': 0
# }

# Useful song ID's
# Mandolin Wind - Rod Stewart: 4sWZwY8RQfK6Fc2pYC7tN1
# Thunderstruck - ACDC: 57bgtoPSgt236HzfBOd8kj
# Stay With Me - Faces: 7fLTytvnvxy653VWxflTRf
# La Vie En Rose - Louis Armstrong: 1UH4viviUjZnS9aWgPGrk0
# Celebrity Skin - Hole: 2V4Bc2I962j7acQj1N0PiQ
# Mr. Blue Sky - ELO: 2RlgNHKcydI9sayD2Df2xp
# Aero Zeppelin - Nirvana: 6ENZJCRagbW3jlzXSucfoI
# All My Life - The Beatles: 3KfbEIOC7YIv90FIfNSZpo
# Georgia On My Mind: Oscar Peterson Trio: 7p6ZeiNtEHJKmc4YWBZELG
# Carry On - Fun: 7gpy7sfWPNuOKmUNs3XQYE
# Don't You Worry 'Bout a Thing: Stevie Wonder: 1QvWxgZvTU0w8rlPRE5Zrv

initial_song_id = '4sWZwY8RQfK6Fc2pYC7tN1'  # Replace with your actual initial song ID
num_songs_to_queue = 100  # Number of songs you want in the queue
queued_songs = sf.generate_song_queue(initial_song_id, songs, weights, attribute_keys, num_songs_to_queue)

# Read the configuration file
config = configparser.ConfigParser()
config.read("../config/config.ini")

# Get Spotify credentials from the configuration file
client_id = config.get('spotifyCredentials', 'CLIENT_ID')
client_secret = config.get('spotifyCredentials', 'CLIENT_SECRET')

# Spotify credentials and client setup
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri="http://localhost:8080/callback",
                                               scope="user-modify-playback-state"))




# For each song in your queue
for song in queued_songs:
    track_uri = song['uri']  # Assuming 'uri' is a part of your song dictionary
    sp.add_to_queue(track_uri, device_id=None)  # If you know the device ID, you can specify it here
