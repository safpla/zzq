# -*- coding: utf-8 -*-

import pickle as pkl
import numpy as np
import operator
import re

# from docopt import docopt


def main():
    # <<<<< origin, changed by xuhaowen, 2017-09-08
    #args = docopt("""
    #    Usage:
    #       process.py [options]

    #   Options:
    #       --word_embedding_dims NUM       The dimension of words [default: 100]
    #       --train_data STRING             [default: data]
    #   """)
    #word_embedding_dims = int(args['--word_embedding_dims'])
    #train_path = args['--train_data']
    # =====
    word_embedding_dims = 100
    train_path = 'data'
    # >>>>>

    global maxlen
    maxlen = 0
    pad = 4

    train_txt = open(train_path + ".txt1", 'r').readlines()
    train_label = open(train_path + ".label", 'r').readlines()

    train_file_path = "train_" + train_path + ".data"
    train_file = open(train_file_path, 'w')
    embedding_file_path = "embedding_" + train_path + ".p"

    dict_file_path = train_path + ".dict"
    dict_file = open(dict_file_path, 'wb')

    # VOCAB ID
    print("vocab dict")
    vocab = {}
    for l in train_txt:
        l = l.strip().split()
        for w in l:
            if w in vocab:
                vocab[w] += 1
            else:
                vocab[w] = 1

    vocab_sorted = sorted(vocab.items(), key=operator.itemgetter(1), reverse=True)

    vocab_id = {'#SOS#': 2}
    for v in range(len(vocab_sorted)):
        vocab_id[vocab_sorted[v][0]] = v + 3

    def padding(s):
        s_tmp = []
        for i in range(pad):
            s_tmp.append(0)
        for w in s:
            s_tmp.append(w)
        for i in range(pad):
            s_tmp.append(0)
        return s_tmp

    # data to file
    def write_data(txt, label, f):
        global maxlen
        for i in range(len(txt)):
            for l in txt[i].strip().split('000000000000000000'):
                l_tmp = []
                l = l.split(' ')
                for j in range(len(l)):
                    w0 = l[j]

                    if w0 in vocab_id:
                        w0_id = vocab_id[w0]
                    else:
                        w0_id = 1
                    l_tmp.append(w0_id)

                if len(l_tmp) > maxlen:
                    maxlen = len(l_tmp)
                l_tmp = padding(l_tmp)

                f.write(' '.join([str(n) for n in l_tmp]) + '\t')

            y = [n for n in label[i].strip()]
            f.write(','.join(y))
            f.write('\n')

    print("write train data")
    write_data(train_txt, train_label, train_file)

    print("maxlen: %d" % maxlen)

    word_vec = {}
    with open("chinesegigawordv5.deps.vec", 'r') as f:
        for l in f:
            l = l.strip().split()
            i = 1
            v = []
            while i < len(l):
                v.append(float(l[i]))
                i += 1
            word_vec[l[0]] = np.asarray(v)

    word_embedding = list()
    word_embedding_rand = list()
    word_embedding.append(np.zeros(word_embedding_dims, dtype='float32'))
    word_embedding_rand.append(np.zeros(word_embedding_dims, dtype='float32'))
    word_embedding.append(np.random.uniform(-0.25, 0.25, word_embedding_dims))
    word_embedding.append(np.random.uniform(-0.25, 0.25, word_embedding_dims))
    word_embedding_rand.append(np.random.uniform(-0.25, 0.25, word_embedding_dims))
    word_embedding_rand.append(np.random.uniform(-0.25, 0.25, word_embedding_dims))
    for i in range(len(vocab_sorted)):
        if vocab_sorted[i][0] in word_vec:
            word_embedding.append(word_vec[vocab_sorted[i][0]])
        else:
            word_embedding.append(np.random.uniform(-0.25, 0.25, word_embedding_dims))
        word_embedding_rand.append(np.random.uniform(-0.25, 0.25, word_embedding_dims))

    # changed by xuhaowen, 2017-09-08, for python3 compatibility
    # f = open(embedding_file_path, 'w')
    f = open(embedding_file_path, 'wb')
    
    pkl.dump({"pretrain": {"word_embedding": word_embedding},
              "random": {"word_embedding": word_embedding_rand},
              "maxlen": maxlen + 2 * pad}, f)
    f.close()

    pkl.dump({"word": vocab_sorted}, dict_file)
    dict_file.close()

    train_file.close()

    def shuffle(path):
        data = open(path, 'r').readlines()
        np.random.shuffle(data)
        f = open(path + ".shuffle", 'w')
        for l in data:
            f.write(l)
        f.close()

    shuffle(train_file_path)

if __name__ == '__main__':
    main()
