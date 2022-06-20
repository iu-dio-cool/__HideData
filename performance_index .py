import math
import numpy as np
from PIL import Image

def E(n):
    return ((2 * n + 1) * math.log(2, 2 * n + 1)) / 2 * n


def R(n):
    return (math.log(2, 2 * n + 1)) / n


# Peak Signal-to-Noise Ratio
def psnr(img1, img2):
    img1 = np.array(Image.open(img1).convert('L')).astype(np.float64)
    img2 = np.array(Image.open(img2).convert('L')).astype(np.float64)
    mse = np.mean((img1-img2)**2)
    if mse == 0:
        return 100
    else:
        return 20*np.log10(255/np.sqrt(mse))


# 原图
old = "D:\study_python\\newprogram\cat.png"
# 处理后输出的图片路径
new = "D:\study_python\\newprogram\cat_test.png"
print(psnr(old, new))
