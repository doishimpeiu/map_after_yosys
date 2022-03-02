import networkx as nx

#特定の属性をもつノードを検索
#https://qiita.com/hitsumabushi845/items/5e425457abc64591886c
# #引数は以下の3つです．
# G : 検索対象となるグラフ
# attr : 検索したい属性名
# value : 見つけたいattrの値
# 返り値は見つかったノード名のリストです．
def find_specific_attribute_node(G, attr, value):

    result = []

    d = nx.get_node_attributes(G, attr)

    for key, v in d.items():
        if(v == value):
            result.append(key)

    return result