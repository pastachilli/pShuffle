import shuffle_functions as sf

# Sample XML data
xml_file = "../xml_files/playlist_5X13HtrTfhv5JpnTeMtL0D.xml"  # Your XML data goes here

# Parse XML data
songs = sf.parse_xml(xml_file)

# Weights dictionary (customize as needed)\
attribute_keys = ['danceability',
                  'energy',
                  'loudness',
                  'speechiness',
                  'acousticness',
                  'instrumentalness',
                  'liveness',
                  'valence'
                  ]

weights = {
    'danceability': 1.2,
    'energy': 1.2,
    'loudness': 1,
    'speechiness': 1,
    'acousticness': 0.6,
    'instrumentalness': 1,
    'liveness': 0,
    'valence': 1.5,
}

initial_song_id = '4smkJW6uzoHxGReZqqwHS5'  # Replace with your actual initial song ID
num_songs_to_queue = 30  # Number of songs you want in the queue
queued_songs = sf.generate_song_queue(initial_song_id, songs, weights, attribute_keys, num_songs_to_queue)

for song in queued_songs:
    print(song)