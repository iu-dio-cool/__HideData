# 编写人员：刘嘉豪
#
# 开发时间：2022/5/6 21:23
import math

from PIL import Image
import Efficiency


def plus(string):
    # Python zfill() 方法返回指定长度的字符串，原字符串右对齐，前面填充0。

    return string.zfill(8)


def Dec2Bin(num):
    # 递归
    result = ''

    if num:
        result = Dec2Bin(num // 2)
        return result + str(num % 2)
    else:
        return result


def mod(x, y):
    return x % y


def LSB(str):
    return str[len(str) - 1]


def f(num1, num2):
    dec = math.floor(num1 / 2) + num2
    out = str(Dec2Bin(dec))
    return LSB(out)


def get_key(strring):
    # 获取要隐藏的文件内容

    tmp = strring

    f = open(tmp, "rb")

    string = ""

    s = f.read()
    print("type= len= ", type(s), len(s))

    print("s=", s)
    for i in range(len(s)):
        # 逐个字节将要隐藏的文件内容转换为二进制，并拼接起来

        # 1.先用ord()函数将s的内容逐个转换为ascii码

        # 2.使用bin()函数将十进制的ascii码转换为二进制

        # 3.由于bin()函数转换二进制后，二进制字符串的前面会有"0b"来表示这个字符串是二进制形式，所以用replace()替换为空

        # 4.又由于ascii码转换二进制后是七位，而正常情况下每个字符由8位二进制组成，所以使用自定义函数plus将其填充为8位
        # print(s[i])

        string = string + plus(bin(s[i]).replace('0b', ''))
    f.close()

    return string


def func(str1, str2, str3):
    im2 = Image.open(str1)

    im = im2.convert('L')

    # 获取图片的宽和高

    width = im.size[0]

    print("width:" + str(width) + "\n")

    height = im.size[1]

    print("height:" + str(height) + "\n")

    count = 0

    # 获取需要隐藏的信息
    key = get_key(str2)
    # 隐藏信息长度
    keylen = len(key)
    print("len=", keylen)
    for h in range(0, height):

        for w in range(0, width):
            pixel1 = im.getpixel((w, h))  # 第i位置的像数值
            pixel2 = im.getpixel((w + 1, h))  # 第i+1位置的像素值

            if count == keylen:
                break

            if key[count] == LSB(Dec2Bin(pixel1)):
                print("lsb=", LSB(Dec2Bin(pixel1)), "count=", count)
                if key[count + 1] != f(pixel1, pixel2):
                    im.putpixel((w + 1, h), pixel2 + 1)
                else:
                    im.putpixel((w + 1, h), pixel2)
                im.putpixel((w, h), pixel1)
            else:
                if key[count + 1] == f(pixel1 - 1, pixel2):
                    im.putpixel((w, h), pixel1 - 1)
                else:
                    im.putpixel((w, h), pixel1 + 1)
                im.putpixel((w + 1, h), pixel2)
            count += 2

    im.show()
    im.save(str3)


# 原图
old = "D:\study_python\\newprogram\cat.png"
# 处理后输出的图片路径
new = "D:\study_python\\newprogram\cat_test.png"
# 需要隐藏的信息
enc = "D:\study_python\\newprogram\\test.txt"

# func(old, enc, new)
print("psnr=", Efficiency.psnr(old, new))
