import cv2
import numpy as np
import os
import datetime
import tkinter
from tkinter import filedialog
from PIL import Image, ImageTk
import sys

# 参数相关
path = r"C:\Users\45029\PycharmProjects\cam"
sys.path.append(path)
MAP_PARAMS_PATH = r"C:\Users\45029\PycharmProjects\cam\map_params.npy"


def mapping(src, params_path=MAP_PARAMS_PATH):
    undistort_map = np.load(params_path)
    img = cv2.remap(src, undistort_map[0], undistort_map[1], cv2.INTER_LINEAR)

    return img


def img_pro(image):
    """
    对image进行处理：
    2. 中心点校正
    3. 展开成俯视图
    4. 中值滤波

    :param image: 输入图像
    :return:
    """
    img_vertical = mapping(image)  # 生成俯视图
    imgblur = cv2.medianBlur(img_vertical.astype(np.uint8), 3)
    return imgblur


class Camera:
    def __init__(self, save_path):
        self.save_path = save_path

        os.makedirs(self.save_path, exist_ok=True)

        self.src_img = None
        self.V_img = None
        self.resize_src = None
        self.resize_V = None
        self.tk = tkinter.Tk()
        self.sys_resolution = (self.tk.winfo_screenwidth(), self.tk.winfo_screenheight())
        self.y = None

        self.src_label = None
        self.V_label = None
        self.text_label = None
        self.text = tkinter.StringVar()
        self.init_Window()

        # ------------------ 临时 保存视频
        self.init_save_video(self.save_path)
        # ------------------

    def init_Window(self):
        """
        窗口初始化
        在窗口中，放置images_label :src_img, v_img
                 save_button, exit_button

        :return:
        """

        def change_save_dir():
            dir_path = filedialog.askdirectory(title="保存文件夹", initialdir=self.save_path)
            if dir_path:
                save_dir.set(dir_path)

        self.tk.title('window')
        tk_weight = int(0.9 * self.sys_resolution[0])  # 根据屏幕分辨率设置
        self.y = int((tk_weight - 50) * 6 / 17)

        tk_height = self.y + 35
        tk_width = int(40 + self.y * 17 / 6)

        self.tk.geometry(f"{tk_width}x{tk_height}")

        # 菜单栏
        menubar = tkinter.Menu(self.tk)

        # 子菜单: 文件
        filemenu = tkinter.Menu(menubar, tearoff=False)

        # 文件-> 3个组件
        save_dir = tkinter.StringVar()
        save_dir.set(self.save_path)
        filemenu.add_command(label="save dir", command=change_save_dir)

        check_save_src = tkinter.IntVar()
        check_save_src.set(1)
        check_save_bird = tkinter.IntVar()
        check_save_bird.set(0)
        filemenu.add_checkbutton(label="save src", variable=check_save_src, onvalue=1, offvalue=0)
        filemenu.add_checkbutton(label="save bird", variable=check_save_bird, onvalue=1, offvalue=0)
        menubar.add_cascade(label="文件", menu=filemenu)
        self.tk.config(menu=menubar)

        images_width = int(20 + self.y * 7 / 3)
        images_height = int(self.y + 10)
        images = tkinter.Frame(self.tk, width=images_width, height=images_height, bg='white', bd=8, relief='ridge')

        self.src_label = self.set_picture_frame(images, (int(self.y * 4 / 3), self.y), 0.00, 0.00, 'nw')
        self.V_label = self.set_picture_frame(images, (self.y, self.y), 1, 0, 'ne')

        images.place(relx=0.99, rely=0.025, anchor='ne')

        button_save = tkinter.Button(self.tk, text="SAVE",
                                     command=lambda: self.save_frame(save_dir.get(), check_save_src.get(),
                                                                     check_save_bird.get()))
        button_save.config(width=10, height=2, font=('Helvetica', 20))
        button_save.place(relx=0.085, rely=0.08, anchor='n')

        button_exit = tkinter.Button(self.tk, text="EXIT", command=self.exit)
        button_exit.config(width=10, height=2, font=('Helvetica', 20))
        button_exit.place(relx=0.085, rely=0.35, anchor='n')

        self.text_label = tkinter.Label(self.tk, textvariable=self.text, relief='ridge')
        self.text_label.config(width=10, height=4, font=('Helvetica', 20))
        self.text_label.place(relx=0.085, rely=0.6, anchor='n')

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
        LI.place(relx=0.5, rely=0, anchor='n')

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
        resize_y = self.y - 10
        ret, frame = self.cap.read()
        if ret:

            # ------------------ 临时 保存视频
            self.out.write(frame)
            # -------------------

            self.src_img = frame
            self.V_img = img_pro(frame)

            self.resize_src = self.bgr2gif(self.src_img, (int(resize_y * 4 / 3), resize_y))
            self.resize_V = self.bgr2gif(self.V_img, (resize_y, resize_y))

            self.src_label.configure(image=self.resize_src)
            self.src_label.image = self.resize_src

            self.V_label.configure(image=self.resize_V)
            self.V_label.image = self.resize_V

            self.text_label.update()

    def init_save_video(self, save_dir):
        video_save_src_name = f"{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}" + ".mp4"
        video_save_src_path = os.path.join(save_dir, video_save_src_name)

        size = (800, 600)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.out = cv2.VideoWriter(video_save_src_path, fourcc, 20, size)


    def save_frame(self, save_dir, is_save_src, is_save_bird):
        image_save_src_name = f"{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}" + ".jpg"
        image_save_V_name = "V-" + image_save_src_name

        if is_save_src:
            image_save_src_path = os.path.join(save_dir, image_save_src_name)
            cv2.imwrite(image_save_src_path, self.src_img)
        if is_save_bird:
            image_save_V_path = os.path.join(save_dir, image_save_V_name)
            cv2.imwrite(image_save_V_path, self.V_img)

        imgs_num = len(os.listdir(save_dir))
        self.text.set(f"图片数量为: \n {imgs_num} ")

    def exit(self):
        # ------------------ 临时 保存视频
        self.out.release()
        # ------------------

        self.cap.release()
        cv2.destroyAllWindows()
        self.tk.destroy()
        sys.exit()

    def __call__(self, *args, **kwargs):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            info_window = tkinter.Tk()
            info_window.geometry(f"300x100+{self.sys_resolution[0] // 2 - 150}+{self.sys_resolution[1] // 2 - 50}")
            info_window.attributes("-topmost", 1)
            message = tkinter.Label(info_window, text="没能打开全景相机，请检查接口或核实是否正在使用中")
            message.place(relx=0.5, rely=0.3, anchor='center')

            exityes = tkinter.Button(info_window, text="确定", command=lambda: exit())
            exityes.place(relx=0.5, rely=0.7, anchor='center')

        self.cap.set(3, 800)
        self.cap.set(4, 600)
        self.cap.set(5, 30)

        self.auto_update()
        while self.cap.isOpened():
            self.auto_update()

        self.tk.mainloop()


if __name__ == '__main__':
    # 图像路径

    save_path = rf"{datetime.datetime.now().strftime('%m%d-%H-%M')}"

    cam = Camera(save_path=save_path)
    cam()
