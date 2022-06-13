# 编写人员：刘嘉豪
#
# 开发时间：2022/6/7 20:41
import math
from PIL import Image
import Efficiency



def plus(string):
    # Python zfill() 方法返回指定长度的字符串，原字符串右对齐，前面填充0。

    return string.zfill(8)


def mod(x, y):
    return x % y


def get_key(n, mod, str2):  # 进制转换，str1=0 表示n进制转二进制，str=1 表示二进制转n进制 str2进制字符串
    s = ""
    if mod == 0:
        i = int(str2, n)
        k = bin(i).replace('0b', '')
        s = str(k)
        print(str2, "\n", n, "进制转2进制：", s)
        return s
    elif mod == 1:
        i = int(str2, 2)
        print("i=", i)
        while i > 0:
            k = i % n
            i = i // n
            s += str(k)
        print(str2, "二进制转n进制:", s[::-1], )
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
    count = 0
    # 获取需要隐藏的信息
    key = get_key(9, 1, str2)  # key是转换n进制后的值
    # 隐藏信息长度
    keylen = len(key)
    print("len=", keylen)
    pixel = []
    b = []
    for h in range(0, height):

        for w in range(0, width, 4):
            if count == keylen:
                break
            pixel.append(im.getpixel((w,h)))  # 第i位置的像数值
            pixel.append(im.getpixel((w + 1,h)))  # 第i+1位置的像素值
            pixel.append(im.getpixel((w + 2,h)))  # 第i+2位置的像素值
            pixel.append(im.getpixel((w + 3,h)))  # 第i+3位置的像素值
            print("p1={} p2={} p3={} p4={}".format(pixel[0], pixel[1], pixel[2], pixel[3]))
            for num in range(4):
                b.append(math.floor(pixel[num] / 4))
                print("b[{}]={}".format(num, b[num]))
            # 计算f值
            f = mod((b[0] * 1 + b[1] * 2 + b[2] * 3 + b[3] * 4), 9)
            print("需要隐藏的key-count={},f={}".format(key[count],f))
            if key[count] == f:
                count += 1
            else:
                s = mod(int(key[count]) - f, 9)
                print("s=", s)
                if s <= 4:
                    pixel[s-1] + 4
                    count += 1
                    for i in range(4):
                        im.putpixel((w, h), pixel[i])
                    for num in range(4):
                        b.append(math.floor(pixel[num] / 4))
                        print(" new :b[{}]={}".format(num, b[num]))
                else:
                    pixel[9 - s-1] - 4
                    count += 1
                    for i in range(4):
                        im.putpixel((w, h), pixel[i])
                    for num in range(4):
                        b.append(math.floor(pixel[num] / 4))
                        print("newwww :b[{}]={}".format(num, b[num]))

            print("count=", count)

        if count == keylen:
            break

    #  im.show()
    im.save(str3)


# 原图
old = "D:\study_python\\newprogram\cat.png"
# 处理后输出的图片路径
new = "D:\study_python\\newprogram\cat_test.png"
# 需要隐藏的信息
enc = "D:\study_python\\newprogram\\flag.txt"

# get_key(8,1,'110101101001')

func(old, '110101101001', new)
# print("psnr=", Efficiency.psnr(old, new))
# func2(4, new)
