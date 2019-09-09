# -*- coding: utf-8 -*-
import tensorflow as tf
from tensorflow.python.client import device_lib
import numpy as np
# 解决Warning：Your CPU supports instructions that this TensorFlow binary was not compiled to use: AVX2 FMA
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
# 当你和其他人共用同台机器上的多卡gpu时，防止和别人争用资源，每个人都最好指定使用哪张GPU卡
# os.environ["CUDA_VISIBLE_DEVICES"] = "0,1"


class TFUtils:

    @staticmethod
    def empty_zero_data(shape_channels_height_width=[1, 28, 28], dtype=np.float32):
        """
        返回length=0的数据
        :param shape_channels_height_width:
        e.g. [(np.zeros((0, 1, 28, 28), dtype=np.float32), np.zeros((0, 10), dtype=np.int64))]
        :return:
        """
        return np.zeros((0,
                        shape_channels_height_width[0],
                        shape_channels_height_width[1],
                        shape_channels_height_width[2]), dtype=dtype)

    @staticmethod
    def total_num_batch(num_total, batch_size, allow_smaller_final_batch=False):
        num_batch = num_total // batch_size
        if allow_smaller_final_batch:
            if num_total > (num_batch * batch_size):
                return num_batch + 1
            else:
                return num_batch
        else:
            # 舍去最后不能够成1批的剩余训练数据部分
            return num_batch

    @staticmethod
    def batchify_np_data_label(tuple_np_data_label, batch_size, allow_smaller_final_batch=False):
        """
        :param tuple_np_data_label:
        :param batch_size:
        :return:
        使用：
        ......
        batched_data_label = TFUtils.batchify_np_data_label(np_test_data, parser_args.eval_batch_size)
        for batch_idx, (data, label) in enumerate(batched_data_label):
            data, label = ......
        ......
        """
        if tuple_np_data_label is None or len(tuple_np_data_label) < 1:
            return []
        data = tuple_np_data_label[0][0]
        label = tuple_np_data_label[0][1]
        num_batch = TFUtils.total_num_batch(data.shape[0], batch_size, allow_smaller_final_batch)
        data = data[:num_batch*batch_size]
        label = label[:num_batch*batch_size]
        batched_data = np.split(data, num_batch)
        batched_label = np.split(label, num_batch)
        return list(zip(batched_data, batched_label))

    @staticmethod
    def l2_normalization(x):
        axis = TFUtils.get_axis(x)
        return tf.nn.l2_normalize(x, axis=axis)

    @staticmethod
    def std_normalization(x):
        axis = TFUtils.get_axis(x)
        batch_mean, batch_var = tf.nn.moments(x=x, axes=axis, name='moments')
        return tf.divide(tf.subtract(x, batch_mean), tf.sqrt(batch_var + TFUtils.get_small_epsilon()))

    @staticmethod
    def get_small_epsilon():
        return 1e-3

    @staticmethod
    def get_axis(x):
        return list(range(len(x.shape) - 1))

    @staticmethod
    def read_mnist_from_local(data_dir="../../dataset/MNIST_data/"):
        """e.g. data_dir=sys.path[0] + '/../../dataset/MNIST_data/'"""
        import tensorflow.examples.tutorials.mnist.input_data as mnist_input_data
        mnist = mnist_input_data.read_data_sets(data_dir, one_hot=True)
        print("MNIST loaded!")
        return mnist

    @staticmethod
    def tf_l2_normal_weight_biases(n_hidden, n_classes, num_hidden=1):
        weights = tf.Variable(tf.nn.l2_normalize(tf.random.normal([num_hidden*n_hidden, n_classes]), [0, 1]))
        biases = tf.Variable(tf.random.normal([n_classes]))
        return weights, biases

    @staticmethod
    def tf_random_normal_weight_biases(n_hidden, n_classes, num_hidden=1):
        weights = tf.Variable(tf.random.normal([num_hidden*n_hidden, n_classes]))
        biases = tf.Variable(tf.random.normal([n_classes]))
        return weights, biases

    @staticmethod
    def tf_truncate_normal_weight_biases(n_hidden, n_classes, num_hidden=1):
        weights = tf.Variable(tf.random.truncated_normal([num_hidden*n_hidden, n_classes], stddev=.075, seed=1234, name='final_weights'))
        biases = tf.Variable(tf.random.normal([n_classes]))
        return weights, biases

    @staticmethod
    def dense_to_one_hot(labels_dense, num_classes=10):
        """
        Convert class labels from scalars to one-hot vectors.
        labels_dense e.g. np.asarray([5, 0, 3, 2, 4, 9, 6, 7, 2, 1, 0, 0, 1, 4, 5, 2, 5, 6, 7, 8])
        as example: dense_to_one_hot(np.asarray([8]), 10)
        ref to: tensorflow/contrib/learn/python/learn/datasets/mnist.py#dense_to_one_hot()
        """
        num_labels = labels_dense.shape[0]
        index_offset = np.arange(num_labels) * num_classes
        labels_one_hot = np.zeros((num_labels, num_classes))
        labels_one_hot.flat[index_offset + labels_dense.ravel()] = 1
        return labels_one_hot

    @staticmethod
    def one_hot_to_dense(labels_dense_one_hot=[]):
        """
        for example:
        one_hot_to_dense([ 0.  1.  0.  0.  0.  0.  0.  0.  0.  0.])
        result index is: [1], and the result shuld be: index+1
        one_hot_to_dense([ 0.  0.  0.  1.  0.  0.  0.  0.  0.  0.])
        result index is: [3], and the result shuld be: index+1
        """
        if np.asarray(labels_dense_one_hot.shape).size <= 1:
            return labels_dense_one_hot
        with tf.compat.v1.Session() as sess:
            return sess.run(tf.argmax(input=labels_dense_one_hot, axis=1))

    @staticmethod
    def average(pixel):
        # #ref to :https://samarthbhargav.wordpress.com/2014/05/05/image-processing-with-python-rgb-to-grayscale-conversion/
        # #1.convert RGB image to gray image
        # return (pixel[0] + pixel[1] + pixel[2]) / 3
        # #2.using numpy average
        # #3.G = R*0.299 + G*0.587 + B*0.114
        return 0.299 * pixel[0] + 0.587 * pixel[1] + 0.114 * pixel[2]

    @staticmethod
    def np_to_tensor(np_data):
        return tf.convert_to_tensor(value=np_data)

    @staticmethod
    def check_available_gpus(show_info=False):
        local_devices = device_lib.list_local_devices()
        gpu_names = [x.name for x in local_devices if x.device_type == 'GPU']
        gpu_num = len(gpu_names)
        if show_info:
            print('{0} GPUs are detected : {1}'.format(gpu_num, gpu_names))
        return gpu_num

    @staticmethod
    def cuda_is_available(show_info=False):
        return TFUtils.check_available_gpus(show_info) > 0

    @staticmethod
    def device(device="gpu", device_index=0):
        """
        :param: device="gpu" 或 "cpu"
        :param: device_index
        :return:
        usage:
        ......
        with TFUtils.device("gpu", 1):
            sum_operation = tf.reduce_sum(dot_operation)
            ......
        """
        if TFUtils.cuda_is_available(show_info=False) and device == 'gpu':
            return tf.device(tf.compat.v1.DeviceSpec(device_type="GPU", device_index=device_index))
        else:
            return tf.device(tf.compat.v1.DeviceSpec(device_type="CPU", device_index=device_index))

    @staticmethod
    def tf_get_length3(sequence):
        """
        去掉batch padded功能，tensorflow特有的get_length，可用于nlp变长序列的bilstm，pytorch没有对应方法
        参考：Variable Sequence Lengths in TensorFlow  https://danijar.com/variable-sequence-lengths-in-tensorflow/
        :param sequence:
        :return:
        e.g.
        [
            [[1,2,3],[1,0,0]],
            [[1,2,3],[4,5,6]]
        ] -> [2,2]
        [
            [[1,2,3],[0,0,0]],
            [[1,2,3],[4,5,6]]
        ] -> [1,2]
        """
        used = tf.sign(tf.reduce_max(input_tensor=tf.abs(sequence), axis=2))
        length = tf.reduce_sum(input_tensor=used, axis=1)
        length = tf.cast(length, tf.int32)
        return length

    @staticmethod
    def tf_get_length2(sequence):
        """
        去掉batch padded功能，tensorflow特有的get_length，可用于nlp变长序列的bilstm, pytorch没有对应方法
        参考：Variable Sequence Lengths in TensorFlow  https://danijar.com/variable-sequence-lengths-in-tensorflow/
        :param x:
        :return:
        e.g. [[1,2,3],[4,5,6]] -> [3,3]
        [[0,2,3],[4,5,6]] -> [2,3]
        """
        used = tf.sign(tf.abs(sequence))  # for x的维度为：[100,80]的场景
        length = tf.reduce_sum(input_tensor=used, axis=1)
        length = tf.cast(length, tf.int32)
        return length

    @staticmethod
    def tf_get_length1(sequence):
        """
        去掉batch padded功能，tensorflow特有的get_length，可用于nlp变长序列的bilstm, pytorch没有对应方法
        参考：Variable Sequence Lengths in TensorFlow  https://danijar.com/variable-sequence-lengths-in-tensorflow/
        :param x:
        :return:
        e.g. [1,2,8] -> 3
        [1,0,8] -> 2
        [0,0,0] -> 0
        [-4,-2,-3] -> 3
        [-4,0,-3] -> 2
        """
        used = tf.sign(tf.abs(sequence))  # for x的维度为：[100]的场景
        length = tf.reduce_sum(input_tensor=used, axis=0, keepdims=False)
        length = tf.cast(length, tf.int32)
        return length


if __name__ == '__main__':
    from py_common_util.common.common_utils import CommonUtils
    iter = CommonUtils.cycle()
    print(next(iter))
    print(next(iter))
    print(next(iter))
    print(next(iter))
    print(next(iter))
    print(next(iter))
