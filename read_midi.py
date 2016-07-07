#!/usr/bin/env python
# -*- coding: utf-8 -*-

def b2i(bin_str):
    """ string of binary 0/1 to int (ex. "0110" -> 6) """
    ret = 0
    for n, bit in enumerate(reversed(bin_str)):
        if not int(bit) in [0, 1]:
            return -1
        else:
            ret += int(bit) * (2**n)
    return ret

def split_data(data):
    """ chunk """
    ret = []
    rest = data
    while rest:
        if [d["hex"] for d in data[:4]] in [['4d', '54', '68', '64'],
                                            ['4d', '54', '72', '6b']]:
            chunk_len = b2i("".join([d["bin"] for d in rest[4:8]]))
            chunk = rest[0:8+chunk_len]
            ret.append(chunk)
            rest = rest[8+chunk_len:]
        else:
            print "Error. "
    return ret

def read_header(header):
    """ extract information from header """
    bins = [d["bin"] for d in header]
    f = b2i("".join(bins[8:10]))
    tn = b2i("".join(bins[10:12]))
    if bins[12][0] == "0":
        # 4分音符あたりの分解能?
        tu = b2i("".join(bins[12:14]))
    else:
        print "Error."

    return f, tn, tu

def read_track(track):
    content = track[8:] # remove chunk-type and length
    pass

if __name__ == '__main__':
    with open('data/goldberg.mid', 'rb') as f:
        raw_data = f.read()

    bin_data = ["{:08b}".format(ord(d)) for d in raw_data]
    hex_data = ["{:02x}".format(ord(d)) for d in raw_data]
#    data = {"bin":bin_data, "hex":hex_data}
    data = [{"bin": b, "hex":h} for b, h in zip(bin_data, hex_data)]    

    chunks = split_data(data)
    
    tracks = []
    for c in chunks:
        if [d["hex"] for d in c[:4]] == ['4d', '54', '68', '64']:
            # header
            header = c
        elif [d["hex"] for d in c[:4]] == ['4d', '54', '72', '6b']:
            # track
            tracks.append(c)
    
    # header
    form, track_num, time_unit = read_header(header)

    # track
    for track in tracks:
        pass


#    hex_str = "".join(hex_data)

    sum = 0
    for b,h in zip(bin_data, hex_data):
        if not "{:02x}".format(b2i(b)) == h:
            sum += 1
    print sum
