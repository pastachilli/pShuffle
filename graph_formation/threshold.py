import graph_functions as gf

xml_file = '../xml_files/playlist_5X13HtrTfhv5JpnTeMtL0D.xml'  # The XML file with the audio features
similarity_graph = gf.create_similarity_graph_bulk(xml_file, similarity_metric='cosine', threshold=0.985)

# draw_graph_with_pyvis(similarity_graph)
gf.draw_graph_with_matplotlib(similarity_graph)