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


def var_length(track):
    """ Calculate variable-length value from 0th element and return the rest. """
    dt = ""
    while True:
        flag = track[0]["bin"][0]
        dt = dt + track[0]["bin"][1:]
        track = track[1:]
        if  flag == "0":
            break
    return b2i(dt), track


def note_to_cde(note_num):
    """ convert note_num(int 21~108) to CDE notation(str A0~C8). """
    # ex) 60->c4, 61->c#4, ..., 72->c5
    cde_list = ["c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "b"]
    n = (note_num // 12) -1
    cde = cde_list[note_num % 12]
    return cde + str(n)
    

# global
prev_c = ""


def event(track):
    """ Extract event-status and event-data from 0th element. """
    global prev_c
    if track[0]["bin"][0] == "1":
        c = track[0]["hex"]
        running = 0
    else:
        # running status
        c = prev_c
        running = 1
    prev_c = c
    event_data = {}
    if   c[0] == "8":
        # note off
        status = "note_off"
        event_data["ch_num"] = c[1]
        event_data["note_num"] = b2i(track[1-running]["bin"])
        event_data["vel"] = b2i(track[2-running]["bin"])
        track = track[3-running:]
    elif c[0] == "9":
        # note on
        status = "note_on"
        event_data["ch_num"] = c[1]
        event_data["note_num"] = b2i(track[1-running]["bin"])
        event_data["vel"] = b2i(track[2-running]["bin"])
        track = track[3-running:]
    elif c[0] == "b":
        # control change
        status = "control_change"
        event_data["ch_num"] = c[1]
        event_data["control_num"] = b2i(track[1-running]["bin"])
        event_data["data"] = b2i(track[2-running]["bin"])
        track = track[3-running:]
    elif c    == "f0":
        # sysex
        status = "sysex"
        data_len, r  = var_length(track[1:])
        event_data["ex_message"] = r[:data_len]
        track = r[data_len+1:]
        print "Error: sysex exists!!!"
    elif c    == "f7":
        # sysex
        status = "sysex"
        data_len, r  = var_length(track[1:])
        event_data["ex_message"] = r[:data_len]
        track = r[data_len:]
        print "Error: sysex exists!!!"
    elif c   ==  "c0":
        # sound?
        status = "sound"
        event_data["sound"] = track[1]["hex"]
        track = track[2:]
    elif c    == "ff":
        # meta event
        et = track[1]["hex"] # event type
        if   et == "00":
            if not track[2]["hex"] == "02":
                print "Error Sequence Number"
            status = "seq_num"
            event_data["seq_num"] = track[3]["hex"]+track[4]["hex"]
            track = track[5:]
        elif et == "01":
            status = "text"
            data_len, r = var_length(track[2:])
            event_data["text"] = r[:data_len]
            track = r[date_len:]
        elif et == "02":
            status = "copyright_notice"
            data_len, r = var_length(track[2:])
            event_data["copyright_notice"] = r[:data_len]
            track = r[date_len:]
        elif et == "03":
            status = "seq/track_name"
            data_len, r = var_length(track[2:])
            event_data["seq/track_name"] = r[:data_len]
            track = r[date_len:]
        elif et == "04":
            status = "instrument_name"
            data_len, r = var_length(track[2:])
            event_data["instrument_name"] = r[:data_len]
            track = r[date_len:]
        elif et == "05":
            status = "lylic"
            data_len, r = var_length(track[2:])
            event_data["lylic"] = r[:data_len]
            track = r[date_len:]
        elif et == "21":
            status = "port"
            event_data["port"] = track[3]["hex"]
            track = track[4:]
        elif et == "2f":
            if not track[2]["hex"] == "00":
                print "Error end of track"
            status = "end_of_track"
            track = track[3:]
        elif et == "51":
            if not track[2]["hex"] == "03":
                print "Error tempo"
            status = "set_tempo"
            # usec
            event_data["tempo"] = b2i("".join([i["bin"] for i in track[3:6]]))
            track = track[6:]
        elif et == "58":
            if not track[2]["hex"] == "04":
                print "Error time signature"
            status = "time_signature"
            event_data["nn"] = track[3]["hex"]
            event_data["dd"] = track[4]["hex"]
            event_data["cc"] = track[5]["hex"]
            event_data["bb"] = track[6]["hex"]
            track = track[7:]
        elif et == "59":
            if not track[2]["hex"] == "02":
                print "Error key signature"
            status = "key_signature"
            event_data["sf"] = track[3]["hex"]
            event_data["ml"] = track[4]["hex"]
            track = track[5:]
        else:
            status = "unknown meta"
            print "Unknown meta: ", track[:3]
    else:
        status = "unknown"
        print "Unknown status: ", track[:3]
    return status, event_data, track

def read_track(track):
    ret_list = []
    content = track[8:] # remove chunk-type and length
    rest = content
    while rest:
        dt, rest = var_length(rest)
        print 
        print "dt=", dt
        status, event_data, rest = event(rest)# TODO: runnning status rule: keep prev_status
        print "status=", status
        print "event_data=", event_data
        if status=="note_on":
            ret_list.append([dt, event_data])
    return ret_list


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

    notes = read_track(tracks[0][:502])
    a = [[n[0], n[1]["note_num"]] for n in notes if n[1]["vel"] > 0]# dt, note_num
    b = [[i[0], note_to_cde(i[1])]for i in a]
    ts = [n[0] for n in notes]

    # dt -> t
    cur_t = 0
    hoge = []
    for n in notes:
        cur_t += n[0]
        if n[1]["vel"]>0:
            hoge.append([cur_t, n[1]["note_num"]])
    import numpy as np
    import matplotlib.pyplot as plt
    plt.plot(np.array([n[1] for n in hoge]))

    # track
    for track in tracks:
        pass


#    hex_str = "".join(hex_data)

    sum = 0
    for b,h in zip(bin_data, hex_data):
        if not "{:02x}".format(b2i(b)) == h:
            sum += 1
    print sum
