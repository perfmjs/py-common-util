# -*- coding: utf-8 -*-
from collections import deque


class RingBuffer(deque):
    """
    python的ring buffer高性能封装
    注意：deque性能远高于封装的RingBuffer类，因此应尽量使用原始的deque对象
    为性能考虑，应注释一切代理的方法(i.e. append, get)，程序中应直接使用deque原始支持的方法
    参考：https://en.wikipedia.org/wiki/Circular_buffer
    # def append(self, x):
        # super().append(x)
    """
    def __init__(self, maxlen):
        super().__init__(maxlen=maxlen)


if __name__ == '__main__':
    import time
    tm1 = time.time()
    rb = RingBuffer(1000)
    for i in range(int(1e6)):
        rb.append(i)
    print(list(rb)[:10])
    rb.clear()
    tm2 = time.time()
    print("使用封装的ringbuffer执行时间；{:.2f}seconds".format(tm2 - tm1))

    import time
    import collections
    tm1 = time.time()
    d = collections.deque(maxlen=1000)
    for i in range(int(1e6)):
        d.append(i)
    print(list(d)[:10])
    d.clear()
    tm2 = time.time()
    print("使用原始的deque执行时间；{:.2f}seconds".format(tm2 - tm1))
