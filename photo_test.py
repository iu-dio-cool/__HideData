# 编写人员：刘嘉豪
#
# 开发时间：2022/4/4 17:24

import cv2


def image_gray(image):  # 灰度化函数
    h, w, ch = image.shape
    for row in range(h):
        for col in range(w):
            b = image[row, col, 0]
            g = image[row, col, 1]
            r = image[row, col, 2]
            k = int(max(b, g, r))
            # 取三个通道内的最大值来计算每一个像素值
            image[row, col, 0] = k
            image[row, col, 1] = k
            image[row, col, 2] = k
    print("Covert Ok！")
    cv2.imshow("noise", image)
    cv2.waitKey(3000)
    cv2.imwrite("gray.png", image)


print("如果显示原图请按1，显示灰度图像请按2,退出请按 q：\n")
while True:
    num = input()
    if num == "1":
        img = cv2.imread('cat.jpeg')  # 读取图像信息
        cv2.imshow("原图", img)
        cv2.waitKey(3000)
        cv2.imwrite("cat.png", img)
    elif num == "2":
        img = cv2.imread('cat.jpeg')  # 读取图像信息
        image_gray(img)
    elif num == "q":
        break
    else:
        print("input error!\n")
