#!/usr/bin/python
import collections


def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func

    return decorate


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **
                                                                 kwargs)
        return cls._instances[cls]


class ROListSlice(collections.Sequence):
    def __init__(self, alist, start, alen):
        self.alist = alist
        self.start = start
        self.alen = alen

    def __len__(self):
        return self.alen

    def _adj_i(self, i):
        if i < 0:
            i += self.alen
        return i + self.start

    def adj(self, i):
        if type(i) == int:
            return self._adj_i(i)
        else:
            start = self._adj_i(i.start or 0)
            stop = self._adj_i(i.stop or self.alen - 1)
            return slice(start, stop, i.step)

    def __getitem__(self, i):
        return self.alist[self.adj(i)]

    def __str__(self):
        return self.alist[self.start : self.start + self.alen].__str__()

    def __repr__(self):
        return self.__str__()




class ListSlice(ROListSlice):
    def __setitem__(self, i, v):
        self.alist[self.adj(i)] = v

    def __delitem__(self, i, v):
        del self.alist[self.adj(i)]
        self.alen -= 1

    def insert(self, i, v):
        self.alist.insert(self.adj(i), v)
        self.alen += 1
