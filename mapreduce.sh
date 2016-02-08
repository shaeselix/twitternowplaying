cat nowplaying.csv | mapper.py | sort -k1,1 | reducer.py > userplays.txt
