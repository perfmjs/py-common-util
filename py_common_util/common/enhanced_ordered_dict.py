# -*- coding:utf-8 -*-
from collections import OrderedDict
from py_common_util.common.common_utils import CommonUtils


class EnhancedOrderedDict(OrderedDict):
    """
    增强功能的OrderedDict，支持subset功能
    """
    def subset(self, items=[]):
        """返回subset的deep copy对象"""
        if items is None or len(items) < 1:
            # return self.copy()  # 是否应该返回空的OrderedDic()，即EnhancedOrderedDict()
            return EnhancedOrderedDict()
        all = super(EnhancedOrderedDict, self).items()
        # return type(self)((key, value) for (key, value) in all if key in items)
        copied_order_dict = EnhancedOrderedDict()
        for key, value in all:
            if key in items:
                copied_order_dict[key] = CommonUtils.deepcopy(value)
        return copied_order_dict

    def to_list(self):
        """convert OrderedDict's items to list"""
        return list(self.items())

    def next_key(self, key):
        all_keys = list(self.keys())
        if key in all_keys:
            key_index = all_keys.index(key)
        if key_index+1 <= len(all_keys) - 1:
            return all_keys[key_index + 1]
        else:
            return None

    def prev_key(self, key):
        all_keys = list(self.keys())
        if key in all_keys:
            key_index = all_keys.index(key)
        if key_index-1 >= 0:
            return all_keys[key_index - 1]
        else:
            return None


if __name__ == '__main__':
    mod = EnhancedOrderedDict(banana=3, apple=4, pear=1, orange=2)
    print("apple next_key=" + str(mod.next_key("orange")))
    print("apple prev_key=" + str(mod.prev_key("orange")))
    print(list(mod.keys()).index("pear"))
    print(mod.to_list()[-1][1])
    print(mod.get("apple"))
    print(mod.subset())
    print("####test copy")
    a = ["1", "2"]
    original_mod = EnhancedOrderedDict(banana=a)
    copied_mod = original_mod.subset(["apple", "banana"])
    a.append("new value")
    print("original_mod", original_mod)
    print("copied_mod", copied_mod)
