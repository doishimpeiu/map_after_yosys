#-*-coding:utf-8-*-
#! /usr/bin/python3
import networkx as nx
import re
import pprint
from find_specific_attribute_node import find_specific_attribute_node as find_nodes
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

##Verilogを一行づつ走査する関数
def scan_verilog():
  global vlines
  counter = 0
  splited_s = []
  ram_no = 0
  for line_no in range(len(vlines)):
    if re.search(r'\.D', vlines[line_no]):
      counter += 1
    ##ramの場合
    if re.search(r'^ *ram_.*$', vlines[line_no]):
      #まず, 空白を区切り文字としてリストに格納する
      splited_s.append((vlines[line_no].split(' ')))
      print(ram_no)
      #splited_s[ram_no][2]について
      print(splited_s[ram_no][2])
      # ram_w8_l2048_id9_3
      #頂点として追加
      G.add_node(splited_s[ram_no][2], name = splited_s[ram_no][2])
      # G.nodes[頂点][属性キー] = 属性値
      G.nodes[splited_s[ram_no][2]]['module'] = 'module' #属性としてmoduleを持たせる
      #splited_s[ram_no][3]について
      print(splited_s[ram_no][3])
      #inst_ram_w8_l2048_id9_3
      #頂点として追加
      G.add_node(splited_s[ram_no][3], name = splited_s[ram_no][3], IO = "in")
      #辺を追加
      G.add_edge(splited_s[ram_no][2], splited_s[ram_no][3])
      #splited_s[ram_no][6]について
      # print(splited_s[ram_no][6])
      #ram_w8_l2048_id9_3_0_addr
      str = re.sub(r'\.', '', splited_s[ram_no][6])
      str = re.sub(r'\(\w+\),', '', str)
      print(str)
      G.add_node(str, name = str, IO = "in")
      G.add_edge(str, splited_s[ram_no][2])
      #splited_s[ram_no][7]について
      # print(splited_s[ram_no][7])
      # ram_w8_l2048_id9_2_0_rdata
      str = re.sub(r'\.', '', splited_s[ram_no][7])
      str = re.sub(r'\(\w+\),', '', str)
      print(str)
      G.add_node(str, name = str, IO = "out")
      G.add_edge(splited_s[ram_no][2], str)
      #splited_s[ram_no][8]について
      # print(splited_s[ram_no][8])
      # ram_w8_l2048_id9_3_0_wdata
      str = re.sub(r'\.', '', splited_s[ram_no][8])
      if(re.sub(r'\(\d+\'\w+\),', '', str)):
        str = re.sub(r'\(\d+\'\w+\),', '', str)
      if(re.sub(r'\(\w+\),', '', str)):
        str = re.sub(r'\(\w+\),', '', str)
      print(str)
      G.add_node(str, name = str, IO = "in")
      G.add_edge(str, splited_s[ram_no][2])
      #splited_s[ram_no][9]について
      # print(splited_s[ram_no][9])
      # ram_w8_l2048_id9_3_0_wenable
      str = re.sub(r'\.', '', splited_s[ram_no][9])
      if(re.sub(r'\(\d+\'\w+\),', '', str)):
        str = re.sub(r'\(\d+\'\w+\),', '', str)
      if(re.sub(r'\(\w+\),', '', str)):
        str = re.sub(r'\(\w+\),', '', str)
      print(str)
      G.add_node(str, name = str, IO = "in")
      G.add_edge(str, splited_s[ram_no][2])
      #splited_s[ram_no][10]について
      # print(splited_s[ram_no][10])
      # ram_w8_l2048_id9_3_0_wenable
      str = re.sub(r'\.', '', splited_s[ram_no][10])
      if(re.sub(r'\(\d+\'\w+\),', '', str)):
        str = re.sub(r'\(\d+\'\w+\),', '', str)
      if(re.sub(r'\(\w+\),', '', str)):
        str = re.sub(r'\(\w+\),', '', str)
      print(str)
      G.add_node(str, name = str, IO = "in")
      G.add_edge(str, splited_s[ram_no][2])
      #splited_s[ram_no][11]について
      # print(splited_s[ram_no][11])
      # ram_w8_l2048_id9_3_1_rdata
      str = re.sub(r'\.', '', splited_s[ram_no][11])
      if(re.sub(r'\(\d+\'\w+\),', '', str)):
        str = re.sub(r'\(\d+\'\w+\),', '', str)
      if(re.sub(r'\(\w+\),', '', str)):
        str = re.sub(r'\(\w+\),', '', str)
      print(str)
      G.add_node(str, name = str, IO = "out")
      G.add_edge(splited_s[ram_no][2], str)
      #splited_s[ram_no][12]について
      # print(splited_s[ram_no][12])
      # ram_w8_l2048_id9_3_1_wdata
      str = re.sub(r'\.', '', splited_s[ram_no][12])
      if(re.sub(r'\(\d+\'\w+\),', '', str)):
        str = re.sub(r'\(\d+\'\w+\),', '', str)
      if(re.sub(r'\(\w+\),', '', str)):
        str = re.sub(r'\(\w+\),', '', str)
      print(str)
      G.add_node(str, name = str, IO = "in")
      G.add_edge(str, splited_s[ram_no][2])
      #splited_s[ram_no][13]について
      # print(splited_s[ram_no][13])
      # ram_w8_l2048_id9_3_1_wenable
      str = re.sub(r'\.', '', splited_s[ram_no][13])
      if(re.sub(r'\(\d+\'\w+\),', '', str)):
        str = re.sub(r'\(\d+\'\w+\),', '', str)
      if(re.sub(r'\(\d+\'\w+\)', '', str)):
        str = re.sub(r'\(\d+\'\w+\)', '', str)
      if(re.sub(r'\(\w+\),', '', str)):
        str = re.sub(r'\(\w+\),', '', str)
      if(re.sub(r'\(\w+\)', '', str)):
        str = re.sub(r'\(\w+\)', '', str)
      print(str)
      G.add_node(str, name = str, IO = "in")
      G.add_edge(str, splited_s[ram_no][2])
      ram_no += 1
  # print(splited_s[119])
  print(counter)

# ram_w8_l2048_id9_3 inst_ram_w8_l2048_id9_3 ( .CLK(CLK), .ram_w8_l2048_id9_3_0_addr(ram_w8_l2048_id9_3_0_addr), .ram_w8_l2048_id9_3_0_rdata(ram_w8_l2048_id9_3_0_rdata), .ram_w8_l2048_id9_3_0_wdata(8'h00), .ram_w8_l2048_id9_3_0_wenable(1'h0), .ram_w8_l2048_id9_3_1_addr(ram_w8_l2048_id9_3_1_addr), .ram_w8_l2048_id9_3_1_rdata(ram_w8_l2048_id9_3_1_rdata), .ram_w8_l2048_id9_3_1_wdata(ram_w8_l2048_id9_3_1_wdata), .ram_w8_l2048_id9_3_1_wenable(ram_w8_l2048_id9_3_1_wenable) );
  # input CLK,
  # input [9-1:0] ram_w8_l2048_id9_3_0_addr,
  # output [8-1:0] ram_w8_l2048_id9_3_0_rdata,
  # input [8-1:0] ram_w8_l2048_id9_3_0_wdata,
  # input ram_w8_l2048_id9_3_0_wenable,
  # input [9-1:0] ram_w8_l2048_id9_3_1_addr,
  # output [8-1:0] ram_w8_l2048_id9_3_1_rdata,
  # input [8-1:0] ram_w8_l2048_id9_3_1_wdata,
  # input ram_w8_l2048_id9_3_1_wenable


## Verilogファイル(presynthesis_sdff.vを読み込む)
path = '/Users/doishinpei/workspace/map_after_yosys/presynthesis_sdff.v'
with open(path) as f:
  vlines = [s.replace('\n', '') for s in f.readlines()]

G = nx.DiGraph()  # 有向グラフ (Directed Graph)

### Verilogファイルを走査する
scan_verilog()

data_list = []
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# len = 30192
# i = 1
# while i <= len:
#   line = f.readline()
#   #readlineの末尾の\nをとる
#   line = line.replace("\n", "")
#   if line:
#     # print(i, ":", line)
#     data_list.append(line)
#     i += 1
#   else:
#     break

# pprint.pprint(data_list)
# data_list.pop(0)
# data_list.pop(0)
# print("hosi")
# pprint.pprint(data_list)
# print(data_list[-1])

# #取り出したものをスペースで区切ってリストの最後番目の値だけ取り出す
# non_space = re.split('\s', data_list[-1])
# print(non_space)
# print(non_space[-1])
# last = non_space[-1]
# print(last)
# sub = re.sub(r";", "", last)
# print(sub)

# data_list_list = []
# for i in range (len(data_list)):
#   triming = re.sub(r"\.b\(|\)\,", "", data_lists_b[i])
#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

nx.nx_agraph.view_pygraphviz(G, prog='fdp')  # pygraphvizが必要

pprint.pprint(find_nodes(G, 'IO', 'out'))

