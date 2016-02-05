import sys

current_user = None
current_artist = None
next_artist = None
current_out = None
count = 0

for l in sys.stdin:
    fields = l.split(',')
    if fields[0] == current_user:
        if fields[1] == current_artist:
            count = count + int(fields[2])
        else:
            current_out = '%s,%s,%s' % (current_out,current_artist,count)
            current_artist = fields[1]
            count = int(fields[2])
    else:
        if current_out != current_user:
            print('%s,%s,%s' % (current_out,current_artist,count))
        current_user = fields[0]
        current_artist = fields[1]
        current_out = current_user
        count = int(fields[2])

if current_out != current_user:
    print('%s,%s,%s' % (current_out,current_artist,count))