# -*- coding:utf-8 -*-
"""
定义一些常用的装饰器
"""
import warnings
from inspect import isfunction, isclass


def print_exec_time(func):
    """
    装饰器：print execution time
    usage:
    @staticmethod
    @print_exec_time
    def add(x, y=10):
        return x + y
    if __name__ == '__main__':
    add(1, 2) -> "func: add(), time taken: 0.000002 seconds"
    :param func:
    :return:
    """
    def decorator_func(*args, **kwargs):
        from time import time
        before_time = time()
        rv = func(*args, **kwargs)
        print('print_exec_time->func: ' + func.__name__ + '()' + ', time taken: {:.3f} seconds'.format(time() - before_time))
        return rv
    return decorator_func


def Override(cls):
    """Annotation for documenting method overrides.
    ```
    usage:
    class A(object):
        def __init__(self):
            pass
        def _init(self):
            pass

    class B(A):
        @print_exec_time
        @PublicAPI
        @Override(A)
        def _init(self):
            pass
    >> B()._init()
    ```
    Arguments:
        cls (type): The superclass that provides the overriden method. If this
            cls does not actually have the method, an error is raised.
    """
    def check_override(method):
        if method.__name__ not in dir(cls):
            raise NameError("{} does not override any method of {}".format(method, cls))
        return method
    return check_override


def PublicAPI(obj):
    """Annotation for documenting public APIs.
    Public APIs are classes and methods exposed to end users of RLlib. You
    can expect these APIs to remain stable across RLlib releases.

    Subclasses that inherit from a ``@PublicAPI`` base class can be
    assumed part of the RLlib public API as well (e.g., all trainer classes
    are in public API because Trainer is ``@PublicAPI``).

    In addition, you can assume all trainer configurations are part of their
    public API as well.
    """
    return obj


def DeveloperAPI(obj):
    """Annotation for documenting developer APIs.
    Developer APIs are classes and methods explicitly exposed to developers
    for the purposes of building custom algorithms or advanced training
    strategies on top of RLlib internals. You can generally expect these APIs
    to be stable sans minor changes (but less stable than public APIs).

    Subclasses that inherit from a ``@DeveloperAPI`` base class can be
    assumed part of the RLlib developer API as well (e.g., all policy
    optimizers are developer API because PolicyOptimizer is ``@DeveloperAPI``).
    """
    return obj


def Deprecated(func):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emmitted
    when the function is used."""
    def newFunc(*args, **kwargs):
        if isfunction(func):
            func_type = "function"
        elif isclass(func):
            func_type = "class"
        else:
            func_type = "type"
        warnings.simplefilter('always', DeprecationWarning)  # turn off filter
        warnings.warn(f"Call to deprecated {func_type}: {func.__name__}.", category=DeprecationWarning, stacklevel=2)
        warnings.simplefilter('default', DeprecationWarning)  # reset filter
        return func(*args, **kwargs)
    newFunc.__name__ = func.__name__
    newFunc.__doc__ = func.__doc__
    newFunc.__dict__.update(func.__dict__)
    return newFunc


if __name__ == '__main__':
    class A(object):
        def __init__(self):
            pass
        @PublicAPI
        def _init(self):
            pass

    class B(A):
        @print_exec_time
        @PublicAPI
        @Override(A)
        def _init(self):
            pass

    B()._init()

    @Deprecated
    class SomeClass:
        @Deprecated
        def some_old_method(self, x, y):
            return x + y

    print(SomeClass().some_old_method(33, 44))


