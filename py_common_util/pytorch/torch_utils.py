# coding: utf-8 or # -*- coding: utf-8 -*-
import torch
import numpy as np


class TorchUtils:

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
    def watch_tensor(tensor):
        """
        在cpu环境下查看PyTorch的tensor
        """
        return tensor.data.cpu().numpy()

    @staticmethod
    def batchify(tensor_data, batch_size, device):
        """
        将数据按batch_size分批
        :param tensor_data:
        :param batch_size:
        :param device:
        :return:
        """
        num_batch = tensor_data.size(0) // batch_size
        # Trim off any extra elements that wouldn't cleanly fit (remainders).
        tensor_data = tensor_data.narrow(0, 0, num_batch * batch_size)
        # Evenly divide the data across the batch_size batches.
        tensor_data = tensor_data.view(batch_size, -1).t().contiguous()
        return tensor_data.to(device)

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
        :param tuple_np_data_label: [([1,2,3],[0,0,1])]
        :param batch_size: 128
        :return: [(1,0),(2,0),(3,1)]
        使用：
        ......
        batched_data_label = TorchUtils.batchify_np_data_label(np_test_data, parser_args.eval_batch_size)
        with torch.no_grad():
            for batch_idx, (data, label) in enumerate(batched_data_label):
                data, label = TorchUtils.np_to_tensor(data).to(device), TorchUtils.np_to_tensor(label).to(device)
        ......
        """
        data = tuple_np_data_label[0][0]
        label = tuple_np_data_label[0][1]
        num_batch = TorchUtils.total_num_batch(data.shape[0], batch_size, allow_smaller_final_batch)
        data = data[:num_batch*batch_size]
        label = label[:num_batch*batch_size]
        batched_data = np.split(data, num_batch)
        batched_label = np.split(label, num_batch)
        return list(zip(batched_data, batched_label))

    @staticmethod
    def np_to_tensor(np_data):
        return np_data if TorchUtils.is_tensor(np_data) else torch.from_numpy(np_data)

    @staticmethod
    def is_tensor(tensor_data):
        return torch.is_tensor(tensor_data)

    @staticmethod
    def check_available_gpus(show_info=False):
        gpu_num = torch.cuda.device_count()
        gpu_names = str([torch.cuda.get_device_name(i) for i in range(gpu_num)])
        if show_info:
            print('{0} GPUs are detected : {1}'.format(gpu_num, gpu_names))
        return gpu_num

    @staticmethod
    def cuda_is_available():
        return torch.cuda.is_available()

    @staticmethod
    def device(device="gpu", device_index=0):
        return torch.device("cuda" if device == "gpu" else "cpu", device_index)


if __name__ == '__main__':
    data = torch.randn(2, 5)
    print(data)
