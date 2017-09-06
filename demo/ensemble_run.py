import tensorflow as tf
import numpy as np
import cPickle as pkl
from src import utilizer
from src import model_cnn as main_model
from src import config
def main(_):
    # load data
    batch_size = config.batch_size

    meta_data_path = 'data/meta.pkl'
    meta_data = pkl.load(open(meta_data_path, 'rb'))
    label_class = meta_data['n_y']
    label_ind_map = meta_data['dl']

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
    print('label to index map', label_ind_map)

    # build graph
    tf.reset_default_graph()
    # gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.9, allow_growth=True)
    gpu_options = tf.GPUOptions(allow_growth=True)
    sess = tf.InteractiveSession(config=tf.ConfigProto(gpu_options=gpu_options, allow_soft_placement=True))

    model = main_model.Model(label_class, maxlen, W_embedding)
    sess.run(tf.global_variables_initializer())

    pro_ensemble = []
    for i in range(10):
        # load parameter
        model_path = 'model/model' + str(i) + 'model.ckpt'
        # graph_path = model_path + '.meta'
        model.saver.restore(sess, model_path)
        probability = model.predict(sess, W_test, L_test, int(batch_size / 1))
        pro_ensemble.append(probability)

    print('result:', pro_ensemble)


if __name__ == '__main__':
    tf.app.run()