#class base(object):
#   def __new__(*args, **kw):
#       print " base_new"
#       return object.__new__(*args, **kw)
#   def __init__(*args, **kw):
#       print " base_init"
#
#class A(base):
#   # Inherit the __new__, but override __init__
#   def __init__(self, *args, **kw):
#       super(A, self).__init__(*args, **kw)
#       print " A_init"
#
#class B(base):
#   # __new__ returns something that is not of type base
#   def __new__(*args, **kw):
#       print " B_new"
#       return object.__new__(object)
#   def __init__(*args, **kw):
#       super(B).__init__(*args, **kw)
#       print " B_init:"
#
#class C(base):
#   # __new__ returns nothing
#   def __new__(*args, **kw):
#       print " C_new"
#       # no return here at all!
#
##base()
#A(1)
#C()

def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
            print "1", instances[cls]
        print "2", instances[cls]
        return instances[cls]
    return getinstance

class Singleton(type):
    def __init__(self, *args, **kwargs):
        #super(Singleton, self).__init__(*args, **kwargs)
        self.__instance = None
        self.__iii = 112
    def __call__(self, *args, **kwargs):
        if self.__instance is None:
            self.__instance = super(Singleton, self).__call__(*args, **kwargs)
        return self.__instance

class MyClass:
    __metaclass__ = Singleton

class MyC:
    def __init__(self, *args, **kwargs):
        self.aa = "aa"

b = MyClass()
a = MyClass()

b1 = MyC()
a2 = MyC()

#s = type(MyC).__call__()
#print s.aa
print "aa"