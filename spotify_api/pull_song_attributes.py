import configparser
import xml.etree.ElementTree as ET
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import time
from tqdm import tqdm  # Import the tqdm function


def fetch_audio_features(sp, track_id):
    while True:
        try:
            return sp.audio_features(track_id)[0]
        except spotipy.SpotifyException as e:
            if e.http_status == 429:
                retry_after = int(e.headers['Retry-After'])
                print(f"Rate limiting in effect, sleeping for {retry_after} seconds.")
                time.sleep(retry_after)  # Adding 1 to ensure it waits enough.
            else:
                raise e


# Read the configuration file
config = configparser.ConfigParser()
config.read("../config/config.ini")

# Get Spotify credentials from the configuration file
client_id = config.get('spotifyCredentials', 'CLIENT_ID')
client_secret = config.get('spotifyCredentials', 'CLIENT_SECRET')

# Spotify credentials and client setup
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

playlist_id = '2W3uVri9LqxSHLFZLsxMgJ'  # Replace with your playlist ID
fields = "items.track(id,name,artists(name)),next"  # Define the fields you want to extract

# Fetch tracks from the playlist
tracks = []
results = sp.playlist_tracks(playlist_id, fields=fields)
tracks.extend(results['items'])

# Keep fetching next set of tracks if available
while results['next']:
    results = sp.next(results)
    tracks.extend(results['items'])

# Create the XML structure for audio features
root = ET.Element("playlist")

# Initialize tqdm progress bar
progress_bar = tqdm(total=len(tracks), desc="Processing tracks", unit="track")

for item in tracks:
    track = item['track']
    track_id = track['id']

    # Fetch audio features for the track, handling rate limiting
    audio_features = fetch_audio_features(sp, track_id)

    if audio_features:
        track_element = ET.SubElement(root, "track")

        # Extract and set the song title, ID, and artist
        ET.SubElement(track_element, "title").text = track['name']
        ET.SubElement(track_element, "id").text = track_id
        ET.SubElement(track_element, "artist").text = ', '.join(artist['name'] for artist in track['artists'])

        # Add audio features
        for feature_name, feature_value in audio_features.items():
            if feature_value is not None:
                ET.SubElement(track_element, feature_name).text = str(feature_value)

    progress_bar.update(1)  # Update the progress bar

# Close the progress bar
progress_bar.close()

# Convert the XML structure to a string
xml_str = ET.tostring(root, encoding='unicode')

# Save the XML to a file
with open("../xml_files/playlist_" + playlist_id + ".xml", "w") as f:
    f.write('<?xml version="1.0"?>\n')
    f.write(xml_str)

print("XML file with audio features created successfully.")
