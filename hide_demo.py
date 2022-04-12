# 编写人员：刘嘉豪
#
# 开发时间：2022/4/10 11:50

# -*- coding: UTF-8 -*-

import requests
from PIL import Image


def fanyiyoudao(word):
    data = {
        'doctype': 'json',
        'type': 'AUTO',
        'i': word,
    }
    url = "http://fanyi.youdao.com/translate"
    r = requests.get(url, params=data)
    result = r.json()
    # print(result['translateResult'][0][0]['tgt'])
    res = result['translateResult'][0][0]['tgt']
    return res


def plus(string):
    # Python zfill() 方法返回指定长度的字符串，原字符串右对齐，前面填充0。

    return string.zfill(8)


def get_key(strring):
    # 获取要隐藏的文件内容

    tmp = strring

    f = open(tmp, "r+", encoding='UTF-8')

    string = ""
    s = f.read()
    res = fanyiyoudao(s)
    print("res= ", res, "len =", len(res))
    for i in range(len(res)):
        # 逐个字节将要隐藏的文件内容转换为二进制，并拼接起来

        # 1.先用ord()函数将s的内容逐个转换为ascii码

        # 2.使用bin()函数将十进制的ascii码转换为二进制

        # 3.由于bin()函数转换二进制后，二进制字符串的前面会有"0b"来表示这个字符串是二进制形式，所以用replace()替换为空

        # 4.又由于ascii码转换二进制后是七位，而正常情况下每个字符由8位二进制组成，所以使用自定义函数plus将其填充为8位

        string = string + plus(bin(ord(res[i])).replace('0b', ''))
    f.close()

    return string


def mod(x, y):
    return x % y


# str1为载体图片路径，str2为隐写文件，str3为加密图片保存的路径

def func(str1, str2, str3):
    im = Image.open(str1)

    # 获取图片的宽和高

    width = im.size[0]

    print("width:" + str(width) + "\n")

    height = im.size[1]

    print("height:" + str(height) + "\n")

    count = 0

    # 获取需要隐藏的信息

    key = get_key(str2)

    keylen = len(key)

    for h in range(0, height):

        for w in range(0, width):

            pixel = im.getpixel((w, h))

            a = pixel[0]

            b = pixel[1]

            c = pixel[2]

            if count == keylen:
                break

            # 下面的操作是将信息隐藏进去

            # 分别将每个像素点的RGB值余2，这样可以去掉最低位的值

            # 再从需要隐藏的信息中取出一位，转换为整型

            # 两值相加，就把信息隐藏起来了

            a = a - mod(a, 2) + int(key[count])

            count += 1

            if count == keylen:
                im.putpixel((w, h), (a, b, c))

                break

            b = b - mod(b, 2) + int(key[count])

            count += 1

            if count == keylen:
                im.putpixel((w, h), (a, b, c))

                break

            c = c - mod(c, 2) + int(key[count])

            count += 1

            if count == keylen:
                im.putpixel((w, h), (a, b, c))

                break

            if count % 3 == 0:
                im.putpixel((w, h), (a, b, c))

    im.save(str3)


def mod(x, y):
    return x % y


def toasc(strr):
    return int(strr, 2)


# le为所要提取的信息的长度，str1为加密载体图片的路径，str2为提取文件的保存路径

def func2(le, str1, str2):
    a = ""

    b = ""
    string = ""
    im = Image.open(str1)

    lenth = le * 8

    width = im.size[0]

    height = im.size[1]

    count = 0

    for h in range(0, height):

        for w in range(0, width):

            # 获得(w,h)点像素的值

            pixel = im.getpixel((w, h))

            # 此处余3，依次从R、G、B三个颜色通道获得最低位的隐藏信息

            if count % 3 == 0:

                count += 1

                b = b + str((mod(int(pixel[0]), 2)))

                if count == lenth:
                    break

            if count % 3 == 1:

                count += 1

                b = b + str((mod(int(pixel[1]), 2)))

                if count == lenth:
                    break

            if count % 3 == 2:

                count += 1

                b = b + str((mod(int(pixel[2]), 2)))

                if count == lenth:
                    break

        if count == lenth:
            break

    with open(str2, "w") as f:

        for i in range(0, len(b), 8):
            # 以每8位为一组二进制，转换为十进制

            stra = toasc(b[i:i + 8])
            string = string + chr(stra)
            # 将转换后的十进制数视为ascii码，再转换为字符串写入到文件中
            # print(chr(stra))
            # f.write(char(stra))

            stra = ""
        res = fanyiyoudao(string)
        f.write(res)

    print('图片中隐藏的中文信息是：', res)
    f.close()


# 文件长度

le = 18

# 原图
old = "D:\study_python\\newprogram\cat.png"
# 处理后输出的图片路径
new = "D:\study_python\\newprogram\cat_test.png"
# 需要隐藏的信息
enc = "D:\study_python\\newprogram\\test.txt"

# 含有隐藏信息的图片
new = "D:\study_python\\newprogram\cat_test.png"
# 信息提取出后所存放的文件
tiqu = "D:\study_python\\newprogram\get_test.txt"

func(old, enc, new)

print("隐藏成功！\n")

func2(le, new, tiqu)
