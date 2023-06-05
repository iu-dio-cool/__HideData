# 编写人员：刘嘉豪
#
# 开发时间：2022/6/9 16:54
import math
import numpy as np
from PIL import Image

def E(n):
    return ((2 * n + 1) * math.log(2, 2 * n + 1)) / 2 * n


def R(n):
    return (math.log(2, 2 * n + 1)) / n


# Peak Signal-to-Noise Ratio
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
