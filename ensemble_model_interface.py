# -*- coding:utf-8 -*-
from abc import ABCMeta, abstractmethod

class EnsembleModelInterface(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def txt2ind(self, txt):
        """
        You need to provide this function if you didn't use Li Shen's preprocessing, or you can just pass
        :param txt: list of strings
        :return: list of strings' index, it will be used as the input of "predict" function
        """
        return

    @abstractmethod
    def predict(self, sess, sent):
        """
        Do prediction
        :param sess: tf.Session()
        :param sent: input sentences
                     sent is a list of sentences
                     each sentence is a list of index, unpadded
                     or you can use the return of "txt2ind" if provided

        :return: list of labels
                 encoding mode:
                 [1,0,0,0,0,0,0,0]: 非影视作品
                 [0,1,0,0,0,0,0,0]: 电视剧
                 [0,0,1,0,0,0,0,0]: 电影
                 [0,0,0,1,0,0,0,0]: 综艺节目
                 [0,0,0,0,1,0,0,0]: 纪录片
                 [0,0,0,0,0,1,0,0]: 动画片
                 [0,0,0,0,0,0,1,0]: 综艺节目
                 [0,0,0,0,0,0,0,1]: 电视节目
        """
        return

    @abstractmethod
    def restore(self, sess, model_path):
        """
        Restore a model from a given checkpoint
        :param sess: tf.Session()
        :param model_path: model file's name

        :return: void
        """
        return

