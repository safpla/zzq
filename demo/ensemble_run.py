import tensorflow as tf
import numpy as np
import pickle as pkl
import sys
import os
import model_info

sys.path.append("..")
sys.path.append("../xwd")
sys.path.append("../src")
from src import utilizer
from src import model_cnn as model_cnn_lishen
from xwd.cnn import CNNInterface
from src import config


def label_decoding(label, ind_label_map):
    label_chn = ''
    for i in range(len(label)):
        if label[i] > 0.5:
            label_chn = label_chn + ind_label_map[i] + ' '
    return label_chn.strip()


def implement_model(model, model_path, model_name, sents):
    configproto = tf.ConfigProto()
    configproto.gpu_options.allow_growth = True
    configproto.allow_soft_placement = True
    with tf.Session(config=configproto) as sess:
        sess.run(tf.global_variables_initializer())
        p = []
        for i in range(10):
            model_full_path = model_path + '/' + model_name[i]
            print("model_path:",model_full_path)
            model.restore(sess, model_full_path)
            print('cross_validation model %d is restored' %(i))
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
    embedding_file = open(embedding_file_path, 'rb')
    embeddings = pkl.load(embedding_file)
    embedding_file.close()
    W_embedding = np.asarray(embeddings["pretrain"]["word_embedding"], dtype=np.float32)
    maxlen = embeddings['maxlen']

    test_data = open('train_data.data', 'r').readlines()
    sents, _, L_test = utilizer.get_train_data_full(test_data, maxlen, 0)
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

    perf_dict = {}
    label_dict = {}

    # implement Li Shen's model
    print('start Li Shen''s model')
    g1 = tf.Graph()
    with g1.as_default():
        model = model_cnn_lishen.Model(label_class, maxlen, W_embedding)
        model_path = model_info.model_cnn_lishen.model_path
        model_name = model_info.model_cnn_lishen.model_name
        multi_label = implement_model(model, model_path, model_name, sents)
        # dimensionality of multi_label is: 10 * num_sample * 8
        label_dict['model_cnn_lishen'] = multi_label
        perf_dict['model_cnn_lishen'] = model_info.model_cnn_lishen.performance
    """

    # implement Xu Weidi's cnn mode
    print('start Xu Weidi''s cnn model')
    g2 = tf.Graph()
    with g2.as_default():
        model = CNNInterface()
        model_path = model_info.model_cnn_xwd.model_path
        model_name = model_info.model_cnn_xwd.model_name
        multi_label = implement_model(model, model_path, model_name, sents)
        label_dict['model_cnn_xwd'] = multi_label
        perf_dict['model_cnn_xwd'] = model_info.model_cnn_xwd.performance
    """
    for i in range(10):
        print(multi_label[i][0])
    

    labels = vote_ensemble(label_dict, perf_dict, num_sample)

    predict_label_path = 'predict.label'
    predict_label = open(predict_label_path, 'w')
    for label in labels:
        label_chn = label_decoding(label, ind_label_map)
        predict_label.write(label_chn)
        predict_label.write('\n')
    predict_label.close()


if __name__ == '__main__':
    tf.app.run()
