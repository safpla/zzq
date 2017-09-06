import config

import tensorflow as tf
import numpy as np

from src import utilizer


class Model:
    def __init__(self, label_class, maxlen, W_embedding):
        self.dropout_mlp = config.dropout_mlp
        self.norm_lim = config.norm_lim
        self.grad_lim = config.grad_lim
        self.filter_num = config.filter_num
        self.filter_lengths = config.filter_lengths
        self.label_class = label_class
        self.maxlen = maxlen

        # input
        self.w = tf.placeholder(tf.int32, [None, None], name='input_w')
        self.sl = tf.placeholder(tf.int32, [None], name='input_sl')
        self.y_ = tf.placeholder(tf.int32, [None, None], name='input_y')
        self.dropout_keep_prob_mlp = tf.placeholder(tf.float32, name='dropout_keep_prob_mlp')
        self.is_training = tf.placeholder(tf.bool, name='is_training')

        self.y_onehot = tf.one_hot(self.y_, depth=2)

        def mlp_weight_variable(shape):
            initial = tf.random_normal(shape=shape, stddev=0.01)
            mlp_W = tf.Variable(initial, name='mlp_W')
            return tf.clip_by_norm(mlp_W, self.norm_lim)

        def mlp_bias_variable(shape):
            initial = tf.zeros(shape=shape)
            mlp_b = tf.Variable(initial, name='mlp_b')
            return mlp_b

        def conv_weight_variable(shape):
            initial = tf.random_uniform(shape, maxval=0.01)
            conv_W = tf.Variable(initial, name='conv_W', dtype=tf.float32)
            return conv_W

        def conv_bias_variable(shape):
            initial = tf.zeros(shape=shape)
            conv_b = tf.Variable(initial, name='conv_b', dtype=tf.float32)
            return conv_b

        def conv1d(x, conv_W, conv_b):
            conv = tf.nn.conv1d(x,
                                conv_W,
                                stride=1,
                                padding='SAME',
                                name='conv')
            conv = tf.nn.bias_add(conv, conv_b)
            return conv

        # word embedding
        with tf.device('/cpu:0'), tf.name_scope('word_embedding'):
            word_embedding_table = tf.Variable(np.asarray(W_embedding), name='word_embedding_table')
            word_embedded = tf.nn.embedding_lookup(word_embedding_table, self.w)

        # word CNN
        with tf.name_scope('CNN'):
            self.cnn_size = self.filter_num * len(self.filter_lengths)

            conv_Ws = []
            conv_bs = []
            for i in self.filter_lengths:
                filter_shape = [i,
                                W_embedding.shape[1],
                                self.filter_num]
                conv_W = conv_weight_variable(filter_shape)
                conv_b = conv_bias_variable([self.filter_num])
                conv_Ws.append(conv_W)
                conv_bs.append(conv_b)

            cnn_outputs = []
            for i in xrange(len(self.filter_lengths)):
                conv = conv1d(word_embedded, conv_Ws[i], conv_bs[i])
                cnn_outputs.append(conv)
            cnn_outputs_concat = tf.concat(cnn_outputs, 2)
            cnn_outputs_concat_act = tf.nn.relu(cnn_outputs_concat, name='relu')

            # predict label
            self.label_hidden_state = tf.reduce_max(cnn_outputs_concat_act, axis=1)
            label_W = mlp_weight_variable([self.cnn_size, self.label_class * 2])
            label_b = mlp_bias_variable([self.label_class * 2])
            h_outputs = tf.matmul(self.label_hidden_state, label_W) + label_b
            self.y = tf.nn.softmax(tf.reshape(h_outputs, [-1, self.label_class, 2]))
            self.y = tf.clip_by_value(self.y, clip_value_min=1e-6, clip_value_max=1.0 - 1e-6)
            self.loss_label = tf.reduce_mean(-tf.reduce_sum(self.y_onehot * tf.log(self.y) + (1 - self.y_onehot) * tf.log(1 - self.y),
                                                            reduction_indices=[1]))
            self.prediction = tf.arg_max(self.y, -1)
            self.correct_prediction = tf.equal(tf.cast(self.prediction, tf.int32), self.y_)

            self.loss = self.loss_label

            # loss
            update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
            with tf.control_dependencies(update_ops):
                optimizer = tf.train.AdadeltaOptimizer(learning_rate=1.0, rho=0.95, epsilon=1e-08)
                gvs = optimizer.compute_gradients(self.loss)
                capped_gvs = [((tf.clip_by_norm(grad, self.grad_lim)), var) for grad, var in gvs]
                self.train_step = optimizer.apply_gradients(capped_gvs)
                # self.train_step = tf.train.AdadeltaOptimizer(learning_rate=1.0, rho=0.95, epsilon=1e-08).minimize(self.loss)
                # self.train_step = tf.train.RMSPropOptimizer(learning_rate=0.1).minimize(self.loss)

            # xhw added, 2017-09-05
            self.saver = tf.train.Saver(max_to_keep=10)
            # tvars = tf.trainable_variables()
            #
            # for var in tvars:
            #     print(var.name)
            # exit()

            # tf.global_variables_initializer().run()
            # w_batch = np.zeros([50, self.maxlen])
            # sl_batch = [self.maxlen for n in xrange(50)]
            # y_batch = np.zeros([50, self.label_class])
            # test = self.correct_prediction.eval({self.w: w_batch,
            #                                 self.sl: sl_batch,
            #                                 self.y_: y_batch,
            #                                 self.dropout_keep_prob_mlp: 1.0})
            # print(test)
            # print(np.asarray(test).shape)
            # exit()

    def temp_check(self, sess, w, t, sl, y):
        r = sess.run(self.tmp_var, feed_dict={self.w: w,
                                            self.t: t,
                                            self.sl: sl,
                                            self.y_: y,
                                            self.dropout_keep_prob_mlp: 1.0,
                                            self.dropout_keep_prob_cnn: 1.0,
                                            self.is_training: False})
        print(r)
        print(np.asarray(r).shape)
        exit()

    def train(self, w, sl, y):
        w_batch = w
        sl_batch = sl
        y_batch = y

        w_batch = utilizer.pad_list(w_batch.tolist())

        self.train_step.run({self.w: w_batch,
                            self.sl: sl_batch,
                            self.y_: y_batch,
                            self.dropout_keep_prob_mlp: self.dropout_mlp,
                            self.is_training: True})

    def test(self, sess, w, sl, y, batch_size):
        label_correct = 0
        loss = 0
        errors = []
        i = 0
        while i < len(w):
            w_batch = w[i: i + batch_size]
            sl_batch = sl[i: i + batch_size]
            y_batch = y[i: i + batch_size]
            i += batch_size

            w_batch = utilizer.pad_list(w_batch.tolist())

            r = sess.run([self.correct_prediction, self.loss],
                         feed_dict={self.w: w_batch,
                                    self.sl: sl_batch,
                                    self.y_: y_batch,
                                    self.dropout_keep_prob_mlp: 1.0,
                                    self.is_training: False})
            labels = r[0]
            loss += len(w_batch) * r[1]
            for n in xrange(len(labels)):
                l = labels[n]
                if l.all():
                    label_correct += 1
                else:
                    errors.append([w_batch[n], y_batch[n]])
        label_accuracy = 1.0 * label_correct / len(w)
        loss /= len(w)

        return label_accuracy, loss, errors


    def predict(self, sess, w, sl, batch_size):
    # xhw added, based on xqw's code, 2017-09-06
        i = 0
	ps = []
        while i < len(w):
            w_batch = w[i: i + batch_size]
            sl_batch = sl[i: i + batch_size]
            i += batch_size

            w_batch = utilizer.pad_list(w_batch.tolist())

            p = sess.run(self.y,
                         feed_dict={self.w: w_batch,
                                    self.sl: sl_batch,
                                    # self.y_: y_batch,
                                    self.dropout_keep_prob_mlp: 1.0,
                                    self.is_training: False})
	    ps.append(p)
	ps = np.concatenate(ps)
        # labels = np.argmax(r, axis=1)
        return ps
