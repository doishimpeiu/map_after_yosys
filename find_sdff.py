#! /usr/bin/python3
import sys
import re

### 行番号
line_no = 0

### ノード情報のクラス
class Node:
    def __init__(self, type, name, line, width, fanout):
        self.valid  = True
        self.type   = type   ### input, output, wire
        self.name   = name   ### ノード名
        self.line   = line   ### 宣言された行の番号（vlines[] の添え字）
        self.width  = width  ### ビット幅
        self.fanout = fanout ### ファンアウト数
        self.driver = []     ### 駆動エレメントの番号
    def add_fanout(self, fo):
        self.fanout = self.fanout + fo
    def set_driver(self, elem):
        self.driver.append(elem)

### Nodeクラスを格納するリスト
node_list = []

### Nodeリスト逆引き用辞書
node_dict = dict([])

### エレメント情報のクラス
class Element:
    def __init__(self, type, name, line, text, para, port):
        self.valid = True ### True : 有効, False : 削除済み
        self.type = type ### input, assign, lut, add, sub, mul, mux, dff, ram
        self.name = name ### インスタンス名 (assign文は左辺の信号名)
        self.line = line ### 記述された行の番号（vlines[] の添え字）
        self.text = text ### Verilog記述
        self.para = para ### パラメータのリスト
        self.port = port ### ポートのリスト
    ### input の場合
    #### para: [ [ 'WIDTH' , ビット幅 ] ]
    #### port: [ [ 'Y' , ワイヤ名 ] ]
    ### assign の場合
    #### para: []
    #### port: [ [ 'A' , 右辺の式 ] , [ 'Y' , 左辺の式 ] ]
    ### lut の場合
    #### para: [ [ 'LUT' , 真理値表 ] , [ 'WIDTH' , 入力ビット数 ] ]
    #### port: [ [ 'A' , 入力の式 ] , [ 'Y' , 出力の式 ] ]
    ### mux の場合
    #### para: [ [ 'WIDTH' , ビット数 ] ]
    #### port: [ [ 'A' , ワイヤ名 ] , [ 'B' , ワイヤ名 ] , [ 'S' , ワイヤ名 ] , [ 'Y' , ワイヤ名 ] ]
    ### dff の場合
    #### para: [ [ 'CLK_POLARITY' , 0か1 ] , [ 'WIDTH' , ビット数 ] ]
    #### port: [ [ 'CLK' , ワイヤ名 ] , [ 'D' , ワイヤ名 ] , [ 'Q' , ワイヤ名 ] ]
    
### Elementクラスを格納するリスト
elem_list = []

#######################################################################
### expr_list に含まれるノードの .fanout に値(fo=1)を足す
def increment_fanout(expr_list,fo=1):
    global node_list
    #global line_no
    #global vlines
    #print({line_no+1},vlines[line_no],expr_list)
    ### { と } で囲まれている場合
    if expr_list[0] == 'concat':
        for l in expr_list[1:]:
            increment_fanout(l,fo)
    ### そうでない場合
    elif expr_list[0] != 'const' and expr_list[1] >= 0:
        node_list[expr_list[1]].add_fanout(fo)

#######################################################################
### expr_list に含まれるノードの .driver を設定する
def define_driver(expr_list, elem):
    global node_list
    #global line_no
    #global vlines
    #print({line_no+1},vlines[line_no],expr_list)
    ### { と } で囲まれている場合
    if expr_list[0] == 'concat':
        for l in expr_list[1:]:
            define_driver(l,elem)
    ### そうでない場合
    elif expr_list[0] != 'const' and expr_list[1] >= 0:
        node_list[expr_list[1]].set_driver(elem)

#######################################################################
### yosys の組み込みセルのインスタンスの構文解析
def parse_builtin(text):
    s = text.strip()
    r = r'^(\\\$[a-z][a-z0-9]*) *\#\((.*) +\) +([_A-Za-z0-9]+) +\( +([^;]+) +\)\; *$'
    rp = r'^\.([_A-Z0-9]+)\((.*)\)$'
    ra = r'^([_A-Z0-9]+)\((.*)\) *$'
    if re.search(r,s):
        name = re.sub(r,'\\1',s).strip()
        para = re.sub(r,'\\2',s).strip()
        inst = re.sub(r,'\\3',s).strip()
        args = re.sub(r,'\\4',s).strip()
        para_list = [ [ re.sub(rp,'\\1',_.strip()) , re.sub(rp,'\\2',_.strip()) ] for _ in para.split(',') ]
        args_list = [ [ re.sub(ra,'\\1',_.strip()) , re.sub(ra,'\\2',_).strip() ] for _ in re.sub(' +',' ',re.sub(r'^\.','',args)).split(', .') ]
        #print('args:',args)
        #print(args_list)
        return [ name, para_list, inst, args_list ]
    else:
        return False

#######################################################################
### ram モジュールのインスタンスの構文解析
def parse_instance(text):
    s = text.strip()
    r = r'^([_A-Za-z][_A-Za-z0-9]*) +([_A-Za-z][_A-Za-z0-9]*) +\( +([^;]+) +\)\; *$'
    ra = r'^([_A-Za-z][_A-Za-z0-9]*)\((.*)\)$'
    if re.search(r,s):
        name = re.sub(r,'\\1',s).strip()
        inst = re.sub(r,'\\2',s).strip()
        args = re.sub(r,'\\3',s).strip()
        args_list = [ [ re.sub(ra,'\\1',_.strip()) , re.sub(ra,'\\2',_.strip()) ] for _ in re.sub(' +',' ',re.sub(r'^\.','',args.strip())).split(', .') ]
        return [ name, inst, args_list ]
    else:
        return False

#######################################################################
### 定数, ワイヤ, 連結演算子からなる式の構文解析
def parse_expression(text):
    global node_dict
    global line_no ### 行番号
    #print(text)
    s = text.strip()
    ### { と } で囲まれている場合
    if re.search(r'^\{.*\}$',s):
        body = re.sub(r'^\{(.*)\}$','\\1',s).split(',')
        if(len(body) == 1):
            return parse_expression(body[0].strip())
        else:
            list = [ 'concat' ]
            for s in body:
                list.append(parse_expression(s.strip()))
            return list
    ### 10進定数の場合
    elif re.search(r'^\-?[0-9]+$',s):
        return [ 'const' , int(s) ]
    ### 16進定数の場合
    elif re.search(r'^[0-9]+\'h[0-9a-fA-F]+$',s):
        return [ 'const' , int(re.sub(r'^[0-9]+\'h([0-9a-fA-F]+)$','\\1',s),16) ]
    ### 不定値定数の場合
    elif re.search(r'^[0-9]+\'h[xX]+$',s):
        return [ 'const' , 0 ]
    ### 単純変数の場合
    elif re.search(r'^[^][{}]+$',s):
        if s in node_dict:
            return [ 'full' , node_dict[s] ]
        else:
            print(f'{line_no+1}: Error: 式中の {s} が宣言されていません *1')
            return [ 'full' , -1 ]
    ### 添え字付きバス形式の場合
    elif re.search(r'^[_A-Za-z0-9]+\[[:0-9]+\]$',s):
        name = re.sub(r'^([_A-Za-z0-9]+)\[([:0-9]+)\]$','\\1',s)
        bus  = re.sub(r'^([_A-Za-z0-9]+)\[([:0-9]+)\]$','\\2',s)
        ### バスの添え字が [31:0] 形式の場合
        if re.search(r':',bus):
            imax   = int(re.sub(r'^([0-9]+):([0-9]+)$','\\1',bus))
            imin   = int(re.sub(r'^([0-9]+):([0-9]+)$','\\2',bus))
        ### バスの添え字が [0] 形式の場合
        else:
            imax   = int(bus)
            imin   = imax
        width = imax - imin + 1
        if name in node_dict:
            j = node_dict[name]
            if imin != 0 or width != node_list[j].width:
                return [ 'partial' , j ]
            else:
                return [ 'full' , j ]
        else:
            print(f'{line_no+1}: Error: 式中の {name} が宣言されていません *2')
            return [ 'partial' , -1 ]

#######################################################################
### Verilog記述を1行ずつ走査する
def scan_verilog():
    global vlines, line_no
    global node_list, node_dict, elem_list
    for line_no in range(len(vlines)):
        ### input文（バスの場合）
        if re.search(r'^ *input *\[[0-9]+:[0-9]+\] ',vlines[line_no]):
            #print(line_no,vlines[line_no])
            imax = int(re.sub(r'^ *input *\[([0-9]+):([0-9]+)\] *([^ ]+) *;.*$','\\1',vlines[line_no]))
            imin = int(re.sub(r'^ *input *\[([0-9]+):([0-9]+)\] *([^ ]+) *;.*$','\\2',vlines[line_no]))
            name = re.sub(r'^ *input *\[([0-9]+):([0-9]+)\] *([^ ]+) *;.*$','\\3',vlines[line_no])
            if imin != 0:
                print(f'{line_no+1}: Warning: input {name} のバス宣言が変です')
            if name in node_dict:
                print(f'{line_no+1}: Warning: input {name} が既に宣言されています')
            node_dict[name] = len(node_list)
            node_list.append(Node('input', name, line_no, imax+1,0))
            width = imax - imin + 1
            elem_list.append(Element('input', name, line_no, vlines[line_no], [ [ 'WIDTH' , width ] ], [ [ 'Y' , name ] ] ))
            define_driver(parse_expression(name),len(elem_list)-1)
        ### input文（バスでない場合）
        elif re.search(r'^ *input ',vlines[line_no]):
            #print(line_no,vlines[line_no])
            imax = 0
            imin = 0
            name = re.sub(r'^ *input +([^ ]+) *;.*$','\\1',vlines[line_no])
            if name in node_dict:
                print(f'{line_no+1}: Warning: input {name} が既に宣言されています')
            node_dict[name] = len(node_list)
            node_list.append(Node('input',name,line_no,imax+1,0))
            width = imax - imin + 1
            elem_list.append(Element('input', name, line_no, vlines[line_no], [ [ 'WIDTH' , width ] ], [ [ 'Y' , name ] ] ))
            define_driver(parse_expression(name),len(elem_list)-1)
        ### output文（バスの場合）
        elif re.search(r'^ *output *\[[0-9]+:[0-9]+\] ',vlines[line_no]):
            #print(line_no,vlines[line_no])
            imax = int(re.sub(r'^ *output *\[([0-9]+):([0-9]+)\] *([^ ]+) *;.*$','\\1',vlines[line_no]))
            imin = int(re.sub(r'^ *output *\[([0-9]+):([0-9]+)\] *([^ ]+) *;.*$','\\2',vlines[line_no]))
            name = re.sub(r'^ *output *\[([0-9]+):([0-9]+)\] *([^ ]+) *;.*$','\\3',vlines[line_no])
            if imin != 0:
                print(f'{line_no+1}: Warning: output {name} のバス宣言が変です')
            if name in node_dict:
                print(f'{line_no+1}: Warning: output {name} が既に宣言されています')
            node_dict[name] = len(node_list)
            node_list.append(Node('output',name,line_no,imax+1,1))
        ### output文（バスでない場合）
        elif re.search(r'^ *output ',vlines[line_no]):
            #print(line_no,vlines[line_no])
            imax = 0
            imin = 0
            name = re.sub(r'^ *output +([^ ]+) *;.*$','\\1',vlines[line_no])
            if name in node_dict:
                print(f'{line_no+1}: Warning: output {name} が既に宣言されています')
            node_dict[name] = len(node_list)
            node_list.append(Node('output',name,line_no,imax+1,1))
            increment_fanout(parse_expression(name))
        ### wire文（バスの場合）
        elif re.search(r'^ *wire *\[[0-9]+:[0-9]+\] ',vlines[line_no]):
            #print(line_no,vlines[line_no])
            imax = int(re.sub(r'^ *wire *\[([0-9]+):([0-9]+)\] *([^ ]+) *;.*$','\\1',vlines[line_no]))
            imin = int(re.sub(r'^ *wire *\[([0-9]+):([0-9]+)\] *([^ ]+) *;.*$','\\2',vlines[line_no]))
            name = re.sub(r'^ *wire *\[([0-9]+):([0-9]+)\] *([^ ]+) *;.*$','\\3',vlines[line_no])
            if imin != 0:
                print(f'{line_no+1}: Warning: wire {name} のバス宣言が変です')
            if name in node_dict:
                print(f'{line_no+1}: Warning: wire {name} が既に宣言されています')
            node_dict[name] = len(node_list)
            node_list.append(Node('wire',name,line_no,imax+1,0))
        ### wire文（バスでない場合）
        elif re.search(r'^ *wire ',vlines[line_no]):
            #print(line_no,vlines[line_no])
            imax = 0
            imin = 0
            name = re.sub(r'^ *wire +([^ ]+) *;.*$','\\1',vlines[line_no])
            if name in node_dict:
                print(f'{line_no+1}: Warning: wire {name} が既に宣言されています')
            node_dict[name] = len(node_list)
            node_list.append(Node('wire',name,line_no,imax+1,0))
        ### assign文
        elif re.search(r'^ *assign +[^=]+ *= *[^;]+;.*$',vlines[line_no]):
            lhs = re.sub(r'^ *assign +([^=]+) *= *([^;]+);.*$','\\1',vlines[line_no]).strip()
            rhs = re.sub(r'^ *assign +([^=]+) *= *([^;]+);.*$','\\2',vlines[line_no]).strip()
            #print(f'{line_no+1}|{vlines[line_no]}|{lhs}|{rhs}|')
            elem_list.append(Element('assign', lhs, line_no, vlines[line_no], [], [ [ 'A' , rhs ] , [ 'Y' , lhs ] ] ))
            increment_fanout(parse_expression(rhs))
            define_driver(parse_expression(lhs),len(elem_list)-1)
        ### yosys の組み込みセルのインスタンス（\$lut, \$add, \$sub, \$mul, \$mux, \$dff）
        elif re.search(r'^ *\\\$.*$',vlines[line_no]):
            #print(line_no,vlines[line_no])
            l = parse_builtin(vlines[line_no])
            if l != False:
                type = re.sub(r'^\\\$([_A-Za-z0-9]+)$','\\1',l[0])
                elem_list.append(Element(type,l[2],line_no,vlines[line_no],l[1],l[3]))
                for p in l[3]:
                    if p[0] == 'Y' or p[0] == 'Q':
                        define_driver(parse_expression(p[1]),len(elem_list)-1)
                    else:
                        increment_fanout(parse_expression(p[1]))
            else:
                print(f'{line_no+1}: Error: 組み込みセルのインスタンスの構文エラーです')
        ### ram モジュールのインスタンス
        elif re.search(r'^ *ram_.*$',vlines[line_no]):
            l = parse_instance(vlines[line_no])
            if l != False:
                elem_list.append(Element('ram',l[1],line_no,vlines[line_no],l[0],l[2]))
                for p in l[2]:
                    #print(f'{line_no}: {p}')
                    if re.search(r'^.*_rdata$',p[0]):
                        define_driver(parse_expression(p[1]),len(elem_list)-1)
                    elif re.search(r'^(CLK|.*(_addr|_wdata|_wenable))$',p[0]):
                        increment_fanout(parse_expression(p[1]))
            else:
                print(f'{line_no+1}: Error: モジュールのインスタンスの構文エラーです')

#######################################################################
### 左辺のwireが他から参照されないassign文、およびそのような左辺のwireの宣言を無効にする
def remove_dummy_assign():
    global node_list, elem_list
    count = 0
    ### エレメントを1個ずつ見る
    for e_ix in range(len(elem_list)):
        ### 無効なエレメントや assign 以外のエレメントはスキップする
        if elem_list[e_ix].valid == False or elem_list[e_ix].type != 'assign':
            continue
        rhs_list = parse_expression(elem_list[e_ix].port[0][1])
        lhs_list = parse_expression(elem_list[e_ix].port[1][1])
        ### 左辺がバスの一部ならばスキップする
        if lhs_list[0] != 'full':
            continue
        ### 左辺のwireが他から参照されているならスキップする
        if node_list[lhs_list[1]].fanout > 0:
            continue
        ### 以上のチェックをパスした assign 文と、その左辺の wire 宣言は削除可能
        #print(f'{node_list[lhs_list[1]].name} は不要です')
        elem_list[e_ix].valid = False
        increment_fanout(rhs_list,-1)
        node_list[lhs_list[1]].valid = False
        count += 1
    print(f"*** 不要な assign文とwire文を各 {count} 行削除しました")

#######################################################################
### dff の D入力にビット幅が同じでファンアウトが 1 の mux が繋がっておりその B 入力が 0 であるものを探し、sdff に統合する
def find_sdff():
    global node_list, node_dict, elem_list
    count = 0
    ### エレメントを1個ずつ見る
    for e_ix in range(len(elem_list)):
        ### 無効なエレメントや dff 以外のエレメントはスキップする
        if elem_list[e_ix].valid == False or elem_list[e_ix].type != 'dff':
            continue
        d_width = int(elem_list[e_ix].para[1][1])  ### dff エレメントのビット数
        d_name = elem_list[e_ix].port[1][1]        ### dff エレメントの Dポートに繋がったワイヤ名
        d_ix = node_dict[d_name]                   ### そのワイヤの番号
        ### dff のビット幅と Dポートに繋がったワイヤのビット幅が一致していなかったら対象外にする
        if node_list[d_ix].width != d_width:
            #print(f'width of dff ({d_width}) and wire ({node_list[d_ix].width}) mismatch')
            continue
        ### dff の Dポートに繋がったワイヤが dff 以外にも何かを駆動していたら対象外にする
        if node_list[d_ix].fanout != 1:
            #print(f'fanout ({node_list[d_ix].fanout}) of wire {node_list[d_ix].name} != 1')
            continue
        ### dff の Dポートに繋がったワイヤを駆動するエレメントが2個以上あったら対象外にする
        if len(node_list[d_ix].driver) != 1:
            #print('#driver != 1')
            continue
        m_ix = node_list[d_ix].driver[0]  ### dff の Dポートに繋がったワイヤを駆動するエレメントの番号
        ### dff の Dポートに繋がったワイヤを駆動するエレメントが mux でなかったら対象外にする
        if elem_list[m_ix].type != 'mux':
            #print(f'driver of {d_name} is {elem_list[m_ix].type}')
            continue
        ### dff のビット数と mux のビット数が一致していなかったら対象外にする
        if int(elem_list[m_ix].para[0][1]) != d_width:
            #print(f'width of dff ({d_width}) and mux ({int(elem_list[m_ix].para[0][1])}) mismatch')
            continue
        ### mux の Bポートに定数 0 が与えられていなければ対象外にする
        if not(re.search(r'^(0+|[0-9]+\'h0+)$',elem_list[m_ix].port[1][1])):
            #print(f'mux\'s input B ({elem_list[m_ix].port[1][1]}) is not constant zero for output Y ({d_name})')
            continue
        ### 以上のチェックをパスした dff と mux は sdff に統合できる
        #print(f'dff {elem_list[e_ix].name} and mux {elem_list[m_ix].name} forms an sdff')
        #print('=== 置換前')
        #print(elem_list[e_ix].text)
        #print(elem_list[m_ix].text)
        ### dff エレメントを sdff エレメントに書き換える
        elem_list[e_ix].type = 'sdff' ### dff を sdff に変更
        elem_list[e_ix].para.append([ 'SRST_POLARITY' , '1\'h1' ]) ### mux の Bポートが定数だったので、リセット極性は 1
        elem_list[e_ix].para.append([ 'SRST_VALUE' , elem_list[m_ix].port[1][1] ])  ### mux のポートB → リセット値
        elem_list[e_ix].port[1][1] =                 elem_list[m_ix].port[0][1]     ### mux のポートA → sdff のポートD
        elem_list[e_ix].port.append([ 'SRST' ,       elem_list[m_ix].port[2][1] ])  ### mux のポートS → sdff のポートSRST
        ### 統合後の sdff エレメントを表す Verilog 記述の生成
        elem_list[e_ix].text = f'  \\${elem_list[e_ix].type} #('
        for i in range(len(elem_list[e_ix].para)):
            if i > 0:
                elem_list[e_ix].text += ','
            elem_list[e_ix].text += f' .{elem_list[e_ix].para[i][0]}({elem_list[e_ix].para[i][1]})'
        elem_list[e_ix].text += f' ) {elem_list[e_ix].name} ('
        for i in range(len(elem_list[e_ix].port)):
            if i > 0:
                elem_list[e_ix].text += ','
            if re.search(r'^\\',elem_list[e_ix].port[i][1]):
                elem_list[e_ix].text += f' .{elem_list[e_ix].port[i][0]}({elem_list[e_ix].port[i][1]} )'
            else:
                elem_list[e_ix].text += f' .{elem_list[e_ix].port[i][0]}({elem_list[e_ix].port[i][1]})'
        elem_list[e_ix].text += f' );'
        ### mux エレメントは無効化
        elem_list[m_ix].valid = False
        ### wire も無効化
        node_list[d_ix].valid = False
        #print('--- 置換後')
        #print(elem_list[e_ix].text)
        count += 1
    print(f"*** mux と dff を統合することにより {count} 個の sdff を生成しました")

#######################################################################
### 有効なノード数やエレメント数を表示する
def print_info():
    global node_list
    global elem_list
    node_types = [ 'input' , 'output' , 'wire' ]
    node_count = [ 0 for i in range(len(node_types)) ]
    elem_types = [ 'input' , 'assign' , 'lut' , 'add' , 'sub' , 'mul' , 'mux' , 'dff' , 'sdff' , 'ram' ]
    elem_count = [ 0 for i in range(len(elem_types)) ]
    ### 有効なノード数を数える
    for n_ix in range(len(node_list)):
        if node_list[n_ix].valid == False:
            continue
        if node_types.count(node_list[n_ix].type) > 0:
            node_count[node_types.index(node_list[n_ix].type)] += 1
    ### 有効なエレメント数を数える
    for e_ix in range(len(elem_list)):
        if elem_list[e_ix].valid == False:
            continue
        if elem_types.count(elem_list[e_ix].type) > 0:
            elem_count[elem_types.index(elem_list[e_ix].type)] += 1
    ### 結果を出力する
    types = ''
    count = ''
    for i in range(len(node_types)):
        types += "{:6} ".format(node_types[i])
        count += "{:6} ".format(node_count[i])
    for i in range(len(elem_types)):
        if elem_types[i] == 'input':
            continue
        types += "{:6} ".format(elem_types[i])
        count += "{:6} ".format(elem_count[i])
    print(types)
    print(count)

#######################################################################
### 有効なノードおよびエレメントからなる Verilog記述を生成する
def generate_verilog():
    global node_list, elem_list
    vlines_new = []
    vlines_new.append(vlines[0])
    for n_ix in range(len(node_list)):
        if node_list[n_ix].valid == True:
            vlines_new.append(vlines[node_list[n_ix].line])
    for e_ix in range(len(elem_list)):
        if elem_list[e_ix].valid == True and elem_list[e_ix].type != 'input':
            vlines_new.append(elem_list[e_ix].text)
    vlines_new.append('endmodule')
    return vlines_new

#######################################################################
############################################## ここからがメインルーチン
#######################################################################

### 入出力ファイル名を設定する
input_file_name = sys.argv[1]
output_file_name = re.sub(r'_join$','',re.sub(r'.v$','',sys.argv[1]))+'_sdff.v'

### Verilogファイルを読み込む
with open(input_file_name) as fv:
    vlines = [s.replace('\n', '') for s in fv.readlines()]
print("{:-8} lines :".format(len(vlines)), input_file_name)

### Verilog記述を走査する
scan_verilog()
print_info()

### 無駄な assign文を無くす
remove_dummy_assign()

### sdff に統合可能な mux + dff を探す
find_sdff()

### 新しい Verilog ファイルを出力する
vlines_new = generate_verilog()
with open(output_file_name,'w') as fnv:
    for i in range(len(vlines_new)):
        fnv.write(vlines_new[i]+'\n')
print("{:-8} lines :".format(len(vlines_new)), output_file_name)
print_info()


#print('### no fanout')
#for i in range(len(node_list)):
#    if node_list[i].fanout == 0:
#        print(f'{i}: {node_list[i].type}, {node_list[i].name}, {node_list[i].line}, {node_list[i].width}, {node_list[i].fanout}, {node_list[i].driver}')
#print('### no driver')
#for i in range(len(node_list)):
#    if len(node_list[i].driver) == 0:
#        print(f'{i}: {node_list[i].type}, {node_list[i].name}, {node_list[i].line}, {node_list[i].width}, {node_list[i].fanout}, {node_list[i].driver}')
#print('### multiple driver')
#for i in range(len(node_list)):
#    if len(node_list[i].driver) > 1:
#        print(f'{i}: {node_list[i].type}, {node_list[i].name}, {node_list[i].line}, {node_list[i].width}, {node_list[i].fanout}, {node_list[i].driver}')
#print(node_dict)
#for i in range(len(elem_list)):
#    print(f'{i}: {elem_list[i].type}, {elem_list[i].name}, {elem_list[i].line}, {elem_list[i].text}, ')
#print(len(elem_list))