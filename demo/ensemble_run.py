from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
import numpy as np
import cPickle as pkl
from ..src import utilizer
from ..src import model_cnn as main_model
from ..src import config
def class_decoding(l_multi, ind_label_map):
    label = ''
    for i in range(len(l_multi)):
        if l_multi[i] == 1:
            label = label + ind_label_map[i+1] + ' '
    if label == '':
        label = label + ind_label_map[0]
    return label


def main(_):
    # load data
    batch_size = config.batch_size

    meta_data_path = 'data/meta.pkl'
    meta_data = pkl.load(open(meta_data_path, 'rb'))
    label_class = meta_data['n_y']
    label_ind_map = meta_data['dl']
    ind_label_map = {}
    for (k, v) in label_ind_map.items():
        ind_label_map[v] = k

    embedding_file_path = 'data/embedding_data.p'
    embedding_file = open(embedding_file_path, 'r')
    embeddings = pkl.load(embedding_file)
    embedding_file.close()
    W_embedding = np.asarray(embeddings["pretrain"]["word_embedding"], dtype=np.float32)
    maxlen = embeddings['maxlen']

    test_data = open('demo/train_data.data', 'r').readlines()
    W_test, _, L_test = utilizer.get_train_data(test_data, maxlen, 0)
    W_test = np.asarray(W_test)
    L_test = np.asarray(L_test)

    print('W_test shape:', W_test.shape)
    print('L_test shape:', L_test.shape)
    print('W_embedding shape', W_embedding.shape)
    print('maxlen:', maxlen)
    print('Label class:', label_class)
    print('label to index map:')
    for (k, v) in label_ind_map.items():
        print('\t', k.encode('utf8'),':',v)

    print('batch_size:', batch_size)

    # build graph
    tf.reset_default_graph()
    # gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.9, allow_growth=True)
    gpu_options = tf.GPUOptions(allow_growth=True)
    sess = tf.InteractiveSession(config=tf.ConfigProto(gpu_options=gpu_options, allow_soft_placement=True))

    model = main_model.Model(label_class, maxlen, W_embedding)
    sess.run(tf.global_variables_initializer())

    p_ave = np.zeros((7, 2), dtype=np.float32)
    for i in range(10):
        # load parameter
        model_path = 'model/model' + str(i) + 'model.ckpt'
        # graph_path = model_path + '.meta'
        model.saver.restore(sess, model_path)
        probability = model.predict(sess, W_test, L_test, int(batch_size / 1))
    p_ave = p_ave + probability
    predict_label_path = 'demo/predict.label'
    predict_label = open(predict_label_path, 'w')
    num_samp, num_class, _ = p_ave.shape
    for isamp in range(num_samp):
        p = p_ave[isamp, :, :]
        l_multi = np.argmax(p,1)
        label = class_decoding(l_multi, ind_label_map)
        predict_label.write(label.encode('utf8'))
        predict_label.write('\n')
    predict_label.close()

if __name__ == '__main__':
    tf.app.run()
