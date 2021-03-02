# coding: utf-8

class StringTypeCase:
    """ 处理字符串类型(str或unicode)值的转换。 """

    @staticmethod
    def to_redis(value):
        """ 接受 basestring 子类的值( str 或 unicode )，
        否则抛出 TypeError 。
        """
        if isinstance(value, basestring):
            return value

        raise TypeError

    @staticmethod
    def to_python(value):
        """ 将值转回str或unicode类型。 """
        if value is None:
            return None
        else:
            try:
                return str(value)
            except:
                return unicode(value)
