import tensorflow as tf
import json
import cPickle as pkl
import thulac


def get_data_extract(input_json):
    ft = open('demo/data.txt0', 'w')
    fl = open('demo.data.label', 'w')
    meta_data_path = 'data/meta.pkl'
    meta_data = pkl.load(open(meta_data_path, 'rb'))
    label_class = meta_data['n_y']
    l = [0] * label_class

    f = open(input_json, 'r')
    data = json.load(f)
    for line in data:
        fl.write(''.join([str(ll) for ll in l[1:]]) + '\n')
        ft.write(' 000000000000000000 '.join(line['extract']) + '\n')
    ft.close()
    fl.close()


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
    input_json = 'input.json'
    output_json = 'output.json'
    dict_file_path = 'data.dict'

    get_data_extract(input_json)

    thu = thulac.thulac(seg_only=True, model_path='thulac_models')
    thu.cut_f('demo/data.txt0', 'demo/data.txt1')

    pad = 4
    train_txt = open('demo/data.txt0', 'r').readlines()
    train_label = open('demo/data.label', 'r').readlines()
    train_file = open('demo/train_data.data', 'w')
    dict_file = open(dict_file_path, 'r')
    vocab_sorted = pkl.load(dict_file)['vocab_sorted']
    vocab_id = {'#SOS#': 2}
    for v in range(len(vocab_sorted)):
        vocab_id[vocab_sorted[v][0]] = v + 3

    write_data(train_txt, train_label, train_file, pad, vocab_id)
    train_file.close()


if __name__ == '__main__':
    tf.app.run()
    """
    meta_data_path = 'data/meta.pkl'
    meta_data = pkl.load(open(meta_data_path, 'rb'))
    label_class = meta_data['n_y']
    label_ind_map = meta_data['dl']

    embedding_file_path = 'data/embedding_data.p'
    embedding_file = open(embedding_file_path, 'r')
    embeddings = pkl.load(embedding_file)
    embedding_file.close()
    embedding = embeddings["pretrain"]["word_embedding"]
    maxlen = embeddings['maxlen']
    """