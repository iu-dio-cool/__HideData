# 编写人员：刘嘉豪
#
# 开发时间：2023/5/20 9:01

# 先监测不同二维码阅读函数
import numpy as np
from PIL import Image, ImageDraw
from pyzbar import pyzbar
import Modulus_Calculations_on_Prime_Number_Algorithm_for_Information_Hiding_With_High_Comprehensive_Performance
import matplotlib.pyplot as plt


def detect_qr_code(image_path):
    if isinstance(image_path, Image.Image):
        gray = image_path
        print("输入的变量是 PIL 图像对象")
    elif isinstance(image_path, str):
        # 打开图像
        image = Image.open(image_path)
        print("输入的变量是文件路径")
        # 转换为灰度图像
        gray = image.convert("L")
    else:
        print("输入的变量类型不正确")

    # 使用 pyzbar 库识别二维码
    qr_codes = pyzbar.decode(gray)

    # 判断是否识别到二维码
    if qr_codes:
        # 遍历识别到的二维码
        for qr_code in qr_codes:
            # 解码二维码数据
            data = qr_code.data.decode("utf-8")
            print("识别到的二维码数据:", data)
            return 1
    else:
        # 未识别到二维码
        print("未识别到二维码")
        return 0


def capacity_test():
    # 循环以每次100的步长生成随机一维数组

    for i in range(80, 120):
        s_data = np.random.randint(0, 2, i * 100)
        # 将生成的数组进行嵌入不同版本二维码
        image_path1 = "D:\ALL_aboutSWU\IDEA_and_code\QR_codePic\\v1_M.png"
        image_path2 = "D:\ALL_aboutSWU\IDEA_and_code\QR_codePic\\v3_M.png"
        image_path3 = "D:\ALL_aboutSWU\IDEA_and_code\QR_codePic\\v5_M.png"
        img_out = Modulus_Calculations_on_Prime_Number_Algorithm_for_Information_Hiding_With_High_Comprehensive_Performance \
            .sole_fun(image_path1, s_data)
        # 显示载体图像
        plt.subplot(2, 2, 1)
        plt.imshow(Image.open(image_path1), cmap='gray')
        plt.title('Original Image')

        plt.subplot(2, 2, 2)
        plt.imshow(img_out, cmap='gray')
        plt.title('Stego Image')
        plt.waitforbuttonpress()
        # 使用二维码识别函数对变换后的二维码图片识别，如果识别失败
        if detect_qr_code(img_out):
            print("当前识别的长度：" + str(len(s_data)))
        else:
            print("当前识别失败的长度：" + str(len(s_data)))  # 打印当前嵌入容量
            return False


capacity_test()
# 调用函数进行二维码识别
# image_path = "D:\ALL_aboutSWU\IDEA_and_code\QR_codePic\\v1_M.png"  # 替换为二维码图像路径
# detect_qr_code(image_path)
