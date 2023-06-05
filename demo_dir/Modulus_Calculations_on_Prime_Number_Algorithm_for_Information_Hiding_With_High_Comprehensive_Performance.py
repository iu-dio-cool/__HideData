# 编写人员：刘嘉豪
#
# 开发时间：2022/7/27 16:08
from PIL import Image
import numpy as np
import math
import os  # 用于查找目录下的文件
import sys
import time
import Efficiency
from pyinstrument import Profiler  # 查看运行时间

profiler = Profiler()
profiler.start()

# 输出图片的位置
ImageWidth = 256
ImageHeight = 256
FILE_PATH = r"D:\study_python\newprogram\%d_%d\Output" % (ImageWidth, ImageHeight)
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
        f2.write('\n')
        f2.write(str)
        f2.write('\n')
    finally:
        if f2:
            f2.close()
    return 0


# ALGORITHM: MOPNA our new 方法
def MOPNA(image_array, secret_string,shape1,shape2,n=2, k=3,):
    # image_array:输入的一维图像数组
    # image_file_name:传入的图像文件名（带全路径）
    # n为一组像素的数量,在本算法中，固定为2
    # n = 2
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
                tmp_P[0] = (pixels_group[i, 0] + j0)  # 寻找x使d = f (G + X)
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
    img_out = img_out[:shape1 * shape2]  # 取前面的pixel
    # 计算PSNR
    img_array_out = img_out.copy()
    # psnr = PSNR(image_array,img_array_out)
    imgpsnr1 = image_array[0:num_pixels_changed]
    imgpsnr2 = img_array_out[0:num_pixels_changed]
    psnr = Efficiency.PSNR(imgpsnr1, imgpsnr2)
    print("PSNR="+str(psnr))
    # 重组图像

    img_out = img_out.reshape(shape1, shape2)

    img_out = Image.fromarray(img_out)
    img_out = img_out.convert('L')
    print(type(img_out))
    # img_out.show()
    return img_out
    # (filepath, tempfilename) = os.path.split(image_file_name)
    # (originfilename, extension) = os.path.splitext(tempfilename)
    # new_file = FILE_PATH + '\\' + originfilename + '_' + sys._getframe().f_code.co_name + "_n_" + str(n) + "_k_" + str(
    #    k) + ".png"
    # img_out.save(new_file, 'png') # 图片保存

    # 保存结果到文件
    # str1 = 'Image:%30s,Method:%15s,n=%d,k=%d,pixels used: %d,PSNR: %.2f' % (originfilename, sys._getframe().f_code.co_name, n, k, num_pixels_changed, psnr)
    # print(str1)
    # SaveResult('\n' + str1)


# 需要嵌入的信息,用整形0,1两种数值，分别表示二进制的0,1
ImageWidth = 256
ImageHeight = 256
# np.random.seed(1203)
# s_data = np.random.randint(0, 2, 98000)  # 49000 #98000
# path = r"F:\Pictures\256_256"
path = os.getcwd()  # 获取当前路径
path = path + r"\OriginalPictures\%d_%d" % (ImageWidth, ImageHeight)
# SaveResult('start')


def poll_fun():
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
            MOPNA(img_array3, s_data, 2, 2, file_path,img_array1.shape[0],img_array1.shape[1])

            # MOPNA(img_array3, s_data, 2, 3, file_path)

            print('-----------------------')
    SaveResult('end')
    # time.sleep(10)


def sole_fun(file_path,s_data):
    print(file_path)
    # 开始仿真
    img = Image.open(file_path, "r")
    img = img.convert('L')
    # img.show()

    # 将二维数组，转换为一维数组
    img_array1 = np.array(img)
    img_array2 = img_array1.reshape(img_array1.shape[0] * img_array1.shape[1])
    print("大小是："+str(img_array1.shape[0])+"*"+str(img_array1.shape[1]))
    # 将二维数组，转换为一维数组
    img_array3 = img_array1.flatten()
    # print(img_array3)
    img_out = MOPNA(img_array3, s_data, img_array1.shape[0],img_array1.shape[1],2, 2)
    return img_out



# poll_fun()
# sole_fun("D:\study_python\\newprogram\demo_dir\OriginalPictures\\256_256\\Boat.png")
# profiler.stop()
# profiler.print()
