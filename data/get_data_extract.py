# -*- coding:utf-8 -*-
import json
import operator
import numpy as np
import pickle as pkl

dt = {}
dl = {}

ft = open('data.txt0', 'w')
fl = open('data.label', 'w')

f0 = open('extract_file0.json', 'r')
data0 = json.load(f0)
f1 = open('extract_file1.json', 'r')
data1 = json.load(f1)

for i in data0:
    if i['DL'] not in dl:
        dl[i['DL']] = len(dl)
    for k in ['extract', ]:
        for c in i[k]:
            if c not in dt:
                dt[c] = 0
            dt[c] += 1

for i in data1:
    for k in i['XL'].replace('、', '，').split('，'):
        if k not in dl:
            dl[k] = len(dl)
    for k in ['extract', ]:
        for c in i[k]:
            if c not in dt:
                dt[c] = 0
            dt[c] += 1

print(dl)
f = open('meta.pkl', 'wb')
pkl.dump({'n_y': len(dl) - 1, 'dl': dl}, f, protocol=2)
f.close()

for i in data0:
    l = [0 for _ in dl]
    ddl = [k for k in dl]
    for k in range(len(ddl)):
        if i['DL'] == ddl[k]:
            l[k] = 1
    fl.write(''.join([str(ll) for ll in l[1:]]) + '\n')

    ts = []
    for k in ['extract', ]:
        t = ''
        for c in i[k]:
            if c in dt:
                t += c
        ts.append(t)
    ft.write(' 000000000000000000 '.join(ts) + '\n')

for i in data1:
    l = [0 for _ in dl]
    ddl = [k for k in dl]
    for k in range(len(ddl)):
        if ddl[k] in i['XL'].replace('、', '，').split('，'):
            l[k] = 1
    fl.write(''.join([str(ll) for ll in l[1:]]) + '\n')

    ts = []
    for k in ['extract', ]:
        t = ''
        for c in i[k]:
            if c in dt:
                t += c
        ts.append(t)
    ft.write(' 000000000000000000 '.join(ts) + '\n')
