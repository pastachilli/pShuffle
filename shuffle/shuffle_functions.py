import xml.etree.ElementTree as ET
import numpy as np
from scipy.spatial.distance import cosine

# Parse the XML and convert to a list of dicts
def parse_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    songs = []
    for track in root.findall('track'):
        song = {child.tag: child.text for child in track}
        song = {k: float(v) if k not in ['title', 'id', 'artist', 'type', 'uri', 'track_href', 'analysis_url'] else v
                for k, v in song.items()}
        songs.append(song)
    return songs


# Calculate weighted Euclidean distance between two songs
def calculate_distance(song1, song2, weights, attributes, distance_type='euclidean'):
    if distance_type == 'euclidean':
        dist = 0
        for key in attributes:
            dist += weights.get(key, 1) * (song1[key] - song2[key]) ** 2
        return np.sqrt(dist)
    elif distance_type == 'cosine':
        # For cosine distance, create vectors containing the weighted attributes
        vec1 = np.array([weights.get(key, 1) * song1[key] for key in attributes])
        vec2 = np.array([weights.get(key, 1) * song2[key] for key in attributes])
        # Calculate cosine distance and return 1 - value to get similarity measure
        return 1 - cosine(vec1, vec2)
    else:
        raise ValueError("Invalid distance_type. Expected 'euclidean' or 'cosine'")



# Main function to find similar songs
def find_similar_songs(song_id, songs, weights, attributes, num_neighbors=20):
    target_song = next(song for song in songs if song['id'] == song_id)
    distances = []

    for song in songs:
        if song['id'] != song_id:  # Don't compare the song with itself
            distance = calculate_distance(target_song, song, weights, attributes)
            distances.append((song, distance))

    distances.sort(key=lambda x: x[1])  # Sort by distance
    return distances[:num_neighbors]  # Return the top 20 songs along with their distances

# Function used to reward more similar songs
def roulette_selection(similar_songs_with_distances, queued_song_ids, exponent=10):
    # Filter out songs that are already in the queue
    filtered_songs_with_distances = [(song, distance) for song, distance in similar_songs_with_distances if song['id'] not in queued_song_ids]

    # Take only the top 3 songs based on distance
    top_songs_with_distances = filtered_songs_with_distances[:3]

    # If there are less than 3 songs available, select from whatever is available
    if len(top_songs_with_distances) == 0:
        return None

    # Initialize a list to store the probabilities for the top 3 songs
    probabilities = []

    # Process each of the top 3 songs and calculate its probability
    for song, distance in top_songs_with_distances:
        # Calculate the probability using the inverse of the distance and apply an exponent
        prob = (1 / distance if distance != 0 else 1.0) ** exponent
        probabilities.append(prob)

    # Normalize the probabilities so they form a probability distribution
    total = sum(probabilities)
    probabilities = [prob / total for prob in probabilities]

    # Randomly select a song based on the probability distribution
    selected_index = np.random.choice(len(top_songs_with_distances), p=probabilities)
    selected_song = top_songs_with_distances[selected_index][0]

    return selected_song

def generate_song_queue(initial_song_id, songs, weights, attributes, num_songs, exponent=2):
    current_song_id = initial_song_id
    song_queue = [next(song for song in songs if song['id'] == initial_song_id)]
    queued_song_ids = {initial_song_id}  # Set of IDs to track already queued songs

    while len(song_queue) < num_songs + 1:  # +1 because the initial song is already in the queue
        # Find similar songs to the current song
        similar_songs_with_distances = find_similar_songs(current_song_id, songs, weights, attributes)

        # Select the next song using roulette selection
        selected_song = roulette_selection(similar_songs_with_distances, queued_song_ids, exponent)

        # Add the selected song to the queue
        song_queue.append(selected_song)
        queued_song_ids.add(selected_song['id'])

        # Update the current song to the selected song
        current_song_id = selected_song['id']

    return song_queue

