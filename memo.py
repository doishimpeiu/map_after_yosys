#! /usr/bin/python3
import networkx as nx
# networkxの使い方
G = nx.DiGraph()  # 有向グラフ (Directed Graph)

# # 頂点の追加
G.add_node(1, name = 1)                
G.add_nodes_from([3, 4, 5])

# # 辺の追加 (頂点も必要に応じて追加されます)
# G.add_edge(1, 2)                                    
# G.add_edges_from([(1, 3), (2, 5), (3, 4), (4, 5)])

# # 辺の削除
# G.remove_edge(3, 4)                    
# G.remove_edges_from([(1, 3), (2, 5)])

# # 頂点の削除 (削除された頂点に接続されている辺も削除されます)
# G.remove_node(5)
# G.remove_nodes_from([3, 4])

# # 指定したパス上の頂点と辺を追加
# nx.add_path(G, [1, 2, 3, 4, 5])  # 1 → 2 → 3 → 4 → 5

# # 指定した閉路上の頂点と辺を追加
# nx.add_cycle(G, [1, 2, 3, 4, 5])  # 1 → 2 → 3 → 4 → 5 → 1

# # 放射状に頂点と辺を追加
# nx.add_star(G, [1, 2, 3, 4, 5])  # 1 → 2, 1 → 3, 1 → 4, 1 → 5

nx.nx_agraph.view_pygraphviz(G, prog='fdp')  # pygraphvizが必要

# .D(_24656_),
