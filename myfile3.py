#-*-coding:utf-8-*-
#! /usr/bin/python3
import networkx as nx
import re
import pprint

from networkx.algorithms.centrality.group import prominent_group
from find_specific_attribute_node import find_specific_attribute_node as find_nodes
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

#グローバル変数を宣言する
g = nx.DiGraph()  # 有向グラフ (Directed Graph)
vlines = []

#scan_verilog関数
def scan_verilog():
  global vlines
  num_identify = 0
  for line_no in range(len(vlines)):
    ### input文（バスの場合）
    if re.search(r'^ *input *\[[0-9]+:[0-9]+\] ',vlines[line_no]):
      # print(line_no)
      # print(vlines[line_no])
      #整形する
      imax = int(re.sub(r'^ *input *\[([0-9]+):([0-9]+)\] *([^ ]+) *;.*$','\\1',vlines[line_no]))
      imin = int(re.sub(r'^ *input *\[([0-9]+):([0-9]+)\] *([^ ]+) *;.*$','\\2',vlines[line_no]))
      name = re.sub(r'^ *input *\[([0-9]+):([0-9]+)\] *([^ ]+) *;.*$','\\3',vlines[line_no])
      # print(imax)
      # print(imin)
      # print(name)
      #頂点として追加
      g.add_node(name, name = name, imax = imax, imin = imin, kind = "input")
    ### input文（バスでない場合）
    elif re.search(r'^ *input ',vlines[line_no]):
      # print(line_no)
      # print(vlines[line_no])
      #整形する
      imax = 0
      imin = 0
      name = re.sub(r'^ *input +([^ ]+) *;.*$','\\1',vlines[line_no])
      # print(imax)
      # print(imin)
      # print(name)
      #頂点として追加
      g.add_node(name, name = name, imax = imax, imin = imin, kind = "input")
    ### output文（バスの場合）
    elif re.search(r'^ *output *\[[0-9]+:[0-9]+\] ',vlines[line_no]):
      # print(line_no)
      # print(vlines[line_no])
      #整形する
      imax = int(re.sub(r'^ *output *\[([0-9]+):([0-9]+)\] *([^ ]+) *;.*$','\\1',vlines[line_no]))
      imin = int(re.sub(r'^ *output *\[([0-9]+):([0-9]+)\] *([^ ]+) *;.*$','\\2',vlines[line_no]))
      name = re.sub(r'^ *output *\[([0-9]+):([0-9]+)\] *([^ ]+) *;.*$','\\3',vlines[line_no])
      #頂点として追加
      g.add_node(name, name = name, imax = imax, imin = imin, kind = "output")
    ### output文（バスでない場合）
    elif re.search(r'^ *output ',vlines[line_no]):
      # print(line_no)
      # print(vlines[line_no])
      #整形する
      imax = 0
      imin = 0
      name = re.sub(r'^ *output +([^ ]+) *;.*$','\\1',vlines[line_no])
      #頂点として追加
      g.add_node(name, name = name, imax = imax, imin = imin, kind = "output")
    ### wire文（バスの場合）
    elif re.search(r'^ *wire *\[[0-9]+:[0-9]+\] ',vlines[line_no]):
      # print(line_no)
      # print(vlines[line_no])
      #整形する
      imax = int(re.sub(r'^ *wire *\[([0-9]+):([0-9]+)\] *([^ ]+) *;.*$','\\1',vlines[line_no]))
      imin = int(re.sub(r'^ *wire *\[([0-9]+):([0-9]+)\] *([^ ]+) *;.*$','\\2',vlines[line_no]))
      name = re.sub(r'^ *wire *\[([0-9]+):([0-9]+)\] *([^ ]+) *;.*$','\\3',vlines[line_no])
      if re.search(r'\\', name):
        # print("ここ")
        # print(name)
        # input()
        name = re.sub(r'\\', '', name)
        name = name.replace(' ', '')
        # print(name)
        # input()
      #頂点として追加
      g.add_node(name, name = name, imax = imax, imin = imin, kind = "wire")
    ### wire文（バスでない場合）
    elif re.search(r'^ *wire ',vlines[line_no]):
      # print(line_no)
      # print(vlines[line_no])
      #整形する
      imax = 0
      imin = 0
      name = re.sub(r'^ *wire +([^ ]+) *;.*$','\\1',vlines[line_no])
      #頂点として追加
      g.add_node(name, name = name, imax = imax, imin = imin, kind = "wire")
      # g.nodes[name]['width'] = (7,31) 
      # del g.nodes[name]['width']
    
    ### assign文
    if re.search(r'^ *assign +[^=]+ *= *[^;]+;.*$',vlines[line_no]):
      # print('line_no:{0}'.format(line_no))
      # print(vlines[line_no])
      lhs = re.sub(r'^ *assign +([^=]+) *= *([^;]+);.*$','\\1',vlines[line_no]).strip()
      rhs = re.sub(r'^ *assign +([^=]+) *= *([^;]+);.*$','\\2',vlines[line_no]).strip()
      # print(rhs)
      #assignの右辺に{}がついている場合
      if re.search(r'\{|\}', rhs):
        rhs = re.sub(r'\{|\}', '', rhs)
        # print("ここを見る2")
        # print(rhs)
      #assignの右辺に[:]がついている場合
      if re.search(r'\[\d+:\d+\]', rhs):
        rhs = re.sub(r'\[\d+:\d+\]', '', rhs)
      # print("ここを見る")
      # print(rhs)
      # print(type(rhs))
      rhs = rhs.replace(' ', '')
      rhs = rhs.replace('{', '')
      rhs = re.sub(r'\[\d+\]', '', rhs)
      rhs = rhs.split(',')
      # print(rhs)
      # print(type(rhs))
      #lhsから[1:0]をとる
      lhs = re.sub(r'\[\d+:\d+\]', '',  lhs)
      if re.search(r'\[\d+\]',  lhs):
        lhs = re.sub(r'\[\d+\]', '',  lhs)
      # print(lhs)
      #g.add_edge(rhs, lhs)
      for rnode in rhs:
        # print("forの中")
        #   input()
        if rnode != lhs:
          # print("ifの中")
          # print(rnode)
          # print(lhs)
          if re.match(r'\d+', rnode) or re.match(r'\d+\'\d+', rnode):
            # print(rnode)
            # print(lhs)
            g.add_node(num_identify, name = num_identify, num = rnode, kind = "num")
            g.add_edge(num_identify, lhs)
            num_identify = num_identify + 1
          else:
            g.add_edge(rnode, lhs)
      # print(nx.ancestors(g, lhs))
      # print(list(g.in_edges(lhs)))
      # input()
    ### \$lut
    elif re.search(r'^ *\\\$lut.*$',vlines[line_no]):
      # print('line_no:{0}'.format(line_no))
      # print(vlines[line_no])
      port_LUT = re.sub(r'^ *\\\$lut.*\.LUT\((.*)\), .*\.A(.*)$','\\1',vlines[line_no])
      # print(port_LUT)
      port_WIDTH = int(re.sub(r'^ *\\\$lut.*\.WIDTH\((.*)\) \) .*\.A(.*)$','\\1',vlines[line_no]))
      # print(type(port_WIDTH))
      # print(port_WIDTH)
      lut_name = re.search(r'\s_\d+_\s',vlines[line_no]).group()
      lut_name = lut_name.replace(' ', '')
      # print(lut_name)
      g.add_node(lut_name, name = lut_name, LUT = port_LUT, WIDTH = port_WIDTH, kind = "lut")
      port_A = re.sub(r'^ *\\\$lut.*\.LUT\((.*)\), .*\.A\((.*)\),\s\..*$','\\2',vlines[line_no])
      # print(port_A)
      # print(type(port_A))
      port_A = re.sub(r'\{|\}', '', port_A)
      # print(port_A)
      port_A = port_A.replace(' ', '')
      port_A = port_A.split(',')
      # print(port_A)
      for rnode in port_A:
        if re.search(r'\[.*\]', rnode):
          # print("異常あり")
          # print(rnode)
          rnode = re.sub(r'\[.*\]', '', rnode)
        if re.match(r'\d+', rnode) or re.match(r'\d+\'\d+', rnode):
          # print(rnode)
          # print(lhs)
          g.add_node(num_identify, name = num_identify, num = rnode, kind = "num")
          g.add_edge(num_identify, lut_name)
          num_identify = num_identify + 1
        else:
          g.add_edge(rnode, lut_name)
        #   print(rnode)
        # print(rnode)
        # print("つないだ")
        # print(list(g.in_edges(lut_name)))
        # input()
      port_Y = re.sub(r'^ *\\\$lut.*\.LUT\((.*)\), .*\.Y\((.*)\)\s\);$','\\2',vlines[line_no])
      # print(port_Y)
      g.add_edge(lut_name, port_Y)
      # print("つないだ")
      # print(list(g.in_edges(port_Y)))
      # input()
    ### \$add 
    elif re.search(r'^ *\\\$add.*$',vlines[line_no]):
      # print('line_no:{0}'.format(line_no))
      # print(vlines[line_no])
      A_SIGNED = re.sub(r'^ *\\\$add.*\.A_SIGNED\((\d)\), .*\.A_WIDTH(.*)$','\\1',vlines[line_no])
      # print(A_SIGNED)
      A_WIDTH = re.sub(r'^ *\\\$add.*\.A_SIGNED\((\d)\), .*\.A_WIDTH\((\d+)\), .*$','\\2',vlines[line_no])
      # print(A_WIDTH)
      B_SIGNED = re.sub(r'^ *\\\$add.*\.B_SIGNED\((\d)\), .*\.B_WIDTH(.*)$','\\1',vlines[line_no])
      # print(B_SIGNED)
      B_WIDTH = re.sub(r'^ *\\\$add.*\.B_SIGNED\((\d)\), .*\.B_WIDTH\((\d+)\), .*$','\\2',vlines[line_no])
      # print(B_WIDTH)
      Y_WIDTH = re.sub(r'^ *\\\$add.*\.Y_WIDTH\((\d+)\) .*$','\\1',vlines[line_no])
      # print(Y_WIDTH)
      add_name = re.search(r'\s_\d+_\s',vlines[line_no]).group()
      add_name = add_name.replace(' ', '')
      # print(add_name)
      g.add_node(add_name, name = add_name, A_SIGNED = A_SIGNED, A_WIDTH = A_WIDTH, B_SIGNED = B_SIGNED, B_WIDTH = B_WIDTH, Y_WIDTH = Y_WIDTH, kind = "add")
      port_A = re.sub(r'^ *\\\$add.*\.A\((.*)\), \.B\((.*)\), \.Y\((.*)\) \);$','\\1',vlines[line_no])
      port_A = re.sub(r'\\', '', port_A)
      port_A = port_A.replace(' ', '')
      #複数入力
      # print("入力A")
      # print(port_A)
      if re.search(r'\{|\}', port_A):
        # print("複数入力")
        port_A = re.sub(r'\{|\}', '', port_A)
        # print(port_A)
        port_A = port_A.replace(' ', '')
        port_A = port_A.split(',')
        for rnode in port_A:
          if re.search(r'\[.*\]', rnode):
            # print("異常あり")
            # print(rnode)
            rnode = re.sub(r'\[.*\]', '', rnode)
          #   print(rnode)
          # print("rnode")
          # print(rnode)
          if re.match(r'\d+', rnode) or re.match(r'\d+\'\d+', rnode):
            # print(rnode)
            # print(lhs)
            g.add_node(num_identify, name = num_identify, num = rnode, kind = "num")
            g.add_edge(num_identify, add_name)
            num_identify = num_identify + 1
          else:
            g.add_edge(rnode, add_name)
          # print("つないだ")
          # print(list(g.in_edges(lut_name)))
          # input()
      #単数入力 
      elif re.search(r'\[.*\]', port_A):
        port_A = re.sub(r'\[.*\]', '', port_A)
        if re.match(r'\d+', port_A) or re.match(r'\d+\'\d+', port_A):
          # print(rnode)
          # print(lhs)
          g.add_node(num_identify, name = num_identify, num = port_A, kind = "num")
          g.add_edge(num_identify, add_name)
          num_identify = num_identify + 1
        else:
          g.add_edge(port_A, add_name)
      # print(list(g.in_edges(add_name)))
      port_B = re.sub(r'^ *\\\$add.*\.A\((.*)\), \.B\((.*)\), \.Y\((.*)\) \);$','\\2',vlines[line_no])
      port_B = re.sub(r'\\', '', port_B)
      port_B = port_B.replace(' ', '')
      # print("入力B")
      # print(port_B)
      #複数入力
      if re.search(r'\{|\}', port_B):
        # print("複数入力")
        port_B = re.sub(r'\{|\}', '', port_B)
        # print(port_B)
        port_B = port_B.replace(' ', '')
        port_B = port_B.split(',')
        for rnode in port_B:
          if re.search(r'\[.*\]', rnode):
            # print("異常あり")
            # print(rnode)
            rnode = re.sub(r'\[.*\]', '', rnode)
          #   print(rnode)
          # print("rnode")
          # print(rnode)
          if re.match(r'\d+', rnode) or re.match(r'\d+\'\d+', rnode):
            # print(rnode)
            # print(lhs)
            g.add_node(num_identify, name = num_identify, num = rnode, kind = "num")
            g.add_edge(num_identify, add_name)
            num_identify = num_identify + 1
          else:
            g.add_edge(rnode, add_name)
          # print("つないだ")
          # print(list(g.in_edges(lut_name)))
          # input()
      #単数入力
      elif re.search(r'\[.*\]', port_B):
        port_B = re.sub(r'\[.*\]', '', port_B)
        if re.match(r'\d+', port_B) or re.match(r'\d+\'\d+', port_B):
            # print(rnode)
            # print(lhs)
            g.add_node(num_identify, name = num_identify, num = port_B, kind = "num")
            g.add_edge(num_identify, add_name)
            num_identify = num_identify + 1
        else:
          g.add_edge(port_B, add_name)
      else:
        if re.match(r'\d+', port_B) or re.match(r'\d+\'\d+', port_B):
            # print(rnode)
            # print(lhs)
            g.add_node(num_identify, name = num_identify, num = port_B, kind = "num")
            g.add_edge(num_identify, add_name)
            num_identify = num_identify + 1
        else:
          g.add_edge(port_B, add_name)
      # print(list(g.in_edges(add_name)))
      port_Y = re.sub(r'^ *\\\$add.*\.A\((.*)\), \.B\((.*)\), \.Y\((.*)\) \);$','\\3',vlines[line_no])
      port_Y = re.sub(r'\\', '', port_Y)
      port_Y = port_Y.replace(' ', '')
      # print("出力Y")
      # print(port_Y)
      # print(type(port_A))
      if re.search(r'\{|\}',port_Y):
        # print("複数出力")
        port_Y = re.sub(r'\{|\}', '', port_Y)
        port_Y = port_Y.replace(' ', '')
        port_Y = port_Y.split(',')
        # print(port_Y)
        for ynode in port_Y:
          if re.search(r'\[.*\]', ynode):
            # print("異常あり")
            # print(rnode)
            ynode = re.sub(r'\[.*\]', '', ynode)
          # print(rnode)
          # print(rnode)
          g.add_edge(add_name, ynode)
          # print("つないだ")
          # print(list(g.in_edges(ynode)))
          # input()
      else:
        # print("単数出力")
        if re.search(r'\[.*\]', port_Y):
            # print("異常あり")
            # print(rnode)
            port_Y = re.sub(r'\[.*\]', '', port_Y)
        g.add_edge(add_name, port_Y)
        # print("つないだ")
        # print(list(g.in_edges(port_Y)))
      # input()
      # print(port_LUT)
    ###\$sub
    elif re.search(r'^ *\\\$sub.*$',vlines[line_no]):
      # print('line_no:{0}'.format(line_no))
      # print(vlines[line_no])
      A_SIGNED = re.sub(r'^ *\\\$sub.*\.A_SIGNED\((\d)\), .*\.A_WIDTH(.*)$','\\1',vlines[line_no])
      # print(A_SIGNED)
      A_WIDTH = re.sub(r'^ *\\\$sub.*\.A_SIGNED\((\d)\), .*\.A_WIDTH\((\d+)\), .*$','\\2',vlines[line_no])
      # print(A_WIDTH)
      B_SIGNED = re.sub(r'^ *\\\$sub.*\.B_SIGNED\((\d)\), .*\.B_WIDTH(.*)$','\\1',vlines[line_no])
      # print(B_SIGNED)
      B_WIDTH = re.sub(r'^ *\\\$sub.*\.B_SIGNED\((\d)\), .*\.B_WIDTH\((\d+)\), .*$','\\2',vlines[line_no])
      # print(B_WIDTH)
      Y_WIDTH = re.sub(r'^ *\\\$sub.*\.Y_WIDTH\((\d+)\) .*$','\\1',vlines[line_no])
      # print(Y_WIDTH)
      sub_name = re.search(r'\s_\d+_\s',vlines[line_no]).group()
      sub_name = sub_name.replace(' ', '')
      # print(sub_name)
      g.add_node(sub_name, name = sub_name, A_SIGNED = A_SIGNED, A_WIDTH = A_WIDTH, B_SIGNED = B_SIGNED, B_WIDTH = B_WIDTH, Y_WIDTH = Y_WIDTH, kind = "sub")
      port_A = re.sub(r'^ *\\\$sub.*\.A\((.*)\), \.B\((.*)\), \.Y\((.*)\) \);$','\\1',vlines[line_no])
      #複数入力
      # print("入力A")
      # print(port_A)
      if re.search(r'\{|\}', port_A):
        # print("複数入力")
        port_A = re.sub(r'\{|\}', '', port_A)
        # print(port_A)
        port_A = port_A.replace(' ', '')
        port_A = port_A.split(',')
        for rnode in port_A:
          if re.search(r'\[.*\]', rnode):
            # print("異常あり")
            # print(rnode)
            rnode = re.sub(r'\[.*\]', '', rnode)
          #   print(rnode)
          # print("rnode")
          # print(rnode)
          if re.match(r'\d+', rnode) or re.match(r'\d+\'\d+', rnode):
            # print(rnode)
            # print(lhs)
            g.add_node(num_identify, name = num_identify, num = rnode, kind = "num")
            g.add_edge(num_identify, sub_name)
            num_identify = num_identify + 1
          else:
            g.add_edge(rnode, sub_name)
          # print("つないだ")
          # print(list(g.in_edges(lut_name)))
          # input()
      #単数入力 
      elif re.search(r'\[.*\]', port_A):
        port_A = re.sub(r'\[.*\]', '', port_A)
        if re.match(r'\d+', port_A) or re.match(r'\d+\'\d+', port_A):
          # print(rnode)
          # print(lhs)
          g.add_node(num_identify, name = num_identify, num = port_A, kind = "num")
          g.add_edge(num_identify, sub_name)
          num_identify = num_identify + 1
        else:
          g.add_edge(port_A, sub_name)
      else: 
        if re.match(r'\d+', port_A) or re.match(r'\d+\'\d+', port_A):
            # print(rnode)
            # print(lhs)
            g.add_node(num_identify, name = num_identify, num = port_A, kind = "num")
            g.add_edge(num_identify, sub_name)
            num_identify = num_identify + 1
        else:
          g.add_edge(port_A, sub_name)
      # print(list(g.in_edges(sub_name)))
      port_B = re.sub(r'^ *\\\$sub.*\.A\((.*)\), \.B\((.*)\), \.Y\((.*)\) \);$','\\2',vlines[line_no])
      # print("入力B")
      # print(port_B)
      #複数入力
      if re.search(r'\{|\}', port_B):
        # print("複数入力")
        port_B = re.sub(r'\{|\}', '', port_B)
        # print(port_B)
        port_B = port_B.replace(' ', '')
        port_B = port_B.split(',')
        for rnode in port_B:
          if re.search(r'\[.*\]', rnode):
            # print("異常あり")
            # print(rnode)
            rnode = re.sub(r'\[.*\]', '', rnode)
          #   print(rnode)
          # print("rnode")
          # print(rnode)
          if re.match(r'\d+', rnode) or re.match(r'\d+\'\d+', rnode):
            # print(rnode)
            # print(lhs)
            g.add_node(num_identify, name = num_identify, num = rnode, kind = "num")
            g.add_edge(num_identify, sub_name)
            num_identify = num_identify + 1
          else:
            g.add_edge(rnode, sub_name)
          # print("つないだ")
          # print(list(g.in_edges(lut_name)))
          # input()
      #単数入力
      elif re.search(r'\[.*\]', port_B):
        port_B = re.sub(r'\[.*\]', '', port_B)
        if re.match(r'\d+', port_B) or re.match(r'\d+\'\d+', port_B):
            # print(rnode)
            # print(lhs)
            g.add_node(num_identify, name = num_identify, num = port_B, kind = "num")
            g.add_edge(num_identify, sub_name)
            num_identify = num_identify + 1
        else:
          g.add_edge(port_B, sub_name)
      else:
        if re.match(r'\d+', port_B) or re.match(r'\d+\'\d+', port_B):
            # print(rnode)
            # print(lhs)
            g.add_node(num_identify, name = num_identify, num = port_B, kind = "num")
            g.add_edge(num_identify, sub_name)
            num_identify = num_identify + 1
        else:
          g.add_edge(port_B, sub_name)
      # print(list(g.in_edges(sub_name)))
      port_Y = re.sub(r'^ *\\\$sub.*\.A\((.*)\), \.B\((.*)\), \.Y\((.*)\) \);$','\\3',vlines[line_no])
      # print("出力Y")
      # print(port_Y)
      # print(type(port_A))
      if re.search(r'\{|\}',port_Y):
        # print("複数出力")
        port_Y = re.sub(r'\{|\}', '', port_Y)
        port_Y = port_Y.replace(' ', '')
        port_Y = port_Y.split(',')
        # print(port_Y)
        for ynode in port_Y:
          if re.search(r'\[.*\]', ynode):
            # print("異常あり")
            # print(rnode)
            ynode = re.sub(r'\[.*\]', '', ynode)
          # print(rnode)
          # print(rnode)
          g.add_edge(sub_name, ynode)
          # print("つないだ")
          # print(list(g.in_edges(ynode)))
          # input()
      else:
        # print("単数出力")
        if re.search(r'\[.*\]', port_Y):
            # print("異常あり")
            # print(rnode)
            port_Y = re.sub(r'\[.*\]', '', port_Y)
        g.add_edge(sub_name, port_Y)
        # print("つないだ")
        # print(list(g.in_edges(port_Y)))
      # input()
      # print(port_LUT)
    ###mul###########################################################
    elif re.search(r'^ *\\\$mul.*$',vlines[line_no]):
      # print('line_no:{0}'.format(line_no))
      # print(vlines[line_no])
      A_SIGNED = re.sub(r'^ *\\\$mul.*\.A_SIGNED\((\d)\), .*\.A_WIDTH(.*)$','\\1',vlines[line_no])
      # print(A_SIGNED)
      A_WIDTH = re.sub(r'^ *\\\$mul.*\.A_SIGNED\((\d)\), .*\.A_WIDTH\((\d+)\), .*$','\\2',vlines[line_no])
      # print(A_WIDTH)
      B_SIGNED = re.sub(r'^ *\\\$mul.*\.B_SIGNED\((\d)\), .*\.B_WIDTH(.*)$','\\1',vlines[line_no])
      # print(B_SIGNED)
      B_WIDTH = re.sub(r'^ *\\\$mul.*\.B_SIGNED\((\d)\), .*\.B_WIDTH\((\d+)\), .*$','\\2',vlines[line_no])
      # print(B_WIDTH)
      Y_WIDTH = re.sub(r'^ *\\\$mul.*\.Y_WIDTH\((\d+)\) .*$','\\1',vlines[line_no])
      # print(Y_WIDTH)
      mul_name = re.search(r'\s_\d+_\s',vlines[line_no]).group()
      mul_name = mul_name.replace(' ', '')
      g.add_node(mul_name, name = mul_name, A_SIGNED = A_SIGNED, A_WIDTH = A_WIDTH, B_SIGNED = B_SIGNED, B_WIDTH = B_WIDTH, Y_WIDTH = Y_WIDTH, kind = "mul")
      port_A = re.sub(r'^ *\\\$mul.*\.A\((.*)\), \.B\((.*)\), \.Y\((.*)\) \);$','\\1',vlines[line_no])
      port_A = re.sub(r'\\', '', port_A)
      port_A = port_A.replace(' ', '')
      #複数入力
      # print("入力A")
      # print(port_A)
      if re.search(r'\{|\}', port_A):
        # print("複数入力")
        port_A = re.sub(r'\{|\}', '', port_A)
        # print(port_A)
        port_A = port_A.replace(' ', '')
        port_A = port_A.split(',')
        for rnode in port_A:
          if re.search(r'\[.*\]', rnode):
            # print("異常あり")
            # print(rnode)
            rnode = re.sub(r'\[.*\]', '', rnode)
          #   print(rnode)
          # print("rnode")
          # print(rnode)
          if re.match(r'\d+', rnode) or re.match(r'\d+\'\d+', rnode):
            # print(rnode)
            # print(lhs)
            g.add_node(num_identify, name = num_identify, num = rnode, kind = "num")
            g.add_edge(num_identify, mul_name)
            num_identify = num_identify + 1
          else:
            g.add_edge(rnode, mul_name)
          # print("つないだ")
          # print(list(g.in_edges(lut_name)))
          # input()
      #単数入力 
      elif re.search(r'\[.*\]', port_A):
        port_A = re.sub(r'\[.*\]', '', port_A)
        port_A = re.sub(r'\{|\}', '', port_A)
        if re.search(r'\\', port_A):
          print(port_A)
          port_A = re.sub(r'\\', '', port_A)
          print(port_A)
          input()
        if re.match(r'\d+', port_A) or re.match(r'\d+\'\d+', port_A):
          # print(rnode)
          # print(lhs)
          g.add_node(num_identify, name = num_identify, num = port_A, kind = "num")
          g.add_edge(num_identify, mul_name)
          num_identify = num_identify + 1
        else:
          g.add_edge(port_A, mul_name)
      else:
        if re.match(r'\d+', port_A) or re.match(r'\d+\'\d+', port_A):
          # print(rnode)
          # print(lhs)
          g.add_node(num_identify, name = num_identify, num = port_A, kind = "num")
          g.add_edge(num_identify, mul_name)
          num_identify = num_identify + 1
        else:
          g.add_edge(port_A, mul_name)
      # print(list(g.in_edges(mul_name)))
      port_B = re.sub(r'^ *\\\$mul.*\.A\((.*)\), \.B\((.*)\), \.Y\((.*)\) \);$','\\2',vlines[line_no])
      port_B = re.sub(r'\\', '', port_B)
      port_B = port_B.replace(' ', '')
      # print("入力B")
      # print(port_B)
      #複数入力
      if re.search(r'\{|\}', port_B):
        # print("複数入力")
        port_B = re.sub(r'\{|\}', '', port_B)
        # print(port_B)
        port_B = port_B.replace(' ', '')
        port_B = port_B.split(',')
        for rnode in port_B:
          if re.search(r'\[.*\]', rnode):
            # print("異常あり")
            # print(rnode)
            rnode = re.sub(r'\[.*\]', '', rnode)
          #   print(rnode)
          # print("rnode")
          # print(rnode)
          if re.match(r'\d+', rnode) or re.match(r'\d+\'\d+', rnode):
            # print(rnode)
            # print(lhs)
            g.add_node(num_identify, name = num_identify, num = rnode, kind = "num")
            g.add_edge(num_identify, mul_name)
            num_identify = num_identify + 1
          else:
            g.add_edge(rnode, mul_name)
          # print("つないだ")
          # print(list(g.in_edges(mul_name)))
          # input()
      #単数入力
      elif re.search(r'\[.*\]', port_B):
        port_B = re.sub(r'\[.*\]', '', port_B)
        if re.match(r'\d+', port_B) or re.match(r'\d+\'\d+', port_B):
          # print(rnode)
          # print(lhs)
          g.add_node(num_identify, name = num_identify, num = port_B, kind = "num")
          g.add_edge(num_identify, mul_name)
          num_identify = num_identify + 1
        else:
          g.add_edge(port_B, mul_name)
      else:
        if re.match(r'\d+', port_B) or re.match(r'\d+\'\d+', port_B):
          # print(rnode)
          # print(lhs)
          g.add_node(num_identify, name = num_identify, num = port_B, kind = "num")
          g.add_edge(num_identify, mul_name)
          num_identify = num_identify + 1
        else:
          g.add_edge(port_B, mul_name)
      # print(list(g.in_edges(mul_name)))
      port_Y = re.sub(r'^ *\\\$mul.*\.A\((.*)\), \.B\((.*)\), \.Y\((.*)\) \);$','\\3',vlines[line_no])
      port_Y = re.sub(r'\\', '', port_Y)
      port_Y = port_Y.replace(' ', '')
      # print("出力Y")
      # print(port_Y)
      # print(type(port_A))
      if re.search(r'\{|\}',port_Y):
        # print("複数出力")
        port_Y = re.sub(r'\{|\}', '', port_Y)
        port_Y = port_Y.replace(' ', '')
        port_Y = port_Y.split(',')
        # print(port_Y)
        for ynode in port_Y:
          if re.search(r'\[.*\]', ynode):
            # print("異常あり")
            # print(rnode)
            ynode = re.sub(r'\[.*\]', '', ynode)
          # print(rnode)
          # print(rnode)
          g.add_edge(mul_name, ynode)
          # print("つないだ")
          # print(list(g.in_edges(ynode)))
          # input()
      else:
        # print("単数出力")
        if re.search(r'\[.*\]', port_Y):
            # print("異常あり")
            # print(rnode)
            port_Y = re.sub(r'\[.*\]', '', port_Y)
        g.add_edge(mul_name, port_Y)
        # print("つないだ")
        # print(list(g.in_edges(port_Y)))
      # input()
      # print(port_LUT)
    #  mux  ###############################################################
    elif re.search(r'^ *\\\$mux.*$',vlines[line_no]):
      # print('line_no:{0}'.format(line_no))
      # print(vlines[line_no])
      WIDTH = re.sub(r'^ *\\\$mux.*\.WIDTH\((\d+)\) .*$','\\1',vlines[line_no])
      # print("WIDTH")
      # print(WIDTH)
      mux_name = re.search(r'\s_\d+_\s',vlines[line_no]).group()
      mux_name = mux_name.replace(' ', '')
      # print("mux_name")
      # print(mux_name)
      g.add_node(mux_name, name = mux_name, WIDTH = WIDTH, kind = "mux")
      port_A = re.sub(r'^ *\\\$mux.*\.A\((.*)\), \.B\((.*)\), \.S\((.*)\), \.Y\((.*)\) \);$','\\1',vlines[line_no])
      #複数入力
      # print("入力A")
      # print(port_A)
      if re.search(r'\{|\}', port_A):
        # print("複数入力")
        port_A = re.sub(r'\{|\}', '', port_A)
        # print(port_A)
        port_A = port_A.replace(' ', '')
        port_A = port_A.split(',')
        for rnode in port_A:
          if re.search(r'\[.*\]', rnode):
            # print("異常あり")
            # print(rnode)
            rnode = re.sub(r'\[.*\]', '', rnode)
          #   print(rnode)
          # print("rnode")
          # print(rnode)
          if re.match(r'\d+', rnode) or re.match(r'\d+\'\d+', rnode) or re.match(r'-\d+', rnode):
            # print(rnode)
            # print(lhs)
            g.add_node(num_identify, name = num_identify, num = rnode, kind = "num")
            g.add_edge(num_identify, mux_name)
            num_identify = num_identify + 1
          else:
            g.add_edge(rnode, mux_name)
          # print("つないだ")
          # print(list(g.in_edges(mux_name)))
      #単数入力 
      elif re.search(r'\[.*\]', port_A):
        port_A = re.sub(r'\[.*\]', '', port_A)
        if re.match(r'\d+', port_A) or re.match(r'\d+\'\d+', port_A) or re.match(r'-\d+', port_A):
          # print(rnode)
          # print(lhs)
          g.add_node(num_identify, name = num_identify, num = port_A, kind = "num")
          g.add_edge(num_identify, mux_name)
          num_identify = num_identify + 1
        else:
          g.add_edge(port_A, mux_name)
      else:
        if re.match(r'\d+', port_A) or re.match(r'\d+\'\d+', port_A)  or re.match(r'-\d+', port_A):
          # print(rnode)
          # print(lhs)
          g.add_node(num_identify, name = num_identify, num = port_A, kind = "num")
          g.add_edge(num_identify, mux_name)
          num_identify = num_identify + 1
        else:
          g.add_edge(port_A, mux_name)
      # print(list(g.in_edges(mux_name)))
      port_B = re.sub(r'^ *\\\$mux.*\.A\((.*)\), \.B\((.*)\), \.S\((.*)\), \.Y\((.*)\) \);$','\\2',vlines[line_no])
      # print("入力B")
      # print(port_B)
      #複数入力
      if re.search(r'\{|\}', port_B):
        # print("複数入力")
        port_B = re.sub(r'\{|\}', '', port_B)
        # print(port_B)
        port_B = port_B.replace(' ', '')
        port_B = port_B.split(',')
        for rnode in port_B:
          if re.search(r'\[.*\]', rnode):
            # print("異常あり")
            # print(rnode)
            rnode = re.sub(r'\[.*\]', '', rnode)
          #   print(rnode)
          # print("rnode")
          # print(rnode)
          if re.match(r'\d+', rnode) or re.match(r'\d+\'\d+', rnode) or re.match(r'-\d+', rnode):
            # print(rnode)
            # print(lhs)
            g.add_node(num_identify, name = num_identify, num = rnode, kind = "num")
            g.add_edge(num_identify, mux_name)
            num_identify = num_identify + 1
          else:
            g.add_edge(rnode, mux_name)
          # print("つないだ")
          # print(list(g.in_edges(mul_name)))
          # input()
      #単数入力
      elif re.search(r'\[.*\]', port_B):
        port_B = re.sub(r'\[.*\]', '', port_B)
        if re.match(r'\d+', port_B) or re.match(r'\d+\'\d+', port_B) or re.match(r'-\d+', port_B):
          # print(rnode)
          # print(lhs)
          g.add_node(num_identify, name = num_identify, num = port_B, kind = "num")
          g.add_edge(num_identify, mux_name)
          num_identify = num_identify + 1
        else:
          g.add_edge(port_B, mux_name)
      else:
        if re.match(r'\d+', port_B) or re.match(r'\d+\'\d+', port_B) or re.match(r'-\d+', port_B):
          # print(rnode)
          # print(lhs)
          g.add_node(num_identify, name = num_identify, num = port_B, kind = "num")
          g.add_edge(num_identify, mux_name)
          num_identify = num_identify + 1
        else:
          g.add_edge(port_B, mux_name)
      # print(list(g.in_edges(mux_name)))
      port_S = re.sub(r'^ *\\\$mux.*\.A\((.*)\), \.B\((.*)\), \.S\((.*)\), \.Y\((.*)\) \);$','\\3',vlines[line_no])
      # print("入力S")
      # print(port_S)
      #複数入力
      if re.search(r'\{|\}', port_S):
        # print("複数入力")
        port_S = re.sub(r'\{|\}', '', port_S)
        # print(port_B)
        port_S = port_S.replace(' ', '')
        port_S = port_S.split(',')
        for rnode in port_S:
          if re.search(r'\[.*\]', rnode):
            # print("異常あり")
            # print(rnode)
            rnode = re.sub(r'\[.*\]', '', rnode)
          #   print(rnode)
          # print("rnode")
          # print(rnode)
          if re.match(r'\d+', rnode) or re.match(r'\d+\'\d+', rnode) or re.match(r'-\d+', rnode):
            # print(rnode)
            # print(lhs)
            g.add_node(num_identify, name = num_identify, num = rnode, kind = "num")
            g.add_edge(num_identify, mux_name)
            num_identify = num_identify + 1
          else:
            g.add_edge(rnode, mux_name)
          # print("つないだ")
          # print(list(g.in_edges(mul_name)))
          # input()
      #単数入力
      elif re.search(r'\[.*\]', port_S):
        port_S = re.sub(r'\[.*\]', '', port_S)
        if re.match(r'\d+', port_S) or re.match(r'\d+\'\d+', port_S):
          # print(rnode)
          # print(lhs)
          g.add_node(num_identify, name = num_identify, num = port_S, kind = "num")
          g.add_edge(num_identify, mux_name)
          num_identify = num_identify + 1
        else:
          g.add_edge(port_S, mux_name)
      else:
        if re.match(r'\d+', port_S) or re.match(r'\d+\'\d+', port_S):
          # print(rnode)
          # print(lhs)
          g.add_node(num_identify, name = num_identify, num = port_S, kind = "num")
          g.add_edge(num_identify, mux_name)
          num_identify = num_identify + 1
        else:
          g.add_edge(port_S, mux_name)
      # print(list(g.in_edges(mux_name)))
      port_Y = re.sub(r'^ *\\\$mux.*\.A\((.*)\), \.B\((.*)\), \.S\((.*)\), \.Y\((.*)\) \);$','\\4',vlines[line_no])
      # print("出力Y")
      # print(port_Y)
      # print(type(port_A))
      if re.search(r'\{|\}',port_Y):
        # print("複数出力")
        port_Y = re.sub(r'\{|\}', '', port_Y)
        port_Y = port_Y.replace(' ', '')
        port_Y = port_Y.split(',')
        # print(port_Y)
        for ynode in port_Y:
          if re.search(r'\[.*\]', ynode):
            # print("異常あり")
            # print(rnode)
            ynode = re.sub(r'\[.*\]', '', ynode)
          # print(rnode)
          # print(rnode)
          g.add_edge(mul_name, ynode)
          # print("つないだ")
          # print(list(g.in_edges(ynode)))
          # input()
      else:
        # print("単数出力")
        if re.search(r'\[.*\]', port_Y):
            # print("異常あり")
            # print(rnode)
            port_Y = re.sub(r'\[.*\]', '', port_Y)
        g.add_edge(mul_name, port_Y)
        # print("つないだ")
      # print(list(g.in_edges(port_Y)))
      # print(port_LUT)
    #  sdff  ###############################################################
    elif re.search(r'^ *\\\$sdff.*$',vlines[line_no]):
      # print('line_no:{0}'.format(line_no))
      # print(vlines[line_no])
      CLK_POLARITY = re.sub(r'^ *\\\$sdff.*\.CLK_POLARITY\((.*)\), \.WIDTH\((\d+)\),.*$','\\1',vlines[line_no])
      WIDTH = re.sub(r'^ *\\\$sdff.*\.WIDTH\((\d+)\), .*$','\\1',vlines[line_no])
      SRST_POLARITY = re.sub(r'^ *\\\$sdff.*\.SRST_POLARITY\((.*)\), \.SRST_VALUE\((.*)\) .*$','\\1',vlines[line_no])
      SRST_VALUE = re.sub(r'^ *\\\$sdff.*\.SRST_VALUE\((.*)\) \) .*$','\\1',vlines[line_no])
      if re.search(r'\s_\d+_\s',vlines[line_no]):
        sdff_name = re.search(r'\s_\d+_\s',vlines[line_no]).group()
        sdff_name = sdff_name.replace(' ', '')
        # print("sdff_name")
        # print(sdff_name)
      elif re.search(r'^ *\\\$sdff #\(.*\)\s.*\s\(.*\);$',vlines[line_no]):
        # sdff_name = re.search(r'#\(.*\)\s.*\s\(.*\);$',vlines[line_no]).group()
        sdff_name = re.sub(r'^ *\\\$sdff #\(.*\)\s(.*)\s\(.*\);$', '\\1', vlines[line_no])
        # print(sdff_name)
      g.add_node(sdff_name, name = sdff_name, CLK_POLARITY = CLK_POLARITY, WIDTH = WIDTH, SRST_POLARITY = SRST_POLARITY, SRST_VALUE = SRST_VALUE, kind = "sdff")
      port_CLK = re.sub(r'^ *\\\$sdff.*\.CLK\((.*)\), \.D\((.*)\), \.Q\((.*)\), \.SRST\((.*)\) \);$','\\1',vlines[line_no])
      #複数入力
      # print(port_CLK)
      if re.search(r'\{|\}', port_CLK):
        # print("複数入力")
        port_CLK = re.sub(r'\{|\}', '', port_CLK)
        # print(port_A)
        port_CLK = port_CLK.replace(' ', '')
        port_CLK = port_CLK.split(',')
        for rnode in port_CLK:
          if re.search(r'\[.*\]', rnode):
            # print("異常あり")
            # print(rnode)
            rnode = re.sub(r'\[.*\]', '', rnode)
          #   print(rnode)
          # print("rnode")
          # print(rnode)
          if re.match(r'\d+', rnode) or re.match(r'\d+\'\d+', rnode):
            # print(rnode)
            # print(lhs)
            g.add_node(num_identify, name = num_identify, num = rnode, kind = "num")
            g.add_edge(num_identify, sdff_name)
            num_identify = num_identify + 1
          else:
            g.add_edge(rnode, sdff_name)
          # print("つないだ")
          # print(list(g.in_edges(mux_name)))
      #単数入力 
      elif re.search(r'\[.*\]', port_CLK):
        port_CLK = re.sub(r'\[.*\]', '', port_CLK)
        if re.match(r'\d+', port_CLK) or re.match(r'\d+\'\d+', port_CLK):
          # print(rnode)
          # print(lhs)
          g.add_node(num_identify, name = num_identify, num = port_CLK, kind = "num")
          g.add_edge(num_identify, sdff_name)
          num_identify = num_identify + 1
        else:
          g.add_edge(port_CLK, sdff_name)
      else:
        if re.match(r'\d+', port_CLK) or re.match(r'\d+\'\d+', port_CLK):
          # print(rnode)
          # print(lhs)
          g.add_node(num_identify, name = num_identify, num = port_CLK, kind = "num")
          g.add_edge(num_identify, sdff_name)
          num_identify = num_identify + 1
        else:
          g.add_edge(port_CLK, sdff_name)
      # print(list(g.in_edges(sdff_name)))
      port_D = re.sub(r'^ *\\\$sdff.*\.CLK\((.*)\), \.D\((.*)\), \.Q\((.*)\), \.SRST\((.*)\) \);$','\\2',vlines[line_no])
      port_D = re.sub(r'\\', '', port_D)
      port_D = port_D.replace(' ', '')
      # print("入力D")
      # print(port_D)
      #複数入力
      if re.search(r'\{|\}', port_D):
        # print("複数入力")
        port_D = re.sub(r'\{|\}', '', port_D)
        # print(port_B)
        port_D = port_D.replace(' ', '')
        port_D = port_D.split(',')
        for rnode in port_D:
          if re.search(r'\[.*\]', rnode):
            # print("異常あり")
            # print(rnode)
            rnode = re.sub(r'\[.*\]', '', rnode)
          #   print(rnode)
          # print("rnode")
          # print(rnode)
          if re.match(r'\d+', rnode) or re.match(r'\d+\'\d+', rnode):
            # print(rnode)
            # print(lhs)
            g.add_node(num_identify, name = num_identify, num = rnode, kind = "num")
            g.add_edge(num_identify, sdff_name)
            num_identify = num_identify + 1
          else:
            g.add_edge(rnode, sdff_name)
          # print("つないだ")
          # print(list(g.in_edges(mul_name)))
          # input()
      #単数入力
      elif re.search(r'\[.*\]', port_D):
        port_D = re.sub(r'\[.*\]', '', port_D)
        if re.match(r'\d+', port_D) or re.match(r'\d+\'\d+', port_D):
          # print(rnode)
          # print(lhs)
          g.add_node(num_identify, name = num_identify, num = port_D, kind = "num")
          g.add_edge(num_identify, sdff_name)
          num_identify = num_identify + 1
        else:
          g.add_edge(port_D, sdff_name)
      else:
        if re.match(r'\d+', port_D) or re.match(r'\d+\'\d+', port_D):
          # print(rnode)
          # print(lhs)
          g.add_node(num_identify, name = num_identify, num = port_D, kind = "num")
          g.add_edge(num_identify, sdff_name)
          num_identify = num_identify + 1
        else:
          g.add_edge(port_D, sdff_name)
      # print(list(g.in_edges(sdff_name)))
      port_Q = re.sub(r'^ *\\\$sdff.*\.CLK\((.*)\), \.D\((.*)\), \.Q\((.*)\), \.SRST\((.*)\) \);$','\\3',vlines[line_no])
      # print("出力Q")
      # print(port_Q)
      # print(type(port_A))
      if re.search(r'\{|\}',port_Q):
        # print("複数出力")
        port_Q = re.sub(r'\{|\}', '', port_Q)
        port_Q = port_Q.replace(' ', '')
        port_Q = port_Q.split(',')
        # print(port_Y)
        for ynode in port_Q:
          if re.search(r'\[.*\]', ynode):
            # print("異常あり")
            # print(rnode)
            ynode = re.sub(r'\[.*\]', '', ynode)
          # print(rnode)
          # print(rnode)
          g.add_edge(sdff_name, ynode)
          # print("つないだ")
          # print(list(g.in_edges(ynode)))
          # input()
      else:
        # print("単数出力")
        if re.search(r'\[.*\]', port_Q):
            # print("異常あり")
            # print(rnode)
            port_Q = re.sub(r'\[.*\]', '', port_Q)
        g.add_edge(sdff_name, port_Q)
        # print("つないだ")
      # print(list(g.in_edges(port_Y)))
      # print(port_LUT)
      port_SRST = re.sub(r'^ *\\\$sdff.*\.CLK\((.*)\), \.D\((.*)\), \.Q\((.*)\), \.SRST\((.*)\) \);$','\\3',vlines[line_no])
      # print("出力SRST")
      # print(port_SRST)
      # print(type(port_A))
      if re.search(r'\{|\}',port_SRST):
        # print("複数出力")
        port_SRST = re.sub(r'\{|\}', '', port_SRST)
        port_SRST = port_SRST.replace(' ', '')
        port_SRST = port_SRST.split(',')
        # print(port_Y)
        for ynode in port_SRST:
          if re.search(r'\[.*\]', ynode):
            # print("異常あり")
            # print(rnode)
            ynode = re.sub(r'\[.*\]', '', ynode)
          # print(rnode)
          # print(rnode)
          g.add_edge(sdff_name, ynode)
          # print("つないだ")
          # print(list(g.in_edges(ynode)))
          # input()
      else:
        # print("単数出力")
        if re.search(r'\[.*\]', port_SRST):
            # print("異常あり")
            # print(rnode)
            port_SRST = re.sub(r'\[.*\]', '', port_SRST)
        g.add_edge(sdff_name, port_SRST)
        # print("つないだ")
      # print(list(g.in_edges(port_Y)))
      # print(port_LUT)
    #  dff  ###############################################################
    elif re.search(r'^ *\\\$dff.*$',vlines[line_no]):
      # print('line_no:{0}'.format(line_no))
      # print(vlines[line_no])
      CLK_POLARITY = re.sub(r'^ *\\\$dff.*\.CLK_POLARITY\((.*)\), \.WIDTH\((.*)\).*$','\\1',vlines[line_no])
      WIDTH = re.sub(r'^ *\\\$dff.*\.CLK_POLARITY\((.*)\), \.WIDTH\((\d+)\) \).*$','\\2',vlines[line_no])
      # WIDTH = re.sub(r'\.WIDTH\((\d+)\)','\\1',vlines[line_no])
      # print(CLK_POLARITY)
      # print(WIDTH)
      if re.search(r'\s_\d+_\s',vlines[line_no]):
        dff_name = re.search(r'\s_\d+_\s',vlines[line_no]).group()
        dff_name = dff_name.replace(' ', '')
        # print("dff_name")
        # print(dff_name)
        # input()
      else:
        # print("else")
        # input()
        # sdff_name = re.search(r'#\(.*\)\s.*\s\(.*\);$',vlines[line_no]).group()
        dff_name = re.sub(r'^ *\\\$dff  #\( \.CLK_POLARITY\(.*\), \.WIDTH\(.*\) \) (.*)  \( \.CLK\(.*\), \.D\(.*\), \.Q\(.*\) \);$', '\\1', vlines[line_no])
        # print("ここ")
        # print(dff_name)
        # input()
      g.add_node(dff_name, name = dff_name, CLK_POLARITY = CLK_POLARITY, WIDTH = WIDTH, kind = "dff")
      # print(list(g.in_edges(dff_name)))
      port_CLK = re.sub(r'^ *\\\$dff.*\.CLK\((.*)\), \.D\((.*)\), \.Q\((.*)\) \);$','\\1',vlines[line_no])
      #複数入力
      # print(port_CLK)
      # input()
      if re.search(r'\{|\}', port_CLK):
        # print("複数入力")
        port_CLK = re.sub(r'\{|\}', '', port_CLK)
        # print(port_A)
        port_CLK = port_CLK.replace(' ', '')
        port_CLK = port_CLK.split(',')
        for rnode in port_CLK:
          if re.search(r'\[.*\]', rnode):
            # print("異常あり")
            # print(rnode)
            rnode = re.sub(r'\[.*\]', '', rnode)
          #   print(rnode)
          # print("rnode")
          # print(rnode)
          if re.match(r'\d+', rnode) or re.match(r'\d+\'\d+', rnode):
            # print(rnode)
            # print(lhs)
            g.add_node(num_identify, name = num_identify, num = rnode, kind = "num")
            g.add_edge(num_identify, dff_name)
            num_identify = num_identify + 1
          else:
            g.add_edge(rnode, dff_name)
          # print("つないだ")
          # print(list(g.in_edges(mux_name)))
      #単数入力 
      elif re.search(r'\[.*\]', port_CLK):
        port_CLK = re.sub(r'\[.*\]', '', port_CLK)
        if re.match(r'\d+', port_CLK) or re.match(r'\d+\'\d+', port_CLK):
          # print(rnode)
          # print(lhs)
          g.add_node(num_identify, name = num_identify, num = port_CLK, kind = "num")
          g.add_edge(num_identify, dff_name)
          num_identify = num_identify + 1
        else:
          g.add_edge(port_CLK, dff_name)
      else:
        if re.match(r'\d+', port_CLK) or re.match(r'\d+\'\d+', port_CLK):
          # print(rnode)
          # print(lhs)
          g.add_node(num_identify, name = num_identify, num = port_CLK, kind = "num")
          g.add_edge(num_identify, dff_name)
          num_identify = num_identify + 1
        else:
          g.add_edge(port_CLK, dff_name)
      # print(list(g.in_edges(sdff_name)))
      port_D = re.sub(r'^ *\\\$dff.*\.CLK\((.*)\), \.D\((.*)\), \.Q\((.*)\) \);$','\\2',vlines[line_no])
      # print("入力D")
      # print(port_D)
      #複数入力
      if re.search(r'\{|\}', port_D):
        # print("複数入力")
        port_D = re.sub(r'\{|\}', '', port_D)
        # print(port_B)
        port_D = port_D.replace(' ', '')
        port_D = port_D.split(',')
        for rnode in port_D:
          if re.search(r'\[.*\]', rnode):
            # print("異常あり")
            # print(rnode)
            rnode = re.sub(r'\[.*\]', '', rnode)
          #   print(rnode)
          # print("rnode")
          # print(rnode)
          if re.match(r'\d+', rnode) or re.match(r'\d+\'\d+', rnode):
            # print(rnode)
            # print(lhs)
            g.add_node(num_identify, name = num_identify, num = rnode, kind = "num")
            g.add_edge(num_identify, dff_name)
            num_identify = num_identify + 1
          else:
            g.add_edge(rnode, dff_name)
          # print("つないだ")
          # print(list(g.in_edges(mul_name)))
          # input()
      #単数入力
      elif re.search(r'\[.*\]', port_D):
        port_D = re.sub(r'\[.*\]', '', port_D)
        if re.match(r'\d+', port_D) or re.match(r'\d+\'\d+', port_D):
          # print(rnode)
          # print(lhs)
          g.add_node(num_identify, name = num_identify, num = port_D, kind = "num")
          g.add_edge(num_identify, dff_name)
          num_identify = num_identify + 1
        else:
          g.add_edge(port_D, dff_name)
      elif re.search(r'\\', port_D):
        # print("ここ")
        port_D = re.sub(r'\\', '', port_D)
        port_D = port_D.replace(' ', '')
        # print(port_Q)
        # input()
        if re.match(r'\d+', port_D) or re.match(r'\d+\'\d+', port_D):
          # print(rnode)
          # print(lhs)
          g.add_node(num_identify, name = num_identify, num = port_D, kind = "num")
          g.add_edge(num_identify, dff_name)
          num_identify = num_identify + 1
        else:
          g.add_edge(port_D, dff_name)
      else:
        if re.match(r'\d+', port_D) or re.match(r'\d+\'\d+', port_D):
          # print(rnode)
          # print(lhs)
          g.add_node(num_identify, name = num_identify, num = port_D, kind = "num")
          g.add_edge(num_identify, dff_name)
          num_identify = num_identify + 1
        else:
          g.add_edge(port_D, dff_name)
      # print(list(g.in_edges(dff_name)))
      # input()
      port_Q = re.sub(r'^ *\\\$dff.*\.CLK\((.*)\), \.D\((.*)\), \.Q\((.*)\) \);$','\\3',vlines[line_no])
      # print("出力Q")
      # print(port_Q)
      # input()
      # input()
      # print(type(port_A))
      port_Q = re.sub(r'\\', '', port_Q)
      port_Q = port_Q.replace(' ', '')
      if re.search(r'\{|\}',port_Q):
        # print("複数出力")
        port_Q = re.sub(r'\{|\}', '', port_Q)
        port_Q = port_Q.replace(' ', '')
        port_Q = port_Q.split(',')
        # print(port_Y)
        for ynode in port_Q:
          if re.search(r'\[.*\]', ynode):
            # print("異常あり")
            # print(rnode)
            ynode = re.sub(r'\[.*\]', '', ynode)
          # print(rnode)
          # print(rnode)
          g.add_edge(dff_name, ynode)
          # print("つないだ")
          # print(list(g.in_edges(ynode)))
          # input()
      elif re.search(r'\\', port_Q):
        # print("ここ")
        port_Q = re.sub(r'\\', '', port_Q)
        port_Q = port_Q.replace(' ', '')
        # print(port_Q)
        g.add_edge(dff_name, port_Q)
      else:
        # print("単数出力")
        if re.search(r'\[.*\]', port_Q):
            # print("異常あり")
            # print(rnode)
            port_Q = re.sub(r'\[.*\]', '', port_Q)
        g.add_edge(dff_name, port_Q)
        # print("つないだ")
      # print(list(g.in_edges(port_Q)))
      # input()
      # print(port_LUT)
      ###########################ram####################################
    elif re.search(r'^ *ram_.*$', vlines[line_no]):
      splited_s = []
      # print("ram")
      # print('line_no:{0}'.format(line_no))
      # print(vlines[line_no])
      #まず, 空白を区切り文字としてリストに格納する
      splited_s = (vlines[line_no].split(' '))
      # print(splited_s)
      # print(len(splited_s))
      if len(splited_s) != 15:
        print("error!!")
        input()
      # input()
      #splited_s[2]について
      # print(splited_s[2])
      # input()
      # ram_w8_l2048_id9_3
      #頂点として追加
      # G.add_node(splited_s[2], name = splited_s[2])
      # G.nodes[頂点][属性キー] = 属性値
      # G.nodes[splited_s[2]]['module'] = 'module' #属性としてmoduleを持たせる
      #splited_s[3]について
      # print(splited_s[3])
      ram_name = splited_s[3]
      # print(ram_name)
      # input()
      #inst_ram_w8_l2048_id9_3
      #頂点として追加
      g.add_node(ram_name, name = ram_name, kind = "ram")
      #splited_s[6]について
      # print(splited_s[6])
      # input()
      #ram_w8_l2048_id9_3_0_addr
      addr_a = re.sub(r'\.', '', splited_s[6])  #ピリオドを削除
      addr_a = re.sub(r'.*\((.*)\)\,$','\\1', addr_a)
      # print(addr_a)
      if re.match(r'\d+', addr_a) or re.match(r'\d+\'\d+', addr_a):
          # print(rnode)
          # print(lhs)
          g.add_node(num_identify, name = num_identify, num = addr_a, kind = "num")
          g.add_edge(num_identify, ram_name)
          num_identify = num_identify + 1
      else:
        g.add_edge(addr_a, ram_name)
      # input()
      #splited_s[7]について
      # print(splited_s[7])
      # ram_w8_l2048_id9_2_0_rdata
      rdata_a = re.sub(r'\.', '', splited_s[7])
      rdata_a = re.sub(r'.*\((.*)\)\,$','\\1', rdata_a)
      # print(rdata_a)
      # input()
      g.add_edge(ram_name, rdata_a)
      #splited_s[8]について
      # print(splited_s[8])
      # ram_w8_l2048_id9_3_0_wdata
      wdata_a = re.sub(r'\.', '', splited_s[8])
      wdata_a = re.sub(r'.*\((.*)\)\,$','\\1', wdata_a)
      # print(wdata_a)
      # input()
      if re.match(r'\d+', wdata_a) or re.match(r'\d+\'\d+', wdata_a):
          # print(rnode)
          # print(lhs)
          g.add_node(num_identify, name = num_identify, num = wdata_a, kind = "num")
          g.add_edge(num_identify, ram_name)
          num_identify = num_identify + 1
      else:
        g.add_edge(wdata_a, ram_name)
      #splited_s[9]について
      # print(splited_s[9])
      # ram_w8_l2048_id9_3_0_wenable
      wenable_a = re.sub(r'\.', '', splited_s[9])
      wenable_a = re.sub(r'.*\((.*)\)\,$','\\1', wenable_a)
      # print(wenable_a)
      # input()
      if re.match(r'\d+', wenable_a) or re.match(r'\d+\'\d+', wenable_a):
          # print(rnode)
          # print(lhs)
          g.add_node(num_identify, name = num_identify, num = wenable_a, kind = "num")
          g.add_edge(num_identify, ram_name)
          num_identify = num_identify + 1
      else:
        g.add_edge(wenable_a, ram_name)
      #splited_s[10]について
      # print(splited_s[10])
      # ram_w8_l2048_id9_3_1_addr
      addr_b = re.sub(r'\.', '', splited_s[10])
      addr_b = re.sub(r'.*\((.*)\)\,$','\\1', addr_b)
      # print(addr_b)
      # input()
      if re.match(r'\d+', addr_b) or re.match(r'\d+\'\d+', addr_b):
          # print(rnode)
          # print(lhs)
          g.add_node(num_identify, name = num_identify, num = addr_b, kind = "num")
          g.add_edge(num_identify, ram_name)
          num_identify = num_identify + 1
      else:
        g.add_edge(addr_b, ram_name)
      #splited_s[11]について
      # print(splited_s[11])
      # ram_w8_l2048_id9_3_1_rdata
      rdata_b = re.sub(r'\.', '', splited_s[11])
      rdata_b = re.sub(r'.*\((.*)\)\,$','\\1', rdata_b)
      # print(rdata_b)
      # input()
      g.add_edge(ram_name, rdata_b)
      #splited_s[12]について
      # print(splited_s[12])
      # ram_w8_l2048_id9_3_1_wdata
      wdata_b = re.sub(r'\.', '', splited_s[12])
      wdata_b = re.sub(r'.*\((.*)\)\,$','\\1', wdata_b)
      # print(wdata_b)
      # input()
      if re.match(r'\d+', wdata_b) or re.match(r'\d+\'\d+', wdata_b):
          # print(rnode)
          # print(lhs)
          g.add_node(num_identify, name = num_identify, num = wdata_b, kind = "num")
          g.add_edge(num_identify, ram_name)
          num_identify = num_identify + 1
      else:
        g.add_edge(wdata_b, ram_name)
      #splited_s[13]について
      # print(splited_s[13])
      # ram_w8_l2048_id9_3_1_wenable
      wenable_b = re.sub(r'\.', '', splited_s[13])
      if re.search(r'ram_.*\((ram_.*)\)$', wenable_b):
        wenable_b = re.sub(r'ram_.*\((ram_.*)\)$','\\1', wenable_b)
      else:
        wenable_b = re.sub(r'ram_.*\((\d\'.*)\)$','\\1', wenable_b)
        # print(wenable_b)
        # input()
      # print(wenable_b)
      # input()
      if re.match(r'\d+', wenable_b) or re.match(r'\d+\'\d+', wenable_b):
        # print(rnode)
        # print(lhs)
        g.add_node(num_identify, name = num_identify, num = wenable_b, kind = "num")
        g.add_edge(num_identify, ram_name)
        num_identify = num_identify + 1
      else:
        g.add_edge(wenable_b, ram_name)

#main関数
def main():
  global vlines
  ## Verilogファイル(presynthesis_sdff.vを読み込む)
  path = '/home/doi/map_after_yosys/presynthesis_sdff.v'
  with open(path) as f:
    vlines = [s.replace('\n', '') for s in f.readlines()]

  ### Verilogファイルを走査する
  scan_verilog()
  


  ###ノードと属性をすべて表示する
  for node in nx.nodes(g):
    print(node)
    print(g.nodes[node])
"""
  #グラフを描画する
  # nx.nx_agraph.view_pygraphviz(g, prog='fdp')  # pygraphvizが必要
  print("ノード数")
  print(nx.number_of_nodes(g))
"""
if __name__ == '__main__':
    main()