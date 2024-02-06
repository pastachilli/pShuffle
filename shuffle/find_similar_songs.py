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


# Find similar songs
similar_songs = sf.find_similar_songs('57bgtoPSgt236HzfBOd8kj', songs, weights, attribute_keys)
for song, distance in similar_songs:
    print(f"{song['title']} by {song['artist']} - Similarity Value: {distance}")
