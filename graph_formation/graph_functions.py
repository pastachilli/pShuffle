import numpy as np
from scipy.spatial.distance import euclidean, cosine
import xml.etree.ElementTree as ET
import networkx as nx
from pyvis.network import Network
from tqdm import tqdm
from itertools import combinations
from multiprocessing import Pool
import matplotlib.pyplot as plt
from collections import defaultdict

# Attributes to take into account when forming the graph
SELECTED_ATTRIBUTES = ['danceability', 
                       'energy', 
                       'speechiness', 
                       'acousticness', 
                       'instrumentalness', 
                       'liveness', 
                       'valence']

# Function takes in a file path to an XML file and returns two arrays, one with all the attribute values, and one 
# with all the track names
def read_all_audio_features(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    all_features = {}
    titles = {}  # To store the titles
    for track in root.findall('track'):
        track_id = track.find('id').text
        title = track.find('title').text if track.find('title') is not None else 'No Title'
        titles[track_id] = title  # Store the title
        features = {}
        for feature in track:
            if feature.tag in SELECTED_ATTRIBUTES and feature.text.replace('.', '', 1).isdigit():
                features[feature.tag] = float(feature.text)
        if features:
            all_features[track_id] = features
    return all_features, titles

# Function takes in a graph object and a file output name and directory, and it creates a html file of the graph
def draw_graph_with_pyvis(graph, filename='graph.html'):
    net = Network(height="750px", width="750px", bgcolor="#222222", font_color="white", select_menu=True)

    # for node, attr in graph.nodes(data=True):
    #     net.add_node(node, label=attr['label'])
    #
    # for edge in graph.edges.data():
    #     src, dst, weight = edge
    #     net.add_edge(src, dst, value=weight['weight'])

    net.from_nx(graph)

    # Save and open the graph
    net.show_buttons(filter_=['physics'])
    net.save_graph(filename)

# Function takes in a graph object and an output directory and name, and it creates a png of the graph
def draw_graph_with_matplotlib(graph, settings, filename='graph.png'):
    print("Computing layout...")
    plt.figure(figsize=settings["figsize"])  # Set the size of the plot
    pos = nx.spring_layout(graph, k=settings["k"], iterations=settings["iterations"])  # Compute node positions

    print("Drawing nodes...")
    nx.draw_networkx_nodes(graph, pos, node_size=settings["node_size"], node_color=settings["node_color"], alpha=0.7)

    print("Drawing edges...")
    # Get edge weights (similarities)
    weights = np.array([data['weight'] for _, _, data in graph.edges(data=True)])
    # Normalize weights to range between 0.05 and 0.2 for alpha (opacity)
    alpha_values = 0.05 + (weights - weights.min()) / (weights.max() - weights.min()) * 0.19
    # Normalize weights to range between 0.1 and 2 for line width
    linewidths = 0.1 + (weights - weights.min()) / (weights.max() - weights.min()) * 1.9

    # Use tqdm for progress bar
    edge_data = zip(graph.edges(data=True), alpha_values, linewidths)
    for (src, dst, data), alpha, linewidth in tqdm(edge_data, total=len(graph.edges), desc="Drawing Edges"):
        nx.draw_networkx_edges(graph, pos, edgelist=[(src, dst)], width=linewidth, edge_color='grey', alpha=alpha)

    print("Adding labels...")
    labels = nx.get_node_attributes(graph, 'label')
    nx.draw_networkx_labels(graph, pos, labels, font_size=6, font_color='black')

    plt.title('Song Similarity Graph', size=25)
    plt.axis('off')  # Turn off the axis

    print("Saving figure...")
    plt.savefig(filename, format='png', bbox_inches='tight', dpi=300)
    plt.close()  # Close the figure to free memory

# The following functions are used to compute the similarity between two tracks
def compute_similarity_pair(args):
    track_id1, track_id2, features1, features2, similarity_metric = args
    similarity = compute_similarity(features1, features2, similarity_metric)
    if similarity:
        return (track_id1, track_id2, {'weight': similarity})
    return None

def compute_similarity(features1, features2, similarity_metric='cosine'):
    # Intersection of keys (features present in both tracks)
    common_keys = features1.keys() & features2.keys()

    # If there are no common features, return None or some indication of non-comparability
    if not common_keys:
        return None

    vector1 = np.array([features1[key] for key in common_keys])
    vector2 = np.array([features2[key] for key in common_keys])

    if similarity_metric == 'euclidean':
        # Avoid division by zero in case vectors are identical
        distance = euclidean(vector1, vector2)
        similarity = 1 / (1 + distance) if distance != 0 else 1.0
    elif similarity_metric == 'cosine':
        similarity = 1 - cosine(vector1, vector2)
    else:
        raise ValueError("Invalid similarity metric. Choose 'euclidean' or 'cosine'.")

    return similarity

def create_similarity_graph_threshold(xml_file, similarity_metric='euclidean', threshold=None):
    all_features, titles = read_all_audio_features(xml_file)
    track_ids = list(all_features.keys())

    # Create all pairs of tracks
    pairs = [(track_id1, track_id2, all_features[track_id1], all_features[track_id2], similarity_metric)
             for track_id1, track_id2 in combinations(track_ids, 2)]

    G = nx.Graph()

    # Add nodes with titles as labels
    for track_id, title in titles.items():
        G.add_node(track_id, label=title)

    print("Calculating similarities...")
    edges = []
    with Pool(processes=4) as pool:  # Adjust the number of processes based on your machine
        for result in tqdm(pool.imap_unordered(compute_similarity_pair, pairs), total=len(pairs),
                           desc="Similarity Calculations"):
            if result and (threshold is None or result[2]['weight'] > threshold):
                edges.append(result)

    print("Adding edges...")
    G.add_edges_from(edges)  # Bulk addition of edges
    return G

# This function makes a graph with a set number of connections per node instead of a hard cutoff:
def create_similarity_graph_number(all_features, titles, top_n=10):
    G = nx.Graph()

    # Add nodes
    for track_id, title in titles.items():
        G.add_node(track_id, label=title)

    # Compute similarity for each pair and store in a dictionary
    similarity_dict = defaultdict(list)
    for track_id1, track_id2 in combinations(all_features.keys(), 2):
        similarity = compute_similarity(all_features[track_id1], all_features[track_id2])
        if similarity:
            similarity_dict[track_id1].append((track_id2, similarity))
            similarity_dict[track_id2].append((track_id1, similarity))

    # For each node, keep only the top N similarities
    for track_id, similarities in similarity_dict.items():
        top_similarities = sorted(similarities, key=lambda x: x[1], reverse=True)[:top_n]
        for neighbor_id, sim in top_similarities:
            G.add_edge(track_id, neighbor_id, weight=sim)

    return G