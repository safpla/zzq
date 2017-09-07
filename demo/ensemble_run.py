from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
import numpy as np
import cPickle as pkl
import sys
import os
import model_info

sys.path.append("..")
from src import utilizer
from src import model_cnn as model_cnn_lishen
from src import config


def label_decoding(label, ind_label_map):
    label_chn = ''
    for i in range(len(label)):
        if label[i] == 1:
            label_chn = label_chn + ind_label_map[i] + ' '
    return label_chn.strip()


def implement_model(model, model_path, model_name, sents):
    gpu_options = tf.GPUOptions(allow_growth=True)
    sess = tf.InteractiveSession(config=tf.ConfigProto(gpu_options=gpu_options, allow_soft_placement=True))
    sess.run(tf.global_variables_initializer())
    saver = tf.train.Saver(max_to_keep=10)
    p = []
    for i in range(10):
        model_path = os.path.join(model_path, model_name + str(i) + '.ckpt')
        saver.restore(sess, model_path)
        p8s = model.predict(sess, sents)
        p.append(p8s)
    return p


def vote_ensemble(label_dict, perf_dict, num_sample):
    label = np.zeros((10, num_sample, 8), dtype=np.float32)
    for one_label in label_dict.values():
        label = label + np.asarray(one_label, dtype=np.float32)
    label = label/len(label_dict)
    label = label.mean(0)
    return label


def main(_):
    # load data
    batch_size = config.batch_size
    meta_data_path = '../data/meta.pkl'
    meta_data = pkl.load(open(meta_data_path, 'rb'))
    label_class = meta_data['n_y']
    label_ind_map = meta_data['dl']
    ind_label_map = {}
    for (k, v) in label_ind_map.items():
        ind_label_map[v] = k

    embedding_file_path = '../data/embedding_data.p'
    embedding_file = open(embedding_file_path, 'r')
    embeddings = pkl.load(embedding_file)
    embedding_file.close()
    W_embedding = np.asarray(embeddings["pretrain"]["word_embedding"], dtype=np.float32)
    maxlen = embeddings['maxlen']

    test_data = open('train_data.data', 'r').readlines()
    sents, _, L_test = utilizer.get_train_data(test_data, maxlen, 0)
    num_sample = len(sents)
    sents = np.asarray(sents)
    L_test = np.asarray(L_test)

    print('W_test shape:', sents.shape)
    print('L_test shape:', L_test.shape)
    print('W_embedding shape', W_embedding.shape)
    print('maxlen:', maxlen)
    print('Label class:', label_class)
    print('label to index map:')
    for (k, v) in label_ind_map.items():
        print('\t', k.encode('utf8'), ':', v)
    print('batch_size:', batch_size)

    # implement Li Shen's model
    g1 = tf.Graph()
    label_dict = {}
    perf_dict = {}

    with g1.as_default():
        model = model_cnn_lishen.Model(label_class, maxlen, W_embedding)
        model_path = model_info.model_cnn_lishen.model_path
        model_name = model_info.model_cnn_lishen.model_name
        multi_label = implement_model(model, model_path, model_name, sents)
        # dimensionality of multi_label is: 10 * num_sample * 8
        label_dict['model_cnn_lishen'] = multi_label
        perf_dict['model_cnn_lishen'] = model_info.model_cnn_lishen.performance

    labels = vote_ensemble(label_dict, perf_dict, num_sample)

    predict_label_path = 'predict.label'
    predict_label = open(predict_label_path, 'w')
    for label in labels:
        label_chn = label_decoding(label, ind_label_map)
        predict_label.write(label_chn.encode('utf8'))
        predict_label.write('\n')
    predict_label.close()


if __name__ == '__main__':
    tf.app.run()
