# 编写人员：刘嘉豪
#
# 开发时间：2022/4/10 20:29

import math


def get_key(n, mode, str2):  # 进制转换，mode=0 表示n进制转二进制，mode=1 表示二进制转n进制 str2进制字符串
    s = ""
    if mode == 0:
        i = int(str2, n)
        k = bin(i).replace('0b', '')
        s = str(k)
        print(str2, "\n", n, "进制转2进制：", s)
        return s
    elif mode == 1:
        i = int(str2, 2)
        print("i=", i)
        while i > 0:
            k = i % n
            i = i // n
            s += str(k)
        print(str2, "二进制转n进制:", s[::-1], )
        return s[::-1]


def fun(n,m):
    s = ""
    while n > 0:
        k = n % m
        n = n // m
        s += str(k)
    print(s)



key = []
key.extend(1)
print(key)
