import numpy as np
import cv2
import math
import time
import tkinter
from tkinter import filedialog


# 全景图参数

T = 3 / 4  # T=a/b ; T1 = 0.6   T1=a/c = T/math.sqrt(1+T**2)
# F = 942


IMG_SHAPE_800x600 = (600, 800)
F_800x600 = 400
RADIUS_800x600 = (48, 330)  # 全向图区域半径
DY_800x600 = 80  # 透视图参数

HEIGHT_800x600 = 70  # 手动设定 俯视图参数 H_vertical, W_vertical = 1288, 1288  # 1288?
VERTICAL_SHAPE_800x600 = (640, 640)
P_800x600 = [IMG_SHAPE_800x600, F_800x600, RADIUS_800x600, DY_800x600, HEIGHT_800x600, VERTICAL_SHAPE_800x600]

# 全向图区域半径,透视图参数,俯视图参数,俯视图区域
IMG_SHAPE, F, RADIUS, DY, HEIGHT, VERTICAL_SHAPE = P_800x600


def mapping(src, dst_matrix):
    H, W = dst_matrix.shape[0:2]
    tx = np.array(dst_matrix[:, :, [0]].reshape(H, W), np.float32)
    ty = np.array(dst_matrix[:, :, [1]].reshape(H, W), np.float32)
    img = cv2.remap(src, ty, tx, cv2.INTER_LINEAR)
    return img


def get_vmatrix(src_shape=IMG_SHAPE, radius=RADIUS, t=T, f=F,
                vertical_shape=VERTICAL_SHAPE, height=HEIGHT):
    t1 = t / math.sqrt(1 + t ** 2)

    h, w = src_shape  # src尺寸
    src_y, src_x = h / 2, w / 2  # 原中心点
    r1, r2 = radius  # 显示半径

    H_vertical, W_vertical = vertical_shape  # 目标图像尺寸
    vertical_coord = np.zeros([H_vertical, W_vertical, 2], np.float)
    for Y in range(H_vertical):
        for X in range(W_vertical):
            if (Y == H_vertical / 2) & (X == W_vertical / 2):
                vertical_coord[Y, X] = [H_vertical / 2, W_vertical / 2]
            else:
                k = -height / (math.sqrt((Y - H_vertical / 2) ** 2 + (X - W_vertical / 2) ** 2))
                Rho = f * (t1 * math.sqrt(1 + k ** 2) + k) / (2 * t ** 2 - k ** 2 + t1 * k * math.sqrt(1 + k ** 2))

                Theta = math.atan2((Y - H_vertical / 2), (X - W_vertical / 2))

                x = Rho * math.cos(Theta) + src_x
                y = Rho * math.sin(Theta) + src_y
                vertical_coord[Y, X] = [y , x ]
    vertical_coord = np.clip(vertical_coord, [0, 0], [h - 1, w - 1])

    return vertical_coord


def show_vmatrix(h):
    """
    设置俯视图
    :return:
    """

    root = tkinter.Tk()
    root.geometry('500x500+700+20')
    root.overrideredirect(0)
    root.withdraw()
    path = filedialog.askopenfilename(title='打开图片',
                                            filetypes=[('All Files', '*'), ('BMP', '*.bmp'), ('JPG', '*.jpg')],
                                            initialdir=r"E:\dataset\ps2.0\jin\dst\val\image")
    root.destroy()

    img = cv2.flip(cv2.imread(path), 1)
    vertical_matrix = get_vmatrix(height=h)

    img_vertical = mapping(img, vertical_matrix)
    cv2.imshow('src', img)
    cv2.imshow('vertical', img_vertical)

    if cv2.waitKey() == 27:
        cv2.destroyAllWindows()
    np.save(f'matrix_vertical_800x600_{h}.npy', vertical_matrix)


if __name__ == '__main__':

    h = 56
    show_vmatrix(h)

