# run in python2

import tensorflow as tf
import pickle as pkl

def write_data(txt, label, f, pad, vocab_id):
    for i in range(len(txt)):
        for line in txt[i].strip().split('000000000000000000'):
            line = line.split(' ')
            l_tmp = []
            for w0 in line:
                if w0 in vocab_id:
                    w0_id = vocab_id[w0]
                else:
                    w0_id = 1
                l_tmp.append(w0_id)

            l = [0] * pad
            l.extend(l_tmp)
            l.extend([0] * pad)
            f.write(' '.join([str(n) for n in l]) + '\t')
        y = [n for n in label[i].strip()]
        f.write(','.join(y))
        f.write('\n')


def main(_):
    dict_file_path = '../data/data.dict'
    pad = 4
    train_txt = open('data.txt1', 'r').readlines()
    train_label = open('data.label', 'r').readlines()
    train_file = open('train_data.data', 'w')
    loaded = pkl.load(open(dict_file_path, 'r'))
    vocab_sorted = loaded['word']
    vocab_id = {'#SOS#': 2}
    for v in range(len(vocab_sorted)):
        vocab_id[vocab_sorted[v][0]] = v + 3
    print('vocab loaded')

    write_data(train_txt, train_label, train_file, pad, vocab_id)
    train_file.close()

if __name__ == '__main__':
    tf.app.run()

