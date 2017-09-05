import numpy as np


def pad_list(lst):
    ll = 0
    for i in xrange(len(lst)):
        if ll < len(lst[i]):
            ll = len(lst[i])
    for i in xrange(len(lst)):
        lst[i].extend([0]*(ll-len(lst[i])))
    return np.asarray(lst)


def read_data(l):
    tmp_w = []

    tmp_l = l.strip().split('\t')

    for n in tmp_l[:-1]:
    # for n in tmp_l[0:2]:
        n = n.split(' ')
        for c in n:
            if c != '0':
                tmp_w.append(int(c))

    tmp_y = [int(y) for y in tmp_l[-1].split(',')]

    for i in xrange(4):
        tmp_w.insert(0, 0)
        tmp_w.append(0)

    tmp_len = len(tmp_w)

    return tmp_w, tmp_y, tmp_len


def read_data_fake(l, maxlen, fake_data_num):
    tmp_ws = []
    tmp_ys = []
    tmp_lens = []

    tmp_l = l.strip().split('\t')

    for fn in xrange(fake_data_num):
        for n in tmp_l[:-1]:
        # for n in tmp_l[0:2]:
            tmp_w = []
            n = n.split(' ')
            for c in n:
                if c != '0':
                    tmp_w.append(int(c[0]))

            tmp_y = [int(y) for y in tmp_l[-1].split(',')]

            tmp_len = len(tmp_w)
            if tmp_len < 10:
                continue

            s = np.random.randint(0, len(tmp_w) / 2)
            e = np.random.randint(len(tmp_w) / 2, len(tmp_w))
            tmp_w = tmp_w[s:e]
            tmp_w = tmp_w[:maxlen]

            for i in xrange(4):
                tmp_w.insert(0, 0)
                tmp_w.append(0)

            tmp_len = len(tmp_w)

            tmp_ws.append(tmp_w)
            tmp_ys.append(tmp_y)
            tmp_lens.append(tmp_len)

    return tmp_ws, tmp_ys, tmp_lens


def padding(l, length):
    while len(l) < length:
        l.append(0)
    return l


def get_train_data(data, maxlen, fake_data_num):
    W = []
    Y = []
    L = []
    for l in data:
        if fake_data_num > 0:
            tmp_w, tmp_y, tmp_len = read_data_fake(l, maxlen, fake_data_num)
            W += tmp_w
            Y += tmp_y
            L += tmp_len
        else:
            tmp_w, tmp_y, tmp_len = read_data(l)
            if tmp_len < 10:
                continue
            W.append(tmp_w)
            Y.append(tmp_y)
            L.append(tmp_len)
    for y in range(len(Y)):
        Y[y] = [j for j in Y[y]]

    return W, Y, L