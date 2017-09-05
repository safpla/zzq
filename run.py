from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
import numpy as np
import time
import cPickle as pkl
import sys

from src import config
from src import model_cnn as main_model
from src import utilizer

from docopt import docopt

np.random.seed(3306)

np.set_printoptions(linewidth=200)


def train(train_data_path, test_data_path):
    embedding_path = 'data/embedding_data.p'
    dict_path = 'data/data.dict'
    meta_data_path = 'data/meta.pkl'
    model_save_path = 'model/model1/model.ckpt'

    fake_data_num = config.fake_data_num
    batch_size = config.batch_size
    checkpoint_num = config.checkpoint_num
    timedelay_num = config.timedelay_num

    print('Loading Data...')

    dictionary_data = pkl.load(open(dict_path, 'r'))['word']
    dictionary = {}
    for d in dictionary_data:
        dictionary[len(dictionary) + 3] = d[0]

    meta_data = pkl.load(open(meta_data_path, 'rb'))

    label_class = meta_data['n_y']

    train_data = open(train_data_path, 'r').readlines()#[:1000]
    dev_data = train_data[int(len(train_data) * 0.9):]
    train_data = train_data[:int(len(train_data) * 0.9)]
    test_data = open(test_data_path, 'r').readlines()#[:1000]

    embedding_file = open(embedding_path, 'r')
    embeddings = pkl.load(embedding_file)
    embedding_file.close()

    W_embedding = np.asarray(embeddings["pretrain"]["word_embedding"], dtype=np.float32)
    maxlen = embeddings['maxlen']

    W_train, Y_train, L_train = utilizer.get_train_data(train_data, maxlen, 0)
    W_dev, Y_dev, L_dev = utilizer.get_train_data(dev_data, maxlen, 0)
    W_test, Y_test, L_test = utilizer.get_train_data(test_data, maxlen, 0)

    W_train = np.asarray(W_train)
    L_train = np.asarray(L_train)
    Y_train = np.asarray(Y_train)

    W_dev = np.asarray(W_dev)
    L_dev = np.asarray(L_dev)
    Y_dev = np.asarray(Y_dev)

    W_test = np.asarray(W_test)
    L_test = np.asarray(L_test)
    Y_test = np.asarray(Y_test)

    print('W_train shape:', W_train.shape)
    print('L_train shape:', L_train.shape)
    print('Y_train shape:', Y_train.shape)

    print('W_dev shape:', W_dev.shape)
    print('L_dev shape:', L_dev.shape)
    print('Y_dev shape:', Y_dev.shape)

    print('W_test shape:', W_test.shape)
    print('L_test shape:', L_test.shape)
    print('Y_test shape:', Y_test.shape)

    print('W_embedding shape:', W_embedding.shape)
    print('maxlen:', maxlen)
    print('Label class:', label_class)

    tf.reset_default_graph()
    # gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.9, allow_growth=True)
    gpu_options = tf.GPUOptions(allow_growth=True)
    sess = tf.InteractiveSession(config=tf.ConfigProto(gpu_options=gpu_options, allow_soft_placement=True))

    model = main_model.Model(label_class, maxlen, W_embedding)

    sess.run(tf.global_variables_initializer())

    best_label = 0
    best_loss = 100
    test_label = 0
    test_loss = 0
    test_errors = []
    batches = 0
    timedelay = 0
    start_time = time.time()
    i = 0
    while timedelay < timedelay_num:
        if i > len(W_train):
            i = 0

        w_batch = W_train[i: i + batch_size]
        sl_batch = L_train[i: i + batch_size]
        y_batch = Y_train[i: i + batch_size]

        # model.temp_check(sess, w_batch, t_batch, sl_batch, y_batch)
        # exit()

        i += batch_size
        batches += 1

        model.train(w_batch, sl_batch, y_batch)

        if batches % checkpoint_num == 0:
            train_label, train_loss, _ = model.test(sess, w_batch, sl_batch, y_batch, batch_size)
            dev_label, dev_loss, _ = model.test(sess, W_dev, L_dev, Y_dev, int(batch_size / 1))

            if best_label < dev_label:
                timedelay = 0
            else:
                timedelay += 1

            if best_label < dev_label:
                best_label = dev_label
                test_label, test_loss, test_errors = model.test(sess, W_test, L_test, Y_test, int(batch_size / 1))
            if best_loss > dev_loss:
                best_loss = dev_loss

            sys.stdout.write("Batches: %d" % batches)
            sys.stdout.write("\tBatch Time: %.4fs" % (1.0 * (time.time() - start_time) / checkpoint_num))

            sys.stdout.write("\nTrain Label: %.6f" % train_label)
            sys.stdout.write("\tTrain Loss: %.6f" % train_loss)

            sys.stdout.write("\nValid Label: %.6f" % dev_label)
            sys.stdout.write("\tValid Loss: %.6f" % dev_loss)

            sys.stdout.write("\nTest Label: %.6f" % test_label)
            sys.stdout.write("\tTest Loss: %.6f" % test_loss)

            sys.stdout.write("\nBest Label: %.6f" % best_label)
            sys.stdout.write("\tBest Loss: %.6f" % best_loss)

            sys.stdout.write("\n\n")

            start_time = time.time()

            save_path = model.saver(sess, model_save_path, global_steps=(batches + 1))
            print('save the model in ', save_path)

    return test_label, test_errors


def main(_):
    f_errors_name = 'results/error' + str(time.time()) + '.log'
    accs_label = []
    for i in xrange(10):
        train_data_path = 'data/cv/train.' + str(i)
        test_data_path = 'data/cv/test.' + str(i)
        acc_label, test_errors = train(train_data_path, test_data_path)
        accs_label.append(acc_label)
        print(np.mean(accs_label))
        print(accs_label)

        f_errors = open(f_errors_name, 'a')
        for e in test_errors:
            for v in e[0]:
                if v > 2:
                    f_errors.write(str(v - 2) + ' ')
            f_errors.write('\t')
            for v in e[1]:
                f_errors.write(str(v))
            f_errors.write('\n')


if __name__ == '__main__':
    tf.app.run()
