#! /usr/bin/python3
import sys
import re

input_file_name = sys.argv[1]
output_file_name = re.sub(r'.v$','',sys.argv[1])+'_join.v'

### Verilogファイルを読み込む
with open(input_file_name) as fv:
        vlines = [s.replace('\n', '') for s in fv.readlines()]
print("{:-8} lines :".format(len(vlines)), input_file_name)

### 行数を削減する
join = 0
newvlines = [ ]
for vline in vlines:
	### 行中のコメントを削る
	vline = re.sub(r'\/\* _[0-9]+_ \*\/','',vline)
	### 空行をスキップする
	if re.search(r'^ *$',vline):
		continue
	### (* *) 形式のコメント行をスキップする
	if re.search(r'^ *\(\*.*\*\) *$',vline):
		continue
	### /* */ 形式のコメント行をスキップする
	if re.search(r'^ *\/\*.*\*\/ *$',vline):
		continue
	### 以下、endmodule 以外で ; で終わっていない行は後続の行と連結する処理
	if join == 0:
		if re.search(r'^ *endmodule *$',vline):
			newvlines.append(vline + '\n')
		elif re.search(r'^.*[^;] *$',vline):
			buf = vline
			join = 1
		else:
			newvlines.append(vline + '\n')
	else:
		if re.search(r'^ *endmodule *$',vline):
			buf = buf + ' ' + vline.strip()
			newvlines.append(buf + '\n')
			join = 0
		elif re.search(r'^.*[^;] *$',vline):
			buf = buf + ' ' + vline.strip()
		else:
			buf = buf + ' ' + vline.strip()
			newvlines.append(buf + '\n')
			join = 0
print("{:-8} lines :".format(len(newvlines)), output_file_name)

### 順序を整えて出力する
with open(re.sub(r'.v$','',sys.argv[1])+'_join.v','w') as fnv:
	### まず、module 文を出力する
	for i in range(len(newvlines)):
		if re.search(r'^ *module ',newvlines[i]):
			fnv.write(newvlines[i])
			newvlines[i] = ''
			break
	### 最初の endmodule 文までに登場する input 文を出力する
	n = 0
	for i in range(len(newvlines)):
		if re.search(r'^ *endmodule *$',newvlines[i]):
			break
		if re.search(r'^ *input ',newvlines[i]):
			fnv.write(newvlines[i])
			newvlines[i] = ''
			n += 1
	print("{:-8} lines : input".format(n))
	n = 0
	### 最初の endmodule 文までに登場する output 文を出力する	
	for i in range(len(newvlines)):
		if re.search(r'^ *endmodule *$',newvlines[i]):
			break
		if re.search(r'^ *output ',newvlines[i]):
			fnv.write(newvlines[i])
			newvlines[i] = ''
			n += 1
	print("{:-8} lines : output".format(n))
	n = 0
	### 最初の endmodule 文までに登場する wire 文を出力する
	for i in range(len(newvlines)):
		if re.search(r'^ *endmodule *$',newvlines[i]):
			break
		if re.search(r'^ *wire ',newvlines[i]):
			fnv.write(newvlines[i])
			newvlines[i] = ''
			n += 1
	print("{:-8} lines : wire".format(n))
	n = 0
	### 最初の endmodule 文までに登場する assign 文を出力する
	for i in range(len(newvlines)):
		if re.search(r'^ *endmodule *$',newvlines[i]):
			break
		if re.search(r'^ *assign ',newvlines[i]):
			fnv.write(newvlines[i])
			newvlines[i] = ''
			n += 1
	print("{:-8} lines : assign".format(n))
	n = 0
	### 最初の endmodule 文までに登場する \$lut インスタンスを出力する
	for i in range(len(newvlines)):
		if re.search(r'^ *endmodule *$',newvlines[i]):
			break
		if re.search(r'^ *\\\$lut ',newvlines[i]):
			fnv.write(newvlines[i])
			newvlines[i] = ''
			n += 1
	print("{:-8} lines : \$lut".format(n))
	n = 0
	### 最初の endmodule 文までに登場する \$add インスタンスを出力する	
	for i in range(len(newvlines)):
		if re.search(r'^ *endmodule *$',newvlines[i]):
			break
		if re.search(r'^ *\\\$add ',newvlines[i]):
			fnv.write(newvlines[i])
			newvlines[i] = ''
			n += 1
	print("{:-8} lines : \$add".format(n))
	n = 0
	### 最初の endmodule 文までに登場する \$sub インスタンスを出力する
	for i in range(len(newvlines)):
		if re.search(r'^ *endmodule *$',newvlines[i]):
			break
		if re.search(r'^ *\\\$sub ',newvlines[i]):
			fnv.write(newvlines[i])
			newvlines[i] = ''
			n += 1
	print("{:-8} lines : \$sub".format(n))
	n = 0
	### 最初の endmodule 文までに登場する \$mul インスタンスを出力する
	for i in range(len(newvlines)):
		if re.search(r'^ *endmodule *$',newvlines[i]):
			break
		if re.search(r'^ *\\\$mul ',newvlines[i]):
			fnv.write(newvlines[i])
			newvlines[i] = ''
			n += 1
	print("{:-8} lines : \$mul".format(n))
	n = 0
	### 最初の endmodule 文までに登場する \$mux インスタンスを出力する
	for i in range(len(newvlines)):
		if re.search(r'^ *endmodule *$',newvlines[i]):
			break
		if re.search(r'^ *\\\$mux ',newvlines[i]):
			fnv.write(newvlines[i])
			newvlines[i] = ''
			n += 1
	print("{:-8} lines : \$mux".format(n))
	n = 0
	### 最初の endmodule 文までに登場する \$dff インスタンスを出力する
	for i in range(len(newvlines)):
		if re.search(r'^ *endmodule *$',newvlines[i]):
			break
		if re.search(r'^ *\\\$dff ',newvlines[i]):
			fnv.write(newvlines[i])
			newvlines[i] = ''
			n += 1
	print("{:-8} lines : \$dff".format(n))
	n = 0
	### 以上に該当しない残りの行は、元通りの順番で出力する
	for i in range(len(newvlines)):
		if not(re.search(r'^ *$',newvlines[i])):
			fnv.write(newvlines[i])
			newvlines[i] = ''
			n += 1
	print("{:-8} lines : other".format(n))


