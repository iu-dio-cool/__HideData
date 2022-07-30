# 编写人员：刘嘉豪
#
# 开发时间：2022/7/8 17:54
import math

from PIL import Image
import Efficiency


def plus(string):
    # Python zfill() 方法返回指定长度的字符串，原字符串右对齐，前面填充0。

    return string.zfill(8)


def mod(x, y):
    return x % y


def get_key(n, mode, str2):  # 进制转换，str1=0 表示n进制转二进制，str=1 表示二进制转n进制 str2进制字符串
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


def dec2m(n, m):
    s = ""
    while n > 0:
        k = n % m
        n = n // m
        s += str(k)
    print('十进制n转m后=', s[::-1])
    return s[::-1]


# 隐藏函数
def func(str1, str2, str3):
    im2 = Image.open(str1)
    # 转换成灰度图
    im = im2.convert('L')
    # 获取图片的宽和高
    width = im.size[0]
    print("width:" + str(width) + "\n")
    height = im.size[1]
    print("height:" + str(height) + "\n")
    w = 0
    h = 0
    c1 = 1
    c2 = 9
    c3 = 73
    c4 = 585
    p1 = im.getpixel((w, h))  # 第i位置的像数值
    p2 = im.getpixel((w, h + 1))  # 第i位置的像数值
    p3 = im.getpixel((w, h + 2))  # 第i位置的像数值
    p4 = im.getpixel((w, h + 3))  # 第i位置的像数值
    # p1 = 53
    # p2 = 81
    # p3 = 105
    # p4 = 96
    print("p={} {} {} {}".format(p1, p2, p3, p4))
    t = mod(c1 * p1 + c2 * p2 + c3 * p3 + c4 * p4, 2 ** 13)
    s = int(str2, 2)
    D = mod(s - t, 2 ** 13)
    k = 2 ** 12
    print("d  k ", D, k, s, t, s - t)
    key = []
    if D > k:
        D = 2 ** 13 - D
        key1 = dec2m(D, 8)
        for i in range(4):
            key.append(int(key1[i]))
            print(key[i])
        p4 -= key[0]
        p3 += key[0]

        p3 -= key[1]
        p2 += key[1]

        p2 -= key[2]
        p1 += key[2]

        p1 -= key[3]
        im.putpixel((w, h), p1)
        im.putpixel((w, h + 1), p2)
        im.putpixel((w, h + 2), p3)
        im.putpixel((w, h + 3), p4)

    elif D < k:
        key1 = dec2m(D, 8)
        for i in range(4):
            key.append(int(key1[i]))
            print(i, key[i])
        p4 += key[0]
        p3 -= key[0]

        p3 += key[1]
        p2 -= key[1]

        p2 += key[2]
        p1 -= key[2]

        p1 += key[3]
        im.putpixel((w, h), p1)
        im.putpixel((w, h + 1), p2)
        im.putpixel((w, h + 2), p3)
        im.putpixel((w, h + 3), p4)
    else:
        im.putpixel((w, h), p1)
        im.putpixel((w, h + 1), p2)
        im.putpixel((w, h + 2), p3)
        im.putpixel((w, h + 3), p4)

    im.save(str3)


def func2(le, str1):
    im = Image.open(str1)

    width = im.size[0]

    height = im.size[1]
    str2 = ""
    c1 = 1
    c2 = 9
    c3 = 73
    c4 = 585

    p1 = im.getpixel((0, 0))  # 取n个像素出来
    p2 = im.getpixel((0, 1))
    p3 = im.getpixel((0, 2))
    p4 = im.getpixel((0, 3))
    print("p={} {} {} {}".format(p1, p2, p3, p4), c1 * p1 + c2 * p2 + c3 * p3 + c4 * p4, 2 ** 13)
    # 计算t值

    t = mod(c1 * p1 + c2 * p2 + c3 * p3 + c4 * p4,2**13)

    print("t=", 63085 % 8192)
    string = get_key(10,0,str(t))
    print("st=", string)
# 原图
old = "D:\study_python\\newprogram\\512_512\Airplane.png"
# 处理后输出的图片路径
new = "D:\study_python\\newprogram\\test.png"
# 需要隐藏的信息
enc = "D:\study_python\\newprogram\\flag.txt"

func(old, '1011001010010', new)
print("psnr=", Efficiency.psnr(old, new))
func2(6, new)
