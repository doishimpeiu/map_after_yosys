presynthesis_sdff.v: presynthesis_join.v find_sdff.py
	./find_sdff.py presynthesis_join.v

presynthesis_join.v: presynthesis.v join_lines.py
	./join_lines.py presynthesis.v

presynthesis.v: nngenmod.v opt.ys mytechmap.v
	yosys < opt.ys | tee opt.log

clean:
	rm -f opt.log presynthesis.v presynthesis_bb.v presynthesis_join.v
