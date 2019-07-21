# -*- coding: utf-8 -*-
import tensorflow as tf
import numpy as np
from py_common_util.tensorflow.tf_utils import TFUtils
from py_common_util.common.date_utils import DateUtils
"""
TensorFlow Dataset API + Graph  https://medium.com/@ywchen88/tensorflow-dataset-api-graph-30807178cfa0
输入管道性能指南 https://tensorflow.juejin.im/performance/datasets_performance.html
TensorFlow全新的数据读取方式：Dataset API入门教程  https://zhuanlan.zhihu.com/p/30751039
tensorflow入门：tfrecord 和tf.data.TFRecordDataset https://blog.csdn.net/yeqiustu/article/details/79793454
tensorflow中的dataset http://d0evi1.com/tensorflow/datasets/
"""


class TFRecordsUtils:

    @staticmethod
    def bytes_feature(value):
        return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))

    @staticmethod
    def int64_feature(value):
        value = value if hasattr(value, "__len__") else [value]
        return tf.train.Feature(int64_list=tf.train.Int64List(value=value))

    """
    e.g. values = [[1, 3],[2, 4],[3, 5]]
    """
    @staticmethod
    def int64_feature_list(values):
        return tf.train.FeatureList(feature=[tf.train.Feature(int64_list=tf.train.Int64List(value=values[i])) for i in range(len(values))])

    @staticmethod
    def float_feature(value):
        value = value if hasattr(value, "__len__") else [value]
        return tf.train.Feature(float_list=tf.train.FloatList(value=value))

    """
    e.g. values = [[1.1, 3.0],[-2.0, 4.1],[3.2, 5.6]]
    """
    @staticmethod
    def float_feature_list(values):
        return tf.train.FeatureList(feature=[tf.train.Feature(float_list=tf.train.FloatList(value=values[i])) for i in range(len(values))])

    """
    dict, e.g. {"feature": bytes_feature(b''), "label": int64_feature(10)}
    """
    @staticmethod
    def build_tf_example_string(dict):
        return tf.train.Example(features=tf.train.Features(feature=dict)).SerializeToString()

    @staticmethod
    def build_tf_sequence_example_string(context_dict, feature_lists_dict):
        return tf.train.SequenceExample(
            context=tf.train.Features(feature=context_dict),
            feature_lists=tf.train.FeatureLists(feature_list=feature_lists_dict)
        ).SerializeToString()

    """
    注意结束应调用writer.close()
    with get_writer(path) as writer:
        xxx
    """
    @staticmethod
    def get_writer(tfrecords_file_path):
        return tf.python_io.TFRecordWriter(tfrecords_file_path)
        # return tf.data.experimental.TFRecordWriter(tfrecords_file_path)

    @staticmethod
    def parse_dataset(tfrecords_files, parse_example_fn):
        return tf.data.TFRecordDataset(tfrecords_files).map(parse_example_fn)

    @staticmethod
    def write_summary(tfrecords_file_path, category='image', channels=1, height=0, width=0, total_count=0,
            train_count=0, valid_count=0, test_count=0, num_classes=0, data_is_normalized=False,
            using_shuffle_batch=False, remark=''):
        with TFRecordsUtils.get_writer(tfrecords_file_path) as writer:
            summary_example = tf.train.Example(features=tf.train.Features(feature={
                'feature_info': TFRecordsUtils.bytes_feature(b'0:feature_info(string),1:category(string),2:channels(int),3:height(int),4:width(int),5:total_count(int),6:train_count(int),7:valid_count(int),8:test_count(int),9:num_classes(int),10:data_is_normalized(int),11:using_shuffle_batch(int),12:remark(string)'),
                'category': TFRecordsUtils.bytes_feature(bytes(category, encoding="utf8")),
                'channels': TFRecordsUtils.int64_feature(channels),
                'height': TFRecordsUtils.int64_feature(height),
                'width': TFRecordsUtils.int64_feature(width),
                'total_count': TFRecordsUtils.int64_feature(total_count),
                'train_count': TFRecordsUtils.int64_feature(train_count),
                'valid_count': TFRecordsUtils.int64_feature(valid_count),
                'test_count': TFRecordsUtils.int64_feature(test_count),
                'num_classes': TFRecordsUtils.int64_feature(num_classes),
                'data_is_normalized': TFRecordsUtils.int64_feature(1 if data_is_normalized else 0),  # 数据是否已被正则化：true-1, false-0
                'using_shuffle_batch': TFRecordsUtils.int64_feature(1 if using_shuffle_batch else 0),  # 训练模型时是否使用shuffle batch读tfrecords的数据
                'remark': TFRecordsUtils.bytes_feature(bytes(remark, encoding="utf8"))
            }))
            writer.write(summary_example.SerializeToString())

    @staticmethod
    def serialize_data_to_string(np_data_raw=[[0.0, 0.0], [0.0, 0.0]], np_label_raw=[0, 0]):
        record_example = tf.train.SequenceExample(
            context=tf.train.Features(feature={
                "feature_info": TFRecordsUtils.bytes_feature(b'data_raw_bytes([byte]),label(int),data_raw([[float]])'),
                'data_raw_bytes': TFRecordsUtils.bytes_feature(np_data_raw.tobytes()),
                'label_raw_bytes': TFRecordsUtils.bytes_feature(np_label_raw.tobytes())
            }),
            feature_lists=tf.train.FeatureLists(feature_list={
                "data_raw": TFRecordsUtils.float_feature_list([[0.0]])
            })
        )
        return record_example.SerializeToString()

    @staticmethod
    def read_summary(tfrecords_file_path):
        """
        :param tfrecords_file_path:
        :return:
        usage:
            tuple_summary = TFRecordsUtils.read_summary("xxx.tfrecords")
            print(tuple_summary[0]) # index 0 to feature_info
        """
        def summary_parser(serialized_example):
            features = tf.compat.v1.parse_single_example(serialized_example,
                                               features={
                                                   'feature_info': tf.compat.v1.FixedLenFeature([], tf.string),
                                                   'category': tf.compat.v1.FixedLenFeature([], tf.string),
                                                   'channels': tf.compat.v1.FixedLenFeature([], tf.int64),
                                                   'height': tf.compat.v1.FixedLenFeature([], tf.int64),
                                                   'width': tf.compat.v1.FixedLenFeature([], tf.int64),
                                                   'total_count': tf.compat.v1.FixedLenFeature([], tf.int64),
                                                   'train_count': tf.compat.v1.FixedLenFeature([], tf.int64),
                                                   'valid_count': tf.compat.v1.FixedLenFeature([], tf.int64),
                                                   'test_count': tf.compat.v1.FixedLenFeature([], tf.int64),
                                                   'num_classes': tf.compat.v1.FixedLenFeature([], tf.int64),
                                                   'data_is_normalized': tf.compat.v1.FixedLenFeature([], tf.int64),
                                                   'using_shuffle_batch': tf.compat.v1.FixedLenFeature([], tf.int64),
                                                   'remark': tf.compat.v1.FixedLenFeature([], tf.string)
                                               })
            return tf.cast(features['feature_info'], tf.string), \
                tf.cast(features['category'], tf.string), \
                tf.cast(features['channels'], tf.int64), \
                tf.cast(features['height'], tf.int64), \
                tf.cast(features['width'], tf.int64), \
                tf.cast(features['total_count'], tf.int64), \
                tf.cast(features['train_count'], tf.int64), \
                tf.cast(features['valid_count'], tf.int64), \
                tf.cast(features['test_count'], tf.int64), \
                tf.cast(features['num_classes'], tf.int64), \
                tf.cast(features['data_is_normalized'], tf.int64), \
                tf.cast(features['using_shuffle_batch'], tf.int64), \
                tf.cast(features['remark'], tf.string)
        dataset = tf.data.TFRecordDataset(tfrecords_file_path).map(summary_parser)
        iter_summary = tf.compat.v1.data.make_one_shot_iterator(dataset)
        batch = iter_summary.get_next()
        print("====", batch.numpy())
        sess = tf.compat.v1.Session()
        try:
            feature_info, \
            category, \
            channels, \
            height, \
            width, \
            total_count, \
            train_count, \
            valid_count, \
            test_count, \
            num_classes, \
            is_normalized, \
            using_shuffle_batch, \
            remark \
                = sess.run(batch)
            return bytes.decode(feature_info), \
                   bytes.decode(category), \
                   channels, \
                   height, \
                   width, \
                   total_count, \
                   train_count, \
                   valid_count, \
                   test_count, \
                   num_classes, \
                   True if is_normalized > 0 else False, \
                   True if using_shuffle_batch > 0 else False, \
                   bytes.decode(remark, 'utf-8')
        except tf.errors.OutOfRangeError:
            print('error occurred while reading summary records!')
        finally:
            sess.close()
        return '', 'image', 1, 1, 1, 1, 1, 1, 1, 1, False, False, ''

    @staticmethod
    def read_and_decode(tfrecords_file_path,
                        num_epoch=1,
                        category='image',
                        batch_size=128,
                        shape_data_channels_height_width=[None],
                        shape_label=[1],
                        data_is_normalized=False,
                        using_shuffle_batch=True,
                        allow_smaller_final_batch=False,
                        using_unbatch=False,
                        using_padded_batch_with_shape=(),
                        data_parser=None):
        """
        数据类型的不一致会引起下面的异常：
        tensorflow.python.framework.errors_impl.InvalidArgumentError: Input to reshape is a tensor with 1568 values, but the requested shape has 784
        处理办法：train_images = np.float32(train_images)
        :param using_padded_batch_with_shape: e.g. x,y的shape为([6],[1])
        """
        def _data_parser(serialized_example):
            contexts, features = tf.parse_single_sequence_example(serialized_example,
                                                                  context_features={
                                                                      "feature_info": tf.compat.v1.FixedLenFeature([], tf.string),
                                                                      'data_raw_bytes': tf.compat.v1.FixedLenFeature([], dtype=tf.string, default_value=''),
                                                                      'label_raw_bytes': tf.compat.v1.FixedLenFeature([], dtype=tf.string, default_value='')
                                                                  }, sequence_features={'data_raw': tf.FixedLenSequenceFeature([], dtype=tf.float32, allow_missing=True)})
            data_raw = tf.decode_raw(contexts['data_raw_bytes'], tf.float32)
            data_raw = tf.reshape(data_raw, shape_data_channels_height_width)
            label_raw = tf.decode_raw(contexts['label_raw_bytes'], tf.int64)
            label_raw = tf.squeeze(tf.reshape(label_raw, shape_label))  # 用tf.squeeze()删除大小是1的维度，e.g. [100, 1]->[100]
            if not data_is_normalized:
                data_raw = TFUtils.l2_normalization(data_raw)
            if category == 'image':
                # Display the training data_raw in the TensorBoard visualizer.
                image_data = tf.expand_dims(data_raw, 0)  # add batch_size dim
                if len(image_data.shape) < 4:
                    image_data = tf.expand_dims(image_data, 3)  # add channels dim
                # tf.summary.image('data_raw', image_data)  #[batch_size, height, width, channels]： 该句会阻塞后面的sess.run()，如需使用图片的summary功能则应该把这句提到外面
            # label_raw = tf.one_hot(label_raw, 10, on_value=1.0, off_value=0.0, axis=-1)
            return data_raw, label_raw
        drop_remainder = not allow_smaller_final_batch
        dataset = tf.data.TFRecordDataset(tfrecords_file_path).map(data_parser if data_parser else _data_parser)
        if using_unbatch:
            # 变长序列问题，The issue here is that we want to batch the data: https://stackoverflow.com/questions/49531286/tensorflow-tf-data-dataset-cannot-batch-tensors-with-different-shapes-in-compo
            dataset = dataset.apply(tf.contrib.data.unbatch())
        if len(using_padded_batch_with_shape) > 0:
            if using_shuffle_batch:
                dataset = dataset.repeat(num_epoch).padded_batch(batch_size, padded_shapes=using_padded_batch_with_shape, drop_remainder=drop_remainder).shuffle(buffer_size=1000).prefetch(buffer_size=batch_size)
            else:
                dataset = dataset.repeat(num_epoch).padded_batch(batch_size, padded_shapes=using_padded_batch_with_shape, drop_remainder=drop_remainder).prefetch(buffer_size=batch_size)
        else:
            if using_shuffle_batch:
                dataset = dataset.repeat(num_epoch).batch(batch_size, drop_remainder=drop_remainder).shuffle(buffer_size=1000).prefetch(buffer_size=batch_size)
            else:
                dataset = dataset.repeat(num_epoch).batch(batch_size, drop_remainder=drop_remainder).prefetch(buffer_size=batch_size)
        iter_data_labels = tf.compat.v1.data.make_one_shot_iterator(dataset)
        # _data_raw, _data_labels = iter_data_labels.get_next()
        #return _data_raw, _data_labels
        return iter_data_labels

    @staticmethod
    def load_np_data(tfrecords_file_path,
                     num_epoch=1,
                     num_total=0,
                     batch_size=128,
                     allow_smaller_final_batch=False,
                     category='image',
                     shape_data_channels_height_width=[],
                     shape_label=[1],
                     data_is_normalized=True,
                     using_shuffle_batch=True,
                     dense_labels_to_one_hot_classes=0,
                     lazy_load_data=False,
                     using_unbatch=False,
                     using_padded_batch_with_shape=(),
                     data_parser=None):
        """
        :param tfrecords_file_path:
        :param num_epoch:
        :param num_total:
        :param batch_size:
        :param allow_smaller_final_batch:
        :param category:
        :param shape_data_channels_height_width:
        :param data_is_normalized:
        :param using_shuffle_batch:
        :param dense_labels_to_one_hot: 0-不用处理，>0就处理labels数据为TFUtils.dense_to_one_hot(label, dense_labels_to_one_hot_classes)
        :param lazy_load_data: true 仅返回iterator, false返回数据numpy数组
        :param using_padded_batch_with_shape: e.g. x,y的shape为([6],[1])
        :return:
        usage:
        iter_data_labels, np_data_labels = \
            TFRecordsUtils.np_load_data(tfrecords_path + "/valid.tfrecords",
                                        num_total=tuple_summary[7],
                                        batch_size=128,
                                        allow_smaller_final_batch=False,
                                        category=category,
                                        shape_data_channels_height_width=[1, height, width],
                                        shape_label=[1],
                                        data_is_normalized=True,
                                        using_shuffle_batch=True,
                                        dense_labels_to_one_hot_classes=0)
        ...
        iter_data_batch = iter_data_labels.get_next()
        ...for....
            if lazy_load_data:
                ...
                batch_x, batch_y = sess.run(iter_data_batch)
            else:
                batch_x, batch_y = np_data_labels[batch_index]
        """
        start_time_int = DateUtils.now_to_int()
        print("begin read_and_decode %s, lazy_load_data=%s ..." % (tfrecords_file_path, str(lazy_load_data)))
        if not lazy_load_data:
            num_epoch = 1
        iter_data_labels = TFRecordsUtils.read_and_decode(tfrecords_file_path=tfrecords_file_path,
                                                        num_epoch=num_epoch,
                                                        category=category,
                                                        batch_size=batch_size,
                                                        shape_data_channels_height_width=shape_data_channels_height_width,
                                                        shape_label=shape_label,
                                                        data_is_normalized=data_is_normalized,
                                                        using_shuffle_batch=using_shuffle_batch,
                                                        allow_smaller_final_batch=allow_smaller_final_batch,
                                                        using_unbatch=using_unbatch,
                                                        using_padded_batch_with_shape=using_padded_batch_with_shape,
                                                        data_parser=data_parser)
        data_labels = []
        total_num_batch = TFUtils.total_num_batch(num_total, batch_size, allow_smaller_final_batch)
        if lazy_load_data:
            duration = DateUtils.calc_duration_seconds(start_time_int, DateUtils.now_to_int())
            print("finished read_and_decode on lazy_load_data=%s mode, duration(seconds)=%d ..." % (lazy_load_data, duration))
            return iter_data_labels, data_labels
        sess = tf.compat.v1.Session()
        try:
            data_raw, labels = iter_data_labels.get_next()
            for i_batch in range(total_num_batch):
                _data, _labels = sess.run([data_raw, labels])
                data_labels.append((np.array(_data, dtype=np.float32),
                                    np.array(_labels, dtype=np.int64) if dense_labels_to_one_hot_classes<1
                                        else TFUtils.dense_to_one_hot(np.asarray(_labels, dtype=np.int64),
                                    dense_labels_to_one_hot_classes)))
        except:
            print('error occurred on reading tfrecods data!')
            import traceback
            traceback.print_exc()
        finally:
            sess.close()
        duration = DateUtils.calc_duration_seconds(start_time_int, DateUtils.to_int(DateUtils.now()))
        print("finished read_and_decode on lazy_load_data=%s mode, duration(seconds)=%d ..." % (lazy_load_data, duration))
        return iter_data_labels, data_labels


if __name__ == '__main__':
    # test_path = "/tony/pycharm_projects/deep_trading/_test"
    # iterator = tf.data.Dataset.range(1000).shuffle(100).make_one_shot_iterator()
    #
    # saveable_obj = tf.contrib.data.make_saveable_from_iterator(iterator)
    # tf.add_to_collection(tf.GraphKeys.SAVEABLE_OBJECTS, saveable_obj)
    # sess = tf.compat.v1.Session()
    # init_op = tf.group(tf.global_variables_initializer(), tf.local_variables_initializer())
    # sess.run(init_op)
    # saver = tf.train.Saver()
    ####
    # for step in range(10):
    #     print('{}: {}'.format(step, sess.run(iterator.get_next())))
    #     if step == 5:
    #         # saver.save(sess, test_path + '/foo', global_step=step)
    #         saver.save(sess,
    #                    test_path + "/model.ckpt",
    #                    global_step=step,
    #                    latest_filename="model.ckpt")
    #######
    # print("*****")
    # checkpoint = tf.train.get_checkpoint_state(
    #     test_path,
    #     latest_filename="model.ckpt")
    # saver.restore(sess, checkpoint.model_checkpoint_path)
    # for step in range(6, 10):
    #     print('{}: {}'.format(step, sess.run(iterator.get_next())))
    #########################
    tfrecords_path = "/tony/pycharm_projects/deep_trading/dataset/tf_records/kcws"
    tuple_summary = TFRecordsUtils.read_summary(tfrecords_path + "/summary.tfrecords")
    category = tuple_summary[1]
    height = tuple_summary[3]
    width = tuple_summary[4]
    num_train_total = tuple_summary[6]
    num_classes = tuple_summary[9]
    dense_labels_to_one_hot_classes = 0
    lazy_load_data = True
    num_epoch = 2
    iter_data_labels, train_data_labels \
        = TFRecordsUtils.load_np_data(tfrecords_path + "/train.tfrecords",
                                    num_epoch=num_epoch,
                                    num_total=num_train_total,
                                    batch_size=100,
                                    allow_smaller_final_batch=False,
                                    category=category,
                                    shape_data_channels_height_width=[height, width],
                                    shape_label=[height],
                                    data_is_normalized=True,
                                    using_shuffle_batch=False,
                                    dense_labels_to_one_hot_classes=dense_labels_to_one_hot_classes,
                                    lazy_load_data=lazy_load_data)
    if lazy_load_data:
        total_num_batch = TFUtils.total_num_batch(num_train_total, 100, allow_smaller_final_batch=False)
        data_raw, labels = iter_data_labels.get_next()
        sess = tf.compat.v1.Session()
        data_labels = []
        for i_batch in range(total_num_batch):
            _data, _labels = sess.run([data_raw, labels])
            data_labels.append((np.array(_data, dtype=np.float32),
                                np.array(_labels, dtype=np.int64) if dense_labels_to_one_hot_classes < 1
                                else TFUtils.dense_to_one_hot(np.asarray(_labels, dtype=np.int64),
                                                              dense_labels_to_one_hot_classes)))
        train_data_labels = data_labels
    for batch_idx, (data, label) in enumerate(train_data_labels):
        print(batch_idx, len(data), len(label))

