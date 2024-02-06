import shuffle_functions as sf

# Sample XML data
xml_file = "../xml_files/playlist_5X13HtrTfhv5JpnTeMtL0D.xml"  # Your XML data goes here

# Parse XML data
songs = sf.parse_xml(xml_file)

# Weights dictionary (customize as needed)\
attribute_keys = ['danceability',
                  'energy',
                  'speechiness',
                  'acousticness',
                  'instrumentalness',
                  'liveness',
                  'valence'
                  ]

weights = {
    'danceability': 1,
    'energy': 1,
    'speechiness': 1,
    'acousticness': 1,
    'instrumentalness': 1,
    'liveness': 1,
    'valence': 1
}

similar_songs_with_distances = sf.find_similar_songs('4jz3eqH3Y8j565cUe3aSOq', songs, weights, attribute_keys)
selected_song, similarity_value = sf.roulette_selection(similar_songs_with_distances)
print(f"Selected Song: {selected_song['title']} by {selected_song['artist']} - Similarity Value: {similarity_value}")