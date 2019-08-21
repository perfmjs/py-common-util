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
            return self.copy()
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


if __name__ == '__main__':
    mod = EnhancedOrderedDict(banana=3, apple=4, pear=1, orange=2)
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
