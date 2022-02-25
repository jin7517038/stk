import cv2
import numpy as np
import os
import datetime
import tkinter
from PIL import Image, ImageTk


# 参数相关

path = r"C:\Users\45029\PycharmProjects\cam"

vertical_matrix_800x600 = np.load(os.path.join(path, 'matrix_vertical_800x600_56.npy'))
center_shift_matrix = np.load(os.path.join(path, "matrix_center_shift_800x600.npy"))


def mapping(src, dst_matrix):
    H, W = dst_matrix.shape[0:2]
    tx = np.array(dst_matrix[:, :, [0]].reshape(H, W), np.float32)
    ty = np.array(dst_matrix[:, :, [1]].reshape(H, W), np.float32)
    img = cv2.remap(src, ty, tx, cv2.INTER_LINEAR)
    return img


def img_pro(image):
    """
    对image进行处理：
    1. 水平翻转
    2. 中心点校正
    3. 展开成俯视图
    4. 中值滤波

    :param image: 输入图像
    :return:
    """
    img_flip = cv2.flip(image, 1)  # 水平翻转
    img_pre = cv2.warpAffine(img_flip, center_shift_matrix, (600, 800), borderValue=0)
    img_vertical = mapping(img_pre, vertical_matrix_800x600)  # 生成俯视图
    imgblur = cv2.medianBlur(img_vertical.astype(np.uint8), 3)
    return imgblur


class Camera:
    def __init__(self, save_path, save_src):
        self.save_path = save_path
        self.save_src = save_src

        self.src_save_dir = os.path.join(save_path, "src")
        os.makedirs(self.src_save_dir, exist_ok=True)
        self.V_save__dir = os.path.join(save_path, "V")
        os.makedirs(self.V_save__dir, exist_ok=True)
        self.image_num = len(os.listdir(self.src_save_dir))

        self.src_img = None
        self.V_img = None

        self.tk = tkinter.Tk()

        self.src_label = None
        self.V_label = None
        self.text_label = None
        self.text = None
        self.init_Window()
        self.tk.mainloop()

    def init_Window(self):
        """
        窗口初始化
        在窗口中，放置images_label :src_img, v_img
                 save_button, exit_button

        :return:
        """
        self.tk.title('window')
        self.tk.geometry("1420x540")

        images = tkinter.Frame(self.tk, width=1200, height=505, bg='white', bd=8, relief='ridge')

        self.src_label = self.set_picture_frame(images, (640, 480), 0.01, 0.01, 'nw')
        self.V_label = self.set_picture_frame(images, (480, 480), 0.99, 0.01, 'ne')

        images.place(relx=0.01, rely=0.025, anchor='nw')

        button_save = tkinter.Button(self.tk, text="SAVE", command=self.save_frame)
        button_save.config(width=10, height=2, font=('Helvetica', 20))
        button_save.place(relx=0.925, rely=0.08, anchor='n')

        button_exit = tkinter.Button(self.tk, text="EXIT", command=self.exit)
        button_exit.config(width=10, height=2, font=('Helvetica', 20))
        button_exit.place(relx=0.925, rely=0.35, anchor='n')

        self.text_label = tkinter.Label(self.tk, textvariable=self.text, relief='ridge')
        self.text_label.config(width=10, height=5, font=('Helvetica', 20))
        self.text_label.place(relx=0.925, rely=0.6, anchor='n')

    @staticmethod
    def set_picture_frame(master_name, size, frelx, frely, fanchor):
        """

        :param master_name:
        :param size:
        :param frelx:
        :param frely:
        :param fanchor:
        :return:
        """
        f_width, f_height = size
        # tk.Frame(父容器， width=宽度, height=高度, bg=颜色, bd=边框宽度, relief=边框样式)
        frame = tkinter.Frame(master_name, width=f_width, height=f_height, bg='white', bd=3,
                              relief='ridge')
        frame.place(relx=frelx, rely=frely, anchor=fanchor)
        LI = tkinter.Label(frame, bg='blue')
        LI.place(relx=0.5, rely=0.01, anchor='n')

        return LI

    @staticmethod
    def bgr2gif(img, size):
        """
        将图像转化为size大小,并使用ImageTk转换格式

        :param img:
        :param size:
        :return:
        """
        imgResize = cv2.resize(img, size)
        imgRGB = cv2.cvtColor(imgResize, cv2.COLOR_BGR2RGB)
        imgImage = Image.fromarray(imgRGB)
        imgTk = ImageTk.PhotoImage(image=imgImage)

        return imgTk

    def auto_update(self):
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                self.src_img = frame
                self.V_img = img_pro(frame)

        self.src_label.configure(image=self.bgr2gif(self.src_img, (640, 480)))
        self.src_label.update()

        self.V_label.configure(image=self.bgr2gif(self.V_img, (480, 480)))
        self.V_label.update()

        self.tk.after(20, self.auto_update)

    def save_frame(self):
        image_save_src_name = f"{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}" + ".jpg"
        image_save_V_name = "V" + image_save_src_name

        if self.save_src:
            image_save_src_path = os.path.join(self.src_save_dir, image_save_src_name)
            cv2.imwrite(image_save_src_path, self.src_img)

        image_save_V_path = os.path.join(self.V_save__dir, image_save_V_name)
        cv2.imwrite(image_save_V_path, self.V_img)

        imgs_num = len(os.listdir(self.src_save_dir))
        self.text = f"图片数量为: {imgs_num} "

    def exit(self):
        self.cap.release()
        cv2.destroyAllWindows()

    def __call__(self, *args, **kwargs):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.cap.set(3, 800)
        self.cap.set(4, 600)
        self.cap.set(5, 30)

        self.tk.after(20, self.auto_update)
        self.tk.mainloop()


if __name__ == '__main__':
    # 图像路径

    save_path = r"C:\Users\45029\PycharmProjects\cam\image"

    cam = Camera(save_path=save_path, save_src=True)
    cam()
