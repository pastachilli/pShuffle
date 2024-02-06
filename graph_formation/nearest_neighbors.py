import graph_functions as gf

matplotlib_settings = {
    "figsize": (20, 20),
    "k": 8,
    "iterations": 400,
    "node_size": 300,
    "node_color": "skyblue"
}

number_of_neighbors = 20

xml_file = '../xml_files/playlist_5X13HtrTfhv5JpnTeMtL0D.xml'  # The XML file with the audio features
all_features, titles = gf.read_all_audio_features(xml_file)
similarity_graph = gf.create_similarity_graph_number(all_features, titles, number_of_neighbors)

gf.draw_graph_with_pyvis(similarity_graph, "../output/gabeMain.html")
# gf.draw_graph_with_matplotlib(similarity_graph, matplotlib_settings, filename="../output/beccaGraph.png")

print("Done!")