# 编写人员：刘嘉豪
#
# 开发时间：2023/6/20 17:47
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


def QRcode_Embed(image_path1, image_path2):
    """
    :param image_path1: 秘密数据二维码
    :param image_path2: 被嵌入的二维码
    :return: 返回被嵌入的图像或者PIL数组
    """
    # 打开图像
    image = Image.open(image_path1)
    # 转换为灰度图像
    if image.mode == "L":
        pass
    else:
        print("图像不是灰度图像")
        image = image.convert("L")
    # 获取图像像素值
    pixel_values = np.array(image)
    # 获取图像大小
    width, height = image.size
    # 隐藏数据
    s_data = np.zeros(8 + width * width)
    if width == height:
        binary = bin(width)[2:].zfill(8)
        binary_array = np.array(list(binary), dtype=int)
    else:
        return False
    od_pixel_values = pixel_values.flatten()
    # 二值化
    binary_pixelValues = np.where(od_pixel_values >= 128, 1, 0)
    # 拼接数据
    s_data = np.concatenate((binary_array, binary_pixelValues))
    print("要隐藏的数据长度" + str(len(s_data)))
    # 选取隐藏算法:
    binary_list = []

    img_out, recover_d_array = \
        Modulus_Calculations_on_Prime_Number_Algorithm_for_Information_Hiding_With_High_Comprehensive_Performance \
            .sole_fun(image_path2, s_data)
    # 提取操作
    for decimal_number in recover_d_array:
        binary_string = bin(int(decimal_number))[2:]  # 去掉前缀 '0b'
        binary_string = binary_string.zfill(5)  # 补全到五位二进制数
        reversed_binary_string = binary_string[::-1]
        binary_list.append(reversed_binary_string)
    binary_array = np.array(list("".join(binary_list)), dtype=int)

    save_path = "D:\ALL_aboutSWU\cat_dog_lab\QR_embed\out_pic\img_out1.png"
    # 生成隐藏后的二维码
    # img_out.save(save_path)
    # 使用二维码识别函数对变换后的二维码图片识别，如果识别失败
    if detect_qr_code(img_out):
        print("当前识别的长度：" + str(len(s_data)))

    else:
        print("当前识别失败的长度：" + str(len(s_data)))  # 打印当前嵌入容量
        return False
    # 确保数组长度至少为 8
    while len(binary_array) < 8:
        binary_array = np.concatenate((binary_array, [0]))
    # 提取前八位二进制数转成十进制，看隐藏图大小
    eight_bit_binary = binary_array[:8]
    secret_number = int("".join(map(str, eight_bit_binary)), 2)
    # 截取出像素
    stego_array = binary_array[8:secret_number * secret_number + 8]

    assert (int((s_data[8:] - stego_array).sum()) == 0), "s_data - stego_array"

    # 组成灰度图（二维码）
    # 将一维数组转换成二维数组
    width = int(np.sqrt(len(stego_array)))
    binary_array_2d = np.reshape(stego_array, (width, width))
    binary_array_2d = binary_array_2d.astype(np.uint8)
    gray_image = Image.fromarray(binary_array_2d * 255)

    # 原来二维码图像对比
    # 显示载体图像
    # 设置中文字体
    plt.rcParams['font.family'] = 'SimHei'
    plt.subplot(2, 2, 1)
    plt.imshow(Image.open(image_path1), cmap='gray')
    plt.title('路径1，被隐藏二维码')

    plt.subplot(2, 2, 2)
    plt.imshow(gray_image, cmap='gray')
    plt.title('提取出来的二维码')

    plt.subplot(2, 2, 3)
    plt.imshow(Image.open(image_path2), cmap='gray')
    plt.title('路径2，用来隐藏的二维码')

    plt.subplot(2, 2, 4)
    plt.imshow(img_out, cmap='gray')
    plt.title('隐藏后的二维码')

    plt.waitforbuttonpress()


# 将生成的数组进行嵌入不同版本二维码
image_path1 = "D:\ALL_aboutSWU\cat_dog_lab\QR_embed\in_pic\qrcode_v1_ec0_bs5_bd4.png"
image_path2 = "D:\ALL_aboutSWU\cat_dog_lab\QR_embed\in_pic\qrcode_v3_ec0_bs5_bd4.png"
image_path3 = "D:\study_python\\newprogram\QRcodePic\\v5_M.png"
image_path4 = "D:\study_python\\newprogram\QRcodePic\\v10_M.png"
QRcode_Embed(image_path1, image_path2)
