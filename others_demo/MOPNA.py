# 编写人员：刘嘉豪
#
# 开发时间：2022/7/26 16:19
# coding:utf-8
from PIL import Image
import numpy as np
import math
import time
import os  # 用于查找目录下的文件
import copy
import sys

# 输出图片的位置
ImageWidth = 256
ImageHeight = 256
FILE_PATH = r"C:\MOPNAoutput\%d_%d\Output" % (ImageWidth, ImageHeight)
if not os.path.exists(FILE_PATH):
    os.makedirs(FILE_PATH)


# 写入文件
def SaveResult(str):
    # 将str写入结果文件中
    try:
        fname = time.strftime("%Y%m%d", time.localtime())
        f2 = open(FILE_PATH + '\\0_result' + fname + '.txt', 'a+')
        # f2 = open('result' + fname + '.txt','a+')
        f2.read()
        # f2.write('--------------------------------------------------')
        # f2.write('\n')
        # timestr = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        # f2.write(timestr)
        f2.write('\n')
        f2.write(str)
        f2.write('\n')
    finally:
        if f2:
            f2.close()
    return 0


# PSNR
def PSNR(image_array1, image_array2):
    # 输入为两个图像数组，一维，大小相同
    assert (np.size(image_array1) == np.size(image_array2))
    n = np.size(image_array1)
    assert (n > 0)
    MSE = 0.0
    for i in range(0, n):
        MSE += math.pow(int(image_array1[i]) - int(image_array2[i]), 2)
    MSE = MSE / n
    if MSE > 0:
        rtnPSNR = 10 * math.log10(255 * 255 / MSE)
    else:
        rtnPSNR = 100
    return rtnPSNR


# 十进制转二进制
# 将一个十进制数x转换为n个bit的二进制数,高位在前
def dec2bin_higher_ahead(x, n):
    b_array1 = np.zeros(n)
    for i in range(0, n, 1):
        b_array1[i] = int(x % 2)
        x = x // 2
    b_array2 = np.zeros(n)
    for i in range(0, n, 1):
        b_array2[i] = b_array1[n - i]  # n-1-i ？
    return b_array2


# 十进制转二进制
# 将一个十进制数x转换为n个bit的二进制数,低位在前
def dec2bin_lower_ahead(y, n):
    x = y
    b_array1 = np.zeros(n)
    for i in range(0, n, 1):
        b_array1[i] = int(x % 2)
        x = x // 2

    return b_array1


# 信息隐藏算法

# ALGORITHM: EMD06 方法
def EMD06(image_array, secret_string, n=2, k=3, image_file_name=''):
    # image_array:输入的一维图像数组
    # image_file_name:传入的图像文件名（带全路径）
    # n为一组像素的数量,我理解n只能取2，4,8,16等值，取其他值会导致嵌入的bit数不好确定
    assert (n == 2 or n == 4 or n == 8 or n == 16 or n == 32 or n == 64)
    moshu = 2 * n + 1  # 模数的底
    # 分成n个像素一组
    num_pixel_groups = math.ceil(image_array.size / n)
    pixels_group = np.zeros((num_pixel_groups, n))
    i = 0
    while (i < num_pixel_groups):
        for j in range(0, n):
            if (i * n + j < image_array.size):
                pixels_group[i, j] = image_array[i * n + j]
        i = i + 1
    # 每一个像素组计算出一个fG值
    fG_array = np.zeros(num_pixel_groups)
    for i in range(0, num_pixel_groups):
        fG = 0
        for j in range(0, n):
            fG += (j + 1) * pixels_group[i, j]
        fG_array[i] = fG % moshu
    # -----------------------------------------------------------------------------------
    # 从待嵌入bit串数据中取出m个比特，作为一组。m=math.log((2*n),2),以2为底的对数
    m = int(math.log((2 * n), 2))
    # 分组
    num_secret_groups = math.ceil(secret_string.size / m)
    secret_group = np.zeros((num_secret_groups, m))
    i = 0
    while (i < num_secret_groups):
        for j in range(0, m):
            if (i * m + j < s_data.size):
                secret_group[i, j] = s_data[i * m + j]
        i = i + 1
    # -----------------------------------------------------------------------------------

    # 一组pixels_group嵌入一组secret_group的信息，多了不能嵌入,最后一组pixel不用于嵌入以防止错误
    assert (np.shape(secret_group)[0] <= np.shape(pixels_group)[0] - 1)
    # 每一组secret_group计算得到一个d值，d为（2n+1）进制的一个数
    d_array = np.zeros(num_secret_groups)
    for i in range(0, num_secret_groups):
        # d代表一个（2n+1）进制的一个数
        d = 0
        for j in range(0, m):
            d += secret_group[i, j] * (2 ** (m - 1 - j))
            d_array[i] = d
    # -----------------------------------------------------------------------------------
    # 开始进行嵌入
    embedded_pixels_group = pixels_group.copy()
    for i in range(0, num_secret_groups):
        d = d_array[i]
        fG = fG_array[i]
        j = int(d - fG) % moshu
        if (j > 0):  # 如果为0的话，则不进行修改
            if (j <= n):
                embedded_pixels_group[i, j - 1] += 1
            else:
                embedded_pixels_group[i, (2 * n + 1 - j) - 1] += -1

    # -----------------------------------------------------------------------------------
    # 恢复，提取加密数据
    recover_d_array = np.zeros(num_secret_groups)
    for i in range(0, num_secret_groups):
        fG = 0
        for j in range(0, n):
            fG += (j + 1) * embedded_pixels_group[i, j]
        recover_d_array[i] = fG % moshu

    # 恢复出的和以前的应该是一致的
    assert (int((recover_d_array - d_array).sum()) == 0)

    # 使用了多少pixel来进行嵌入
    num_pixels_changed = num_secret_groups * n

    # -----------------------------------------------------------------------------------
    # 输出图像
    img_out = embedded_pixels_group.flatten()
    img_out = img_out[:ImageWidth * ImageHeight]  # 取前面的pixel
    # 计算PSNR
    img_array_out = img_out.copy()
    # psnr = PSNR(image_array,img_array_out)
    imgpsnr1 = image_array[0:num_pixels_changed]
    imgpsnr2 = img_array_out[0:num_pixels_changed]
    psnr = PSNR(imgpsnr1, imgpsnr2)

    # 重组图像
    img_out = img_out.reshape(ImageWidth, ImageHeight)
    img_out = Image.fromarray(img_out)
    # img_out.show()
    img_out = img_out.convert('L')

    (filepath, tempfilename) = os.path.split(image_file_name)
    (originfilename, extension) = os.path.splitext(tempfilename)
    new_file = FILE_PATH + '\\' + originfilename + '_' + sys._getframe().f_code.co_name + "_n_" + str(n) + "_k_" + str(
        k) + ".png"
    img_out.save(new_file, 'png')

    # 保存结果到文件
    str1 = 'Image:%30s,Method:%15s,n=%d,k=%d,pixels used: %d,PSNR: %.2f' % (
        originfilename, sys._getframe().f_code.co_name, n, k, num_pixels_changed, psnr)
    print(str1)
    SaveResult('\n' + str1)

    return 0


# ALGORITHM: LWC07 方法
def LWC07(image_array, secret_string, n=2, k=3, image_file_name=''):
    # image_array:输入的一维图像数组
    # image_file_name:传入的图像文件名（带全路径）
    # 分成2个像素一组
    n = 2
    num_pixel_groups = math.ceil(image_array.size / n)
    pixels_group = np.zeros((num_pixel_groups, n))
    i = 0
    while (i < num_pixel_groups):
        for j in range(0, n):
            if (i * n + j < image_array.size):
                pixels_group[i, j] = image_array[i * n + j]
        i = i + 1
    # -----------------------------------------------------------------------------------
    # 从待嵌入bit串数据中取出3个比特，作为一组
    # 分组
    num_secret_groups = math.ceil(secret_string.size / 3)
    secret_group = np.zeros((num_secret_groups, 3))
    i = 0
    while (i < num_secret_groups):
        for j in range(0, 3):
            if (i * 3 + j < s_data.size):
                secret_group[i, j] = s_data[i * 3 + j]
        i = i + 1

        # 一组pixels_group嵌入一组secret_group的信息，多了不能嵌入,最后一组pixel不用于嵌入以防止错误
    assert (np.shape(secret_group)[0] <= np.shape(pixels_group)[0] - 1)
    # 每一组secret_group计算得到一个d值，d为十进制的一个数
    d_array = np.zeros(num_secret_groups)
    for i in range(0, num_secret_groups):
        # d代表一个（2n+1）进制的一个数
        d = 0
        for j in range(0, 3):
            d += secret_group[i, j] * (2 ** (3 - 1 - j))
        d_array[i] = d

    # -----------------------------------------------------------------------------------
    # 开始进行嵌入
    embedded_pixels_group = pixels_group.copy()
    for i in range(0, num_secret_groups):
        fe = 1 * pixels_group[i, 0] + 3 * pixels_group[i, 1]
        fe = fe % 8
        if (int(fe) == int(d_array[i])):
            # 不修改
            embedded_pixels_group[i, 0] = pixels_group[i, 0]
            embedded_pixels_group[i, 1] = pixels_group[i, 1]
        else:
            fe = 1 * (pixels_group[i, 0] + 1) + 3 * pixels_group[i, 1]
            fe = fe % 8
            if (int(fe) == int(d_array[i])):
                embedded_pixels_group[i, 0] += 1
            else:
                fe = 1 * (pixels_group[i, 0] - 1) + 3 * pixels_group[i, 1]
                fe = fe % 8
                if (int(fe) == int(d_array[i])):
                    embedded_pixels_group[i, 0] += -1
                else:
                    fe = 1 * pixels_group[i, 0] + 3 * (pixels_group[i, 1] + 1)
                    fe = fe % 8
                    if (int(fe) == int(d_array[i])):
                        embedded_pixels_group[i, 1] += 1
                    else:
                        fe = 1 * pixels_group[i, 0] + 3 * (pixels_group[i, 1] - 1)
                        fe = fe % 8
                        if (int(fe) == int(d_array[i])):
                            embedded_pixels_group[i, 1] += -1
                        else:
                            fe = 1 * (pixels_group[i, 0] + 1) + 3 * (pixels_group[i, 1] + 1)
                            fe = fe % 8
                            if (int(fe) == int(d_array[i])):
                                embedded_pixels_group[i, 0] += 1
                                embedded_pixels_group[i, 1] += 1
                            else:
                                fe = 1 * (pixels_group[i, 0] + 1) + 3 * (pixels_group[i, 1] - 1)
                                fe = fe % 8
                                if (int(fe) == int(d_array[i])):
                                    embedded_pixels_group[i, 0] += 1
                                    embedded_pixels_group[i, 1] += -1
                                else:
                                    fe = 1 * (pixels_group[i, 0] - 1) + 3 * (pixels_group[i, 1] + 1)
                                    fe = fe % 8
                                    if (int(fe) == int(d_array[i])):
                                        embedded_pixels_group[i, 0] += -1
                                        embedded_pixels_group[i, 1] += 1
    # -----------------------------------------------------------------------------------
    # 恢复，提取加密数据
    recover_d_array = np.zeros(num_secret_groups)
    for i in range(0, num_secret_groups):
        fe = 1 * embedded_pixels_group[i, 0] + 3 * embedded_pixels_group[i, 1]
        recover_d_array[i] = fe % 8

    # 恢复出的和以前的应该是一致的
    assert (int((recover_d_array - d_array).sum()) == 0)

    # 使用了多少pixel来进行嵌入
    num_pixels_changed = num_secret_groups * n
    # -----------------------------------------------------------------------------------
    # 输出图像
    img_out = embedded_pixels_group.flatten()
    img_out = img_out[:ImageWidth * ImageHeight]  # 取前面的pixel
    # 计算PSNR
    img_array_out = img_out.copy()
    # psnr = PSNR(image_array,img_array_out)
    imgpsnr1 = image_array[0:num_pixels_changed]
    imgpsnr2 = img_array_out[0:num_pixels_changed]
    psnr = PSNR(imgpsnr1, imgpsnr2)

    # 重组图像
    img_out = img_out.reshape(ImageWidth, ImageHeight)
    img_out = Image.fromarray(img_out)
    # img_out.show()
    img_out = img_out.convert('L')

    (filepath, tempfilename) = os.path.split(image_file_name)
    (originfilename, extension) = os.path.splitext(tempfilename)
    new_file = FILE_PATH + '\\' + originfilename + '_' + sys._getframe().f_code.co_name + "_n_" + str(n) + "_k_" + str(
        k) + ".png"
    img_out.save(new_file, 'png')

    # 保存结果到文件
    str1 = 'Image:%30s,Method:%15s,n=%d,k=%d,pixels used: %d,PSNR: %.2f' % (
        originfilename, sys._getframe().f_code.co_name, n, k, num_pixels_changed, psnr)
    print(str1)
    SaveResult('\n' + str1)

    return 0


# ALGORITHM: JY_2009 方法
def JY09(image_array, secret_string, n=1, k=2, image_file_name=''):
    # image_array:输入的一维图像数组
    # image_file_name:传入的图像文件名（带全路径）
    # n = 1 #此算法在一个像素中嵌入
    num_pixel_groups = image_array.size
    # -----------------------------------------------------------------------------------
    # 从待嵌入bit串数据中取出k个比特，作为一组
    # k = 2 #bpp，只能取1，2，再大的话就不能使用。
    assert (int(k) <= 2)
    moshu = 2 * k + 1
    # 分组
    num_secret_groups = math.ceil(secret_string.size / k)
    secret_group = np.zeros((num_secret_groups, k))
    for i in range(0, num_secret_groups, 1):
        for j in range(0, k, 1):
            if (i * k + j < secret_string.size):
                secret_group[i, j] = s_data[i * k + j]

    # 一组pixels_group嵌入一组secret_group的信息，多了不能嵌入,最后一组pixel不用于嵌入以防止错误
    assert (num_pixel_groups > num_secret_groups)
    # 每一组secret_group计算得到一个d值，d为十进制的一个数
    secret_d_array = np.zeros(num_secret_groups)
    for i in range(0, num_secret_groups):
        # d代表一个（2n+1）进制的一个数
        d = 0
        for j in range(0, k, 1):
            d += secret_group[i, j] * (2 ** j)  # 将secret视为低位在前
        secret_d_array[i] = d

    # -----------------------------------------------------------------------------------
    # 开始进行嵌入
    embedded_pixels_group = image_array.copy()
    pixels_group = image_array.copy()
    for i in range(0, num_secret_groups):
        x = 0
        if (pixels_group[i] >= 0) and (pixels_group[i] <= moshu):
            for x in range(0, moshu, 1):
                fg = (pixels_group[i] + x) % moshu
                if int(fg) == int(secret_d_array[i]):
                    embedded_pixels_group[i] = pixels_group[i] + x
                    break
        else:
            if (pixels_group[i] >= 255 - moshu) and (pixels_group[i] <= 255):
                for x in range(-1 * moshu + 1, 1, 1):
                    fg = (pixels_group[i] + x) % moshu
                    if int(fg) == int(secret_d_array[i]):
                        embedded_pixels_group[i] = pixels_group[i] + x
                        break
            else:
                for x in range(-1 * moshu, moshu + 1, 1):
                    fg = (pixels_group[i] + x) % moshu
                    if int(fg) == int(secret_d_array[i]):
                        embedded_pixels_group[i] = pixels_group[i] + x
                        break

        tmp1 = embedded_pixels_group[i] % moshu
        tmp2 = int(secret_d_array[i])
        assert (tmp1 == tmp2)

    # -----------------------------------------------------------------------------------
    # 恢复，提取加密数据
    recover_d_array = np.zeros(num_secret_groups)
    for i in range(0, num_secret_groups):
        recover_d_array[i] = embedded_pixels_group[i] % moshu

    # 恢复出的和以前的应该是一致的
    assert (int((recover_d_array - secret_d_array).sum()) == 0)
    # 使用了多少pixel来进行嵌入
    num_pixels_changed = num_secret_groups
    # -----------------------------------------------------------------------------------
    # 输出图像
    img_out = embedded_pixels_group.flatten()
    img_out = img_out[:ImageWidth * ImageHeight]  # 取前面的pixel
    # 计算PSNR
    img_array_out = img_out.copy()
    # psnr = PSNR(image_array,img_array_out)
    imgpsnr1 = image_array[0:num_pixels_changed]
    imgpsnr2 = img_array_out[0:num_pixels_changed]
    psnr = PSNR(imgpsnr1, imgpsnr2)

    # 重组图像
    img_out = img_out.reshape(ImageWidth, ImageHeight)
    img_out = Image.fromarray(img_out)
    # img_out.show()
    img_out = img_out.convert('L')

    (filepath, tempfilename) = os.path.split(image_file_name)
    (originfilename, extension) = os.path.splitext(tempfilename)
    new_file = FILE_PATH + '\\' + originfilename + '_' + sys._getframe().f_code.co_name + "_n_" + str(n) + "_k_" + str(
        k) + ".png"
    img_out.save(new_file, 'png')

    # 保存结果到文件
    str1 = 'Image:%30s,Method:%15s,n=%d,k=%d,pixels used: %d,PSNR: %.2f' % (
        originfilename, sys._getframe().f_code.co_name, n, k, num_pixels_changed, psnr)
    print(str1)
    SaveResult('\n' + str1)

    return 0


# ALGORITHM: GEMD13 方法
def GEMD13(image_array, secret_string, n=2, k=3, image_file_name=''):
    # image_array:输入的一维图像数组
    # image_file_name:传入的图像文件名（带全路径）
    # n为一组像素的数量

    # 将一个十进制数x转换为（n+1）个bit的二进制数,低位在前
    def dec2bin_lower_ahead(x, n):
        b_array1 = np.zeros(n + 1)
        for i in range(0, n + 1, 1):
            b_array1[i] = int(x % 2)
            x = x // 2
        # 没有这个功能 b_array.reverse()
        # b_array2 = np.zeros(n + 1)
        # for i in range(0,n + 1,1):
        #    b_array2[i] = b_array1[n - i]
        return b_array1

    moshu = 2 ** (n + 1)  # 模数的底
    # 分成n个像素一组
    num_pixel_groups = math.ceil(image_array.size / n)
    pixels_group = np.zeros((num_pixel_groups, n))
    i = 0
    while (i < num_pixel_groups):
        for j in range(0, n):
            if (i * n + j < image_array.size):
                pixels_group[i, j] = image_array[i * n + j]
        i = i + 1
    # 每一个像素组计算出一个fGEMD值
    fGEMD_array = np.zeros(num_pixel_groups)
    for i in range(0, num_pixel_groups):
        fGEMD = 0
        for j in range(0, n):
            fGEMD += (2 ** (j + 1) - 1) * pixels_group[i, j]
        fGEMD_array[i] = fGEMD % moshu
    # -----------------------------------------------------------------------------------
    # 从待嵌入bit串数据中取出m个比特，作为一组
    m = n + 1
    # 分组
    num_secret_groups = math.ceil(secret_string.size / m)
    secret_group = np.zeros((num_secret_groups, m))
    i = 0
    while (i < num_secret_groups):
        for j in range(0, m):
            if (i * m + j < s_data.size):
                secret_group[i, j] = s_data[i * m + j]
        i = i + 1
    # -----------------------------------------------------------------------------------

    # 一组pixels_group嵌入一组secret_group的信息，多了不能嵌入,最后一组pixel不用于嵌入以防止错误
    assert (np.shape(secret_group)[0] <= np.shape(pixels_group)[0] - 1)
    # 每一组secret_group计算得到一个d值，d为（2n+1）进制的一个数
    d_array = np.zeros(num_secret_groups)
    for i in range(0, num_secret_groups):
        # d代表一个十进制的一个数
        d = 0
        for j in range(0, m):
            d += secret_group[i, j] * (2 ** (m - 1 - j))
        d_array[i] = d
    # -----------------------------------------------------------------------------------
    # 开始进行嵌入
    embedded_pixels_group = pixels_group.copy()
    diff_array = np.zeros(num_secret_groups)
    for i in range(0, num_secret_groups):
        d = d_array[i]
        fGEMD = fGEMD_array[i]
        assert (fGEMD < 33)
        diff_array[i] = int(d - fGEMD) % moshu

    for i in range(0, num_secret_groups):
        diff = int(diff_array[i])
        if (diff == 2 ** n):
            embedded_pixels_group[i, 0] = pixels_group[i, 0] + 1
            embedded_pixels_group[i, n - 1] = pixels_group[i, n - 1] + 1
        if (diff > 0) and (diff < 2 ** n):
            # 将diff转换为（n+1）个二进制数
            b_array = np.zeros(n + 1)
            b_array = dec2bin_lower_ahead(diff, n)
            for j in range(n, 0, -1):  # 倒序
                if (int(b_array[j]) == 0) and (int(b_array[j - 1]) == 1):
                    embedded_pixels_group[i, j - 1] = pixels_group[i, j - 1] + 1
                if (int(b_array[j]) == 1) and (int(b_array[j - 1]) == 0):
                    embedded_pixels_group[i, j - 1] = pixels_group[i, j - 1] - 1
        if (diff > 2 ** n) and (diff < 2 ** (n + 1)):
            # 将diff转换为（n+1）个二进制数
            b_array = np.zeros(n + 1)
            b_array = dec2bin_lower_ahead(2 ** (n + 1) - diff, n)
            for j in range(n, 0, -1):  # 倒序
                if (int(b_array[j]) == 0) and (int(b_array[j - 1]) == 1):
                    embedded_pixels_group[i, j - 1] = pixels_group[i, j - 1] - 1
                if (int(b_array[j]) == 1) and (int(b_array[j - 1]) == 0):
                    embedded_pixels_group[i, j - 1] = pixels_group[i, j - 1] + 1

    # -----------------------------------------------------------------------------------
    # 恢复，提取加密数据
    recover_d_array = np.zeros(num_secret_groups)
    for i in range(0, num_secret_groups):
        fGEMD = 0
        for j in range(0, n):
            fGEMD += (2 ** (j + 1) - 1) * embedded_pixels_group[i, j]
        recover_d_array[i] = fGEMD % moshu

    # 恢复出的和以前的应该是一致的
    assert (int((recover_d_array - d_array).sum()) == 0)
    # 使用了多少pixel来进行嵌入
    num_pixels_changed = num_secret_groups * n
    # -----------------------------------------------------------------------------------
    # 输出图像
    img_out = embedded_pixels_group.flatten()
    img_out = img_out[:ImageWidth * ImageHeight]  # 取前面的pixel
    # 计算PSNR
    img_array_out = img_out.copy()
    # psnr = PSNR(image_array,img_array_out)
    imgpsnr1 = image_array[0:num_pixels_changed]
    imgpsnr2 = img_array_out[0:num_pixels_changed]
    psnr = PSNR(imgpsnr1, imgpsnr2)

    # 重组图像
    img_out = img_out.reshape(ImageWidth, ImageHeight)
    img_out = Image.fromarray(img_out)
    # img_out.show()
    img_out = img_out.convert('L')

    (filepath, tempfilename) = os.path.split(image_file_name)
    (originfilename, extension) = os.path.splitext(tempfilename)
    new_file = FILE_PATH + '\\' + originfilename + '_' + sys._getframe().f_code.co_name + "_n_" + str(n) + "_k_" + str(
        k) + ".png"
    img_out.save(new_file, 'png')

    # 保存结果到文件
    str1 = 'Image:%30s,Method:%15s,n=%d,k=%d,pixels used: %d,PSNR: %.2f' % (
        originfilename, sys._getframe().f_code.co_name, n, k, num_pixels_changed, psnr)
    print(str1)
    SaveResult('\n' + str1)

    return 0


# ALGORITHM: KKWW16 方法
def KKWW16(image_array, secret_string, n=2, k=3, image_file_name=''):
    # image_array:输入的一维图像数组
    # image_file_name:传入的图像文件名（带全路径）
    # n为一组像素的数量

    # 将一个十进制数x转换为n个bit的（2**k）进制数,低位在前
    def dec_2k_lower_ahead(x, n):
        b_array1 = np.zeros(n)
        for i in range(0, n, 1):
            b_array1[i] = int(x) % (2 ** k)
            x = x // (2 ** k)
        # 没有这个功能 b_array.reverse()
        # b_array2 = np.zeros(n + 1)
        # for i in range(0,n + 1,1):
        #    b_array2[i] = b_array1[n - i]
        return b_array1

    # k = 3 #k是一个参数，表示一个pixel嵌入多少个bit

    moshu = 2 ** (n * k + 1)  # 模数的底
    # 参数c
    c_array = np.zeros(n)
    c_array[0] = 1
    for i in range(1, n):
        c_array[i] = (2 ** k) * c_array[i - 1] + 1

    # 分成n个像素一组
    num_pixel_groups = math.ceil(image_array.size / n)
    pixels_group = np.zeros((num_pixel_groups, n))
    i = 0
    while (i < num_pixel_groups):
        for j in range(0, n):
            if (i * n + j < image_array.size):
                pixels_group[i, j] = image_array[i * n + j]
                # overflow处理
                if pixels_group[i, j] <= 2 ** k - 2:
                    pixels_group[i, j] = 2 ** k - 1
                if pixels_group[i, j] >= 255 - (2 ** k - 2):
                    pixels_group[i, j] = 255 - (2 ** k - 1)
        i = i + 1
    # 每一像素组计算出一个fG值
    fG_array = np.zeros(num_pixel_groups)
    for i in range(0, num_pixel_groups):
        fG = 0
        for j in range(0, n):
            fG += c_array[j] * pixels_group[i, j]
        fG_array[i] = int(fG) % moshu
    # -----------------------------------------------------------------------------------
    # 从待嵌入bit串数据中取出n*k+1个比特，作为一组
    m = n * k + 1
    # 分组
    num_secret_groups = math.ceil(secret_string.size / m)
    secret_group = np.zeros((num_secret_groups, m))
    for i in range(0, num_secret_groups):
        for j in range(0, m):
            if (i * m + j < secret_string.size):
                secret_group[i, j] = secret_string[i * m + j]
    # -----------------------------------------------------------------------------------
    # 一组pixels_group嵌入一组secret_group的信息，多了不能嵌入,最后一组pixel不用于嵌入以防止错误
    assert (np.shape(secret_group)[0] <= np.shape(pixels_group)[0] - 1)
    # 每一组secret_group计算得到一个d值，d为（2n+1）进制的一个数
    d_array = np.zeros(num_secret_groups)
    for i in range(0, num_secret_groups):
        # d代表一个十进制的一个数
        d = 0
        for j in range(0, m):
            d += secret_group[i, j] * (2 ** (m - 1 - j))
        d_array[i] = d
    # -----------------------------------------------------------------------------------
    # 开始进行嵌入
    embedded_pixels_group = pixels_group.copy()
    diff_array = np.zeros(num_secret_groups)
    for i in range(0, num_secret_groups):
        d = d_array[i]
        fG = fG_array[i]
        diff_array[i] = int(d - fG) % moshu
    # 开始
    for i in range(0, num_secret_groups):
        # print(i,end=" ")
        diff = diff_array[i]
        if int(diff) > 0:
            if int(diff) == 2 ** (n * k):
                embedded_pixels_group[i, n - 1] = pixels_group[i, n - 1] + (2 ** k - 1)
                embedded_pixels_group[i, 0] = pixels_group[i, 0] + 1
            else:
                if int(diff) < 2 ** (n * k):
                    d_transfromed = np.zeros(n)
                    d_transfromed = dec_2k_lower_ahead(diff, n)
                    for j in range(n - 1, -1, -1):
                        embedded_pixels_group[i, j] = embedded_pixels_group[i, j] + d_transfromed[j]
                        if j > 0:
                            embedded_pixels_group[i, j - 1] = embedded_pixels_group[i, j - 1] - d_transfromed[j]
                else:
                    if int(diff) > 2 ** (n * k):
                        d_transfromed = np.zeros(n)
                        d_transfromed = dec_2k_lower_ahead((2 ** (n * k + 1)) - diff, n)
                        for j in range(n - 1, -1, -1):
                            embedded_pixels_group[i, j] = embedded_pixels_group[i, j] - d_transfromed[j]
                            if j > 0:
                                embedded_pixels_group[i, j - 1] = embedded_pixels_group[i, j - 1] + d_transfromed[j]
    # -----------------------------------------------------------------------------------
    # 使用了多少pixel来进行嵌入
    num_pixels_changed = num_secret_groups * n
    # -----------------------------------------------------------------------------------
    # 恢复，提取加密数据
    recover_d_array = np.zeros(num_secret_groups)
    for i in range(0, num_secret_groups):
        fG = 0
        for j in range(0, n):
            fG += c_array[j] * embedded_pixels_group[i, j]
        recover_d_array[i] = int(fG) % moshu
        # assert(int((recover_d_array[i] - d_array[i]).sum()) == 0)

    # 恢复出的和以前的应该是一致的
    assert (int((recover_d_array - d_array).sum()) == 0)
    # -----------------------------------------------------------------------------------
    # 输出图像
    img_out = embedded_pixels_group.flatten()
    img_out = img_out[:ImageWidth * ImageHeight]  # 取前面的pixel
    # 计算PSNR
    img_array_out = img_out.copy()
    # psnr = PSNR(image_array,img_array_out)
    imgpsnr1 = image_array[0:num_pixels_changed]
    imgpsnr2 = img_array_out[0:num_pixels_changed]
    psnr = PSNR(imgpsnr1, imgpsnr2)

    # 重组图像
    img_out = img_out.reshape(ImageWidth, ImageHeight)
    img_out = Image.fromarray(img_out)
    # img_out.show()
    img_out = img_out.convert('L')

    (filepath, tempfilename) = os.path.split(image_file_name)
    (originfilename, extension) = os.path.splitext(tempfilename)
    new_file = FILE_PATH + '\\' + originfilename + '_' + sys._getframe().f_code.co_name + "_n_" + str(n) + "_k_" + str(
        k) + ".png"
    img_out.save(new_file, 'png')

    # 保存结果到文件
    str1 = 'Image:%30s,Method:%15s,n=%d,k=%d,pixels used: %d,PSNR: %.2f' % (
        originfilename, sys._getframe().f_code.co_name, n, k, num_pixels_changed, psnr)
    print(str1)
    SaveResult('\n' + str1)

    return 0


# ALGORITHM: SB19 方法
def SB19(image_array, secret_string, n=1, k=3, image_file_name=''):
    # image_array:输入的一维图像数组
    # image_file_name:传入的图像文件名（带全路径）
    n = 1  # 此算法在一个像素中嵌入
    num_pixel_groups = image_array.size
    # -----------------------------------------------------------------------------------
    # 从待嵌入bit串数据中取出k个比特，作为一组
    # k = 2 #k应该是可调的
    moshu = k * k
    # 分组
    num_secret_groups = math.ceil(secret_string.size / k)
    secret_group = np.zeros((num_secret_groups, k))
    for i in range(0, num_secret_groups, 1):
        for j in range(0, k, 1):
            if (i * k + j < secret_string.size):
                secret_group[i, j] = s_data[i * k + j]

    # 一组pixels_group嵌入一组secret_group的信息，多了不能嵌入,最后一组pixel不用于嵌入以防止错误
    assert (num_pixel_groups > num_secret_groups)
    # 每一组secret_group计算得到一个d值，d为十进制的一个数
    secret_d_array = np.zeros(num_secret_groups)
    for i in range(0, num_secret_groups, 1):
        # d代表一个（2n+1）进制的一个数
        d = 0
        for j in range(0, k, 1):
            d += secret_group[i, j] * (2 ** j)  # 将secret视为低位在前
        secret_d_array[i] = d

    # -----------------------------------------------------------------------------------
    # 开始进行嵌入
    embedded_pixels_group = image_array.copy()
    pixels_group = image_array.copy()
    for i in range(0, num_secret_groups):
        x = 0
        for x in range(-1 * math.floor(moshu / 2), math.floor(moshu / 2) + 1, 1):
            f = (pixels_group[i] + x) % moshu
            if int(f) == int(secret_d_array[i]):
                if pixels_group[i] + x < 0:
                    embedded_pixels_group[i] = pixels_group[i] + x + moshu
                else:
                    embedded_pixels_group[i] = pixels_group[i] + x

                break
        tmp1 = embedded_pixels_group[i] % moshu
        tmp2 = int(secret_d_array[i])
        assert (tmp1 == tmp2)

    # -----------------------------------------------------------------------------------
    # 恢复，提取加密数据
    recover_d_array = np.zeros(num_secret_groups)
    for i in range(0, num_secret_groups):
        recover_d_array[i] = embedded_pixels_group[i] % moshu

    # 恢复出的和以前的应该是一致的
    diff_array = recover_d_array - secret_d_array
    assert (int((recover_d_array - secret_d_array).sum()) == 0)
    # 使用了多少pixel来进行嵌入
    num_pixels_changed = num_secret_groups * n
    # -----------------------------------------------------------------------------------
    # 输出图像
    img_out = embedded_pixels_group.flatten()
    img_out = img_out[:ImageWidth * ImageHeight]  # 取前面的pixel
    # 计算PSNR
    img_array_out = img_out.copy()
    # psnr = PSNR(image_array,img_array_out)
    imgpsnr1 = image_array[0:num_pixels_changed]
    imgpsnr2 = img_array_out[0:num_pixels_changed]
    psnr = PSNR(imgpsnr1, imgpsnr2)

    # 重组图像
    img_out = img_out.reshape(ImageWidth, ImageHeight)
    img_out = Image.fromarray(img_out)
    # img_out.show()
    img_out = img_out.convert('L')

    (filepath, tempfilename) = os.path.split(image_file_name)
    (originfilename, extension) = os.path.splitext(tempfilename)
    new_file = FILE_PATH + '\\' + originfilename + '_' + sys._getframe().f_code.co_name + "_n_" + str(n) + "_k_" + str(
        k) + ".png"
    img_out.save(new_file, 'png')

    # 保存结果到文件
    str1 = 'Image:%30s,Method:%15s,n=%d,k=%d,pixels used: %d,PSNR: %.2f' % (
        originfilename, sys._getframe().f_code.co_name, n, k, num_pixels_changed, psnr)
    print(str1)
    SaveResult('\n' + str1)

    return 0


# ALGORITHM: MOPNA our new 方法
def MOPNA(image_array, secret_string, n=2, k=3, image_file_name=''):
    # image_array:输入的一维图像数组
    # image_file_name:传入的图像文件名（带全路径）
    # n为一组像素的数量,在本算法中，固定为2
    n = 2
    # k = 3 #每个pixel嵌入nk+1个bit
    moshu = 2 ** (n * k + 1)  # 模数的底数
    c0 = 3
    c1 = 11
    # 分成n个像素一组,保证整数组，不足的补零
    num_pixel_groups = math.ceil(image_array.size / n)
    pixels_group = np.zeros((num_pixel_groups, n))

    for i in range(0, num_pixel_groups, 1):
        for j in range(0, n, 1):
            if i * n + j < image_array.size:
                pixels_group[i, j] = image_array[i * n + j]  # image_array填充在pixels_group中
    # 分别计算每个f函数值
    fG_array = np.zeros((num_pixel_groups))
    for i in range(0, num_pixel_groups, 1):
        fG_array[i] = (c0 * pixels_group[i, 0] + c1 * pixels_group[i, 1]) % moshu

    num_BitsPerPixelsGoup = n * k + 1  # 每组pixcel嵌入的bit数
    num_secret_groups = math.ceil(secret_string.size / num_BitsPerPixelsGoup)  # num_secret_groups切割的组数
    # secret_group为num_secret_groups行num_BitsPerPixelsGoup列
    secret_group = np.zeros((num_secret_groups, num_BitsPerPixelsGoup))
    secret_string_copy = secret_string.copy()
    for i in range(0, num_secret_groups, 1):
        for j in range(0, num_BitsPerPixelsGoup, 1):
            if i * num_BitsPerPixelsGoup + j < secret_string.size:
                # 把secret_string中的每一个传入secret_group中
                secret_group[i, j] = secret_string_copy[i * num_BitsPerPixelsGoup + j]

    secret_d_array = np.zeros(num_secret_groups)  # 待嵌入的secret值
    for i in range(0, num_secret_groups, 1):
        for j in range(0, num_BitsPerPixelsGoup, 1):
            # d = 2**2k*b(2k) +2**2k−1*b(2k−1)+ · · · +2**1*b1 + 2**0b0.
            secret_d_array[i] += (2 ** j) * secret_group[i, j]

    # -----------------------------------------------------------------------------------
    # metrics
    def CPV(image_array1, image_array2):
        # 输入为两个图像数组，一维，大小相同
        assert (np.size(image_array1) == np.size(image_array2))
        n = np.size(image_array1)
        assert (n > 0)
        MSE = 0
        P2 = 0
        for i in range(0, n):
            MSE += math.pow(image_array1[i] - image_array2[i], 2)
            P2 += math.pow(image_array1[i], 2)
        if (MSE > 0) and (int(P2) > 0):
            rtnCSNR = 10 * math.log10(P2 / MSE)
        else:
            rtnCSNR = 100
        return rtnCSNR

    # -----------------------------------------------------------------------------------

    assert (num_pixel_groups > num_secret_groups)
    embedded_pixels_group = pixels_group.copy()
    for i in range(0, num_secret_groups, 1):
        tmp_MaxPsnr = -120000
        tmp_SlectedIndex0 = -129
        tmp_SlectedIndex1 = -129
        tmp_P = np.zeros(2)
        for j0 in range(-1 * moshu, moshu, 1):
            for j1 in range(-1 * moshu, moshu, 1):
                tmp_P[0] = (pixels_group[i, 0] + j0)
                tmp_P[1] = (pixels_group[i, 1] + j1)
                if (int(tmp_P[0]) >= 0 and int(tmp_P[1]) >= 0):
                    tmp = (c0 * tmp_P[0] + c1 * tmp_P[1]) % moshu
                    if (int(secret_d_array[i]) == int(tmp)):
                        tmp1 = CPV(pixels_group[i], tmp_P)
                        if tmp1 > tmp_MaxPsnr:
                            tmp_MaxPsnr = tmp1
                            tmp_SlectedIndex0 = j0
                            tmp_SlectedIndex1 = j1
        assert (tmp_SlectedIndex0 > -129)
        assert (tmp_SlectedIndex1 > -129)
        embedded_pixels_group[i, 0] = pixels_group[i, 0] + tmp_SlectedIndex0
        embedded_pixels_group[i, 1] = pixels_group[i, 1] + tmp_SlectedIndex1

        # check
        tmp = 0
        for j in range(0, num_BitsPerPixelsGoup, 1):
            tmp = (c0 * (embedded_pixels_group[i, 0]) + c1 * (embedded_pixels_group[i, 1])) % moshu
        assert (int((tmp - secret_d_array[i]).sum()) == 0)

    # 使用了多少pixel来进行嵌入
    num_pixels_changed = num_secret_groups * 2
    # -----------------------------------------------------------------------------------
    # 恢复，提取加密数据
    recover_d_array = np.zeros(num_secret_groups)  # 待嵌入的secret值
    for i in range(0, num_secret_groups, 1):
        for j in range(0, num_BitsPerPixelsGoup, 1):
            tmp = (c0 * (embedded_pixels_group[i, 0]) + c1 * (embedded_pixels_group[i, 1])) % moshu
            recover_d_array[i] = tmp

    assert (int((recover_d_array - secret_d_array).sum()) == 0)
    # -----------------------------------------------------------------------------------
    # 输出图像
    img_out = embedded_pixels_group.flatten()
    img_out = img_out[:ImageWidth * ImageHeight]  # 取前面的pixel
    # 计算PSNR
    img_array_out = img_out.copy()
    # psnr = PSNR(image_array,img_array_out)
    imgpsnr1 = image_array[0:num_pixels_changed]
    imgpsnr2 = img_array_out[0:num_pixels_changed]
    psnr = PSNR(imgpsnr1, imgpsnr2)

    # 重组图像
    img_out = img_out.reshape(ImageWidth, ImageHeight)
    img_out = Image.fromarray(img_out)
    # img_out.show()
    img_out = img_out.convert('L')

    (filepath, tempfilename) = os.path.split(image_file_name)
    (originfilename, extension) = os.path.splitext(tempfilename)
    new_file = FILE_PATH + '\\' + originfilename + '_' + sys._getframe().f_code.co_name + "_n_" + str(n) + "_k_" + str(
        k) + ".png"
    img_out.save(new_file, 'png')

    # 保存结果到文件
    str1 = 'Image:%30s,Method:%15s,n=%d,k=%d,pixels used: %d,PSNR: %.2f' % (
        originfilename, sys._getframe().f_code.co_name, n, k, num_pixels_changed, psnr)
    print(str1)
    SaveResult('\n' + str1)
    return


# 证明可以映射到所有值
def proof():
    n = 2
    k = 5  # 每个pixel嵌入nk+1个bit
    moshu = 2 ** (n * k + 1)  # 模数的底数
    c0 = 3
    c1 = 11
    outlist = []
    for g0 in range(0, 256):
        for g1 in range(0, 256):
            d = (c0 * g0 + c1 * g1) % moshu
            if d not in outlist:
                outlist.append(d)
    outlist.sort()
    assert (len(outlist) == moshu)
    return


# proof()

# 需要嵌入的信息,用整形0,1两种数值，分别表示二进制的0,1
np.random.seed(1203)
s_data = np.random.randint(0, 2, 98000)  # 49000 #98000
# path = r"F:\Pictures\256_256"
path = os.getcwd()  # 获取当前路径
path = path + r"\OriginalPictures\%d_%d" % (ImageWidth, ImageHeight)
SaveResult('start')

for file in os.listdir(path):
    file_path = os.path.join(path, file)
    # if "Pepper.png" not in file_path:
    #    continue
    # if "Tiffany.png" not in file_path:
    #    continue
    if os.path.isfile(file_path):
        print(file_path)
        # 开始仿真
        img = Image.open(file_path, "r")
        img = img.convert('L')
        # img.show()

        # 将二维数组，转换为一维数组
        img_array1 = np.array(img)
        img_array2 = img_array1.reshape(img_array1.shape[0] * img_array1.shape[1])
        # print(img_array2)
        # 将二维数组，转换为一维数组
        img_array3 = img_array1.flatten()
        # print(img_array3)

        # 调用函数
        # EMD06(img_array3,s_data,2,3,file_path)
        # EMD06(img_array3,s_data,4,3,file_path)
        # LWC07(img_array3,s_data,2,3,file_path)

        # JY09(img_array3,s_data,1,1,file_path)
        JY09(img_array3, s_data, 1, 2, file_path)

        # GEMD13(img_array3,s_data,4,3,file_path)

        KKWW16(img_array3, s_data, 2, 2, file_path)
        KKWW16(img_array3, s_data, 2, 3, file_path)
        KKWW16(img_array3, s_data, 4, 2, file_path)
        KKWW16(img_array3, s_data, 4, 3, file_path)

        SB19(img_array3, s_data, 1, 2, file_path)
        SB19(img_array3, s_data, 1, 3, file_path)
        # SB19(img_array3,s_data,1,4,file_path)

        MOPNA(img_array3, s_data, 2, 2, file_path)
        MOPNA(img_array3, s_data, 2, 3, file_path)

        print('-----------------------')
SaveResult('end')
time.sleep(10)
