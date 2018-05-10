setlocal
set syll_cnt_fn=cmudict_dev.json
set bf_fn=Bloom_filter_data.py
py -3 make_Bloom_filter.py %syll_cnt_fn% %bf_fn%  > outf
