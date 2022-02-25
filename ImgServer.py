import cv2.cv2 as cv2
import socket
import sys
import numpy as np
import time


class ImgServer:
    def __init__(self):
        self.address = ('192.168.16.199', 5007)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(self.address)
        self._init_camera()
        print("Init Done，Start ImgServe")

        self.start()

    def start(self):
        # 开始监听TCP传入连接。参数指定在拒绝连接之前，操作系统可以挂起的最大连接数量。该值至少为1，大部分应用程序设为5就可以了。

        self.socket.listen(1)
        conn, addr = self.socket.accept()
        print('Connect from:' + str(addr))
        print("Start Transferring Image")

        while True:
            time.sleep(0.01)
            try:
                state = conn.recv(16)  # 16位,代表客户发送状态
                state = int(state)
                if state:
                    # 发送图片
                    try:
                        length_ImageMessage, Data_ImageMessage = self.getImage()
                        conn.send(length_ImageMessage)
                        conn.send(Data_ImageMessage)
                    except Exception as e:
                        print(e)
                        raise Exception("send error")

            except BaseException as be:
                print(be)
                break
                # continue

        self.close()

    def _init_camera(self):
        """
        设置VideoCapture格式
        分辨率
        帧数
        """
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.cap.set(3, 800)
        self.cap.set(4, 600)
        self.cap.set(5, 30)
        self.imgEncodeParams = [int(cv2.IMWRITE_JPEG_QUALITY), 95]

    def getImage(self):
        ret, frame = self.cap.read()
        if ret:
            try:
                # cv2.imencode将图片格式转换(编码)成流数据，赋值到内存缓存中;主要用于图像数据格式的压缩，方便网络传输
                # '.jpg'表示将图片按照jpg格式编码。
                result, imgencode = cv2.imencode('.jpg', frame, self.imgEncodeParams)

                # 图片编码成字符串格式,计算长度
                data = np.array(imgencode)
                Data_ImageMessage = data.tobytes()
                length_ImageMessage = str.encode(str(len(Data_ImageMessage)).ljust(16))

                return length_ImageMessage, Data_ImageMessage
            except BaseException as e:
                exit(0)
                print(e)
        else:
            raise Exception("No Camera")

    def close(self):
        self.socket.close()
        self.cap.release()


if __name__ == '__main__':
    ImgServer()
