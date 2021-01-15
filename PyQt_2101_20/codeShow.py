import importlib
import os
import sys
from PyQt5 import QtCore
from PyQt5.QtCore import QTimer,QCoreApplication
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
from window import Ui_MainWindow  # 由qtdesigner 生成的布局
import subprocess
import tkinter as tk
from tkinter import filedialog
from PyQt5 import QtGui
import cv2
import time
import signal
from PyQt5.QtWidgets import *
import qimage2ndarray


class show_thread(QtCore.QThread):
    updated = QtCore.pyqtSignal(str)        # 创建一个自定义信号

    def __init__(self, show_win, cmd):      # 构造函数属性包括pyqt控件和cmd命令
        self.cmd = cmd
        self.show_win = show_win
        super().__init__()

    def run(self):
        # do some functionality
        while self.cmd.poll is not None:
            # self.show_win.append(str(self.cmd.stdout.readline()))
            output = self.cmd.stdout.readline()             # 读取命令输出
            self.updated.emit(str(output.decode()))


class codeShow(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(codeShow, self).__init__()
        self.setupUi(self)
        # 下面将输出重定向到textBrowser中
        # sys.stdout = EmittingStr(textWritten=self.outputWritten)
        # sys.stderr = EmittingStr(textWritten=self.outputWritten)
        self.timer_camera = QTimer()  # 定义定时器，用于控制显示视频的帧率
        self.cap = cv2.VideoCapture()
        self.CAM_NUM = 0
        self.a = 5

        self.connect()
        self.PrepParameters()
        self.show_Text_Msg()
        # self.Timer = QTimer()
        # self.Timer.timeout.connect(self.TimerOutFun)

    # 布局参数初始化
    def PrepParameters(self):
        # self.RecordFlag=0
        self.pushButton_start.setEnabled(True)
        self.pushButton_stop.setEnabled(False)
        self.pushButton_exit.setEnabled(True)

        # self.Text_Msg.setText("请先选择要运行的模型")

    # #信号槽设置
    def connect(self):
        self.comboBox_NetChoose.currentTextChanged.connect(self.chooseNet)
        self.pushButton_code1.clicked.connect(self.choose_code)
        self.pushButton_code2.clicked.connect(self.choose_file)
        self.pushButton_code3.clicked.connect(self.choose_model)
        self.pushButton_code4.clicked.connect(self.choose_video)
        self.pushButton_save.clicked.connect(self.choose_savedir)
        self.lineEdit_code1.textChanged.connect(self.show_Text_Msg)
        self.lineEdit_code2.textChanged.connect(self.show_Text_Msg)
        self.lineEdit_code3.textChanged.connect(self.show_Text_Msg)
        self.lineEdit_code4.textChanged.connect(self.show_Text_Msg)
        self.lineEdit_code5.textChanged.connect(self.show_Text_Msg)
        self.pushButton_start.clicked.connect(self.imshow)
        self.radioButton_camera.clicked.connect(self.button_open_camera)
        self.pushButton_exit.clicked.connect(self.close_video)
        self.timer_camera.timeout.connect(self.show_camera)
        self.pushButton_OK.clicked.connect(self.send_msg)
        self.pushButton_OK.clicked.connect(self.start_thread)
        self.pushButton_STOP.clicked.connect(self.stop_thread)


    # # 模型选择—>布局名称改变
    def chooseNet(self):
        if self.comboBox_NetChoose.currentIndex() == 0:
            self.CodePath1 = ''  # python py文件
            self.CodePath2 = ''  # cfg文件
            self.CodePath3 = ''  # 选择训练好的模型
            self.CodePath4 = ''  # 日志文件保存路径
            self.CodePath5 = ''  # 可视化视频帧保存路径
            self.pushButton_code1.setText('参数1')
            self.pushButton_code2.setText('参数2')
            self.pushButton_code3.setText('参数3')
            self.pushButton_code4.setText('参数4')
            self.pushButton_save.setText('变啦')

        elif self.comboBox_NetChoose.currentIndex() == 1:
            self.CodePath1 = 'python scripts/demo_inference.py'  # python py文件
            self.CodePath2 = ' --cfg configs/coco/resnet/256x192_res50_lr1e-3_1x.yaml'  # cfg文件
            self.CodePath3 = ' --checkpoint input/exp/2_AlphaPose/final_DPG.pth'  # 选择训练好的模型
            # self.CodePath4 = ' --outdir out/webcam_1 --vis --webcam 0'  # 日志文件保存路径
            self.CodePath4 = ' --indir examples/demo/pic/pic_4 --outdir out/pic/pic_4 --save_img --detbatch 1 --posebatch 30'  # 日志文件保存路径
            self.CodePath5 = ''  # 可视化视频帧保存路径
            self.pushButton_code1.setText('code')
            self.pushButton_code2.setText('cfg')
            self.pushButton_code3.setText('input')
            self.pushButton_code4.setText('out')
            self.pushButton_save.setText('save')

        elif self.comboBox_NetChoose.currentIndex() == 2:
            # self.CodePath1 = 'python scripts/demo_inference.py'  # python py文件
            # self.CodePath2 = ' --cfg configs/coco/resnet/256x192_res50_lr1e-3_1x.yaml'  # cfg文件
            # self.CodePath3 = ' --checkpoint input/exp/2_AlphaPose/final_DPG.pth'  # 选择训练好的模型
            # self.CodePath4 = ' --indir examples/demo/pic/pic_4 --outdir out/pic/pic_4 --save_img --detbatch 1 --posebatch 30'  # 日志文件保存路径
            # self.CodePath5 = ''  # 可视化视频帧保存路径
            self.CodePath1 = 'python ex1.py'  # python py文件
            self.CodePath2 = ''  # cfg文件
            self.CodePath3 = ''  # 选择训练好的模型
            self.CodePath4 = ''  # 日志文件保存路径
            self.CodePath5 = ''  # 可视化视频帧保存路径
            self.pushButton_code1.setText('变啦')
            self.pushButton_code2.setText('变啦')
            self.pushButton_code3.setText('变啦')
            self.pushButton_code4.setText('变啦')
            self.pushButton_save.setText('变啦')

        elif self.comboBox_NetChoose.currentIndex() == 3:
            self.CodePath1 = 'python social-distancing-prediction-master/code/inference/main_simple.py'  # python py文件
            self.CodePath2 = ' social-distancing-prediction-master/test/VID379.mp4'  # 视频文件
            self.CodePath3 = ''  # 暂时无法选择模型
            self.CodePath4 = ' social-distancing-prediction-master/test/output_379_simple'  # 日志文件保存路径
            self.CodePath5 = ' --pred_vis_path social-distancing-prediction-master/test/visualization  --is_baseline'  # 可视化视频帧保存路径
            self.pushButton_code1.setText('program')
            self.pushButton_code2.setText('video')
            self.pushButton_code3.setText('model(暂无)')
            self.pushButton_code4.setText('output')
            self.pushButton_save.setText('visulization')

        self.lineEdit_code1.setText(self.CodePath1)
        self.lineEdit_code2.setText(self.CodePath2)
        self.lineEdit_code3.setText(self.CodePath3)
        self.lineEdit_code4.setText(self.CodePath4)
        self.lineEdit_code5.setText(self.CodePath5)

# 输入生成

    # # 文本框的指针光标
    def outputWritten(self, text):
        cursor = self.Text_Msg.textCursor()  # 获得指针对象（这里是一个文本光标）
        cursor.movePosition(QtGui.QTextCursor.End)  # 每次修改内容，自动将光标移到最后
        cursor.insertText(text)  # insertText()将文本插入到光标所在位置的文档中
        self.Text_Msg.setTextCursor(cursor)  # 要想使操作生效需要调用一下setTextCursor()函数
        self.Text_Msg.ensureCursorVisible()
        importlib.reload(sys)  # 重新载入sys

    # # 关闭事件
    def closeEvent(self, event):  # 重写。关闭事件
        """Shuts down application on close."""
        # Return stdout to defaults.
        sys.stdout = sys.__stdout__
        super().closeEvent(event)

    # # 加载文件(命令)的选择
    def choose_code(self):
        try:
            codename,fileType= QFileDialog.getOpenFileName(self, 'choose_code', './', 'Image files(*.jpg *.gif *.png)')  # 可设置默认路径与可选文件类型
            # foldername = QFileDialog.getExistingDirectory(self, '标题', './')  # 可设置默认路径
            self.lineEdit_code1.setText('python'+codename+'')
            print(codename)
        except:
            print("未选择文件")

    def choose_file(self):
        try:
            filename,fileType= QFileDialog.getOpenFileName(self, 'choose_file', './', 'Image files(*.jpg *.gif *.png)')  # 可设置默认路径与可选文件类型
            self.lineEdit_code2.setText(' --'+filename+'')
        except:
            print("未选择文件")

    def choose_model(self):
        try:
            modelname,fileType= QFileDialog.getOpenFileName(self, 'choose_model', './', 'Image files(*.jpg *.gif *.png)')  # 可设置默认路径与可选文件类型
            self.lineEdit_code3.setText(' --'+modelname+'')
        except:
            print("未选择文件")

    def choose_video(self):
        try:
            videoname, fileType= QFileDialog.getOpenFileName(self, 'choose_video', './', 'Image files(*.jpg *.gif *.png)')  # 可设置默认路径与可选文件类型
            self.lineEdit_code5.setText(' --'+videoname+'')
        except:
            print("未选择文件")

    def choose_savedir(self):
        try:
            savedirname= QFileDialog.getSaveFileName(self, '标题', './', 'Image files(*.jpg *.gif *.png)')  # 可设置默认路径与可选文件类型
            self.lineEdit_code5.setText(' --pred_vis_path '+savedirname+' --is_baseline')
        except:
            print("未选择文件")

    # # 命令行生成
    def show_Text_Msg(self):
        self.Text_Msg.setText(self.lineEdit_code1.text()+
                              self.lineEdit_code2.text()+
                              self.lineEdit_code3.text()+
                              self.lineEdit_code4.text()+
                              self.lineEdit_code5.text())  # 2
        self.str = self.Text_Msg.toPlainText()

    # 在终端运行命令
    def send_msg(self):
        alphapose_cwd = 'D:\\Users\\wmj\\AlphaPose_1.1+\\AlphaPose-master'
        try:
            self.cmd = subprocess.Popen(self.str, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, \
                                        cwd=alphapose_cwd, bufsize=1)
        except:
            print("出现错误")

    # 开启子线程
    def start_thread(self):
        if self.comboBox_NetChoose.currentIndex() == 0:
            reply_model = QMessageBox.information(self, 'Message', "请先选择模型",
                                                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            print(reply_model)
        else:
            self.msg_show = show_thread(self.Text_Msg, self.cmd)  # 创建实例
            self.msg_show.updated.connect(self.show_msg)  # 自定义信号updated连接
            self.msg_show.start()  # 开启线程

    def show_msg(self, msg):
        print(msg)
        self.Text_Msg.append(msg)

    def stop_thread(self, event):
        if self.comboBox_NetChoose.currentIndex() == 0:
            reply_model = QMessageBox.information(self, 'Message', "请先选择模型",
                                                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            print(reply_model)
        else:
            reply_run = QMessageBox.question(self, 'Message', "确认退出运行吗?", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if reply_run == QMessageBox.Yes:
                self.msg_show.terminate()
                self.Text_Msg.setText(self.str)
            elif reply_run == QMessageBox.No:
                pass


# 输出显示
    # # 获取输出的文件路径
    def getFileList(slef, dir, Filelist, ext=None):
        # 获取文件夹及其子文件夹中文件列表
        # 输入 dir：文件夹根目录
        # 输入 ext: 扩展名
        # 返回：文件路径列表
        newDir = dir
        if os.path.isfile(dir):
            if ext is None:
                Filelist.append(dir)
            else:
                if ext in dir[-3:]:  # jpg为-3/py为-2
                    Filelist.append(dir)

        elif os.path.isdir(dir):
            for s in os.listdir(dir):
                newDir = os.path.join(dir, s)
                slef.getFileList(newDir, Filelist, ext)
        return Filelist

    # # 显示输出内容
    def imshow(self):

        if self.radioButton_video.isChecked() == False:
            reply_video = QMessageBox.information(self, 'Message', "请先选择视频文件选择框",
                                                QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            print(reply_video)
        else:
            # # # 打开选择文件夹对话框
            root = tk.Tk()
            root.withdraw()
            Folderpath = filedialog.askdirectory()  # 获得选择好的文件夹
            print('Folderpath:', Folderpath)
            # # #检索文件
            imglist = self.getFileList(Folderpath, [], 'jpg')
            print('本次执行检索到 ' + str(len(imglist)) + ' 个jpg文件\n')

            for imgpath in imglist:
                img = cv2.imread(imgpath)
                # img = cv2.resize(img, (480, 320))  # 这里不起作用
                img_h = img.shape[0]
                img_w = img.shape[1]
                self.lcdNumber_pichight.display(img_h)
                self.lcdNumber_picwight.display(img_w)

                img = cv2.resize(img, (480, 360))
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                qimg = qimage2ndarray.array2qimage(img)
                self.Box_out1.setPixmap(QtGui.QPixmap(qimg))
                self.Box_out1.show()
                # self.Box_out1.clear()
                cv2.waitKey(30)
                frame_rate = 24
                self.lcdNumber_frame.display(frame_rate)
                if self.a == 1:
                    break

    # 摄像头输入
    def button_open_camera(self):
        if self.timer_camera.isActive() == False:  # 若定时器未启动
            flag = self.cap.open(self.CAM_NUM)
            if flag == False:  # flag表示open()成不成功
                reply_camera = QMessageBox.information(self, 'Message', "请检查相机是否连接正确",
                                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
                print(reply_camera)
            else:
                self.timer_camera.start(30)  # 每过30ms从摄像头中取一帧显示
        else:
            self.timer_camera.stop()  # 关闭定时器
            self.cap.release()
            self.Box_input.clear()

    def show_camera(self):
        flag, self.image = self.cap.read()
        show = cv2.resize(self.image, (480, 360))
        show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)
        showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0], QtGui.QImage.Format_RGB888)
        self.Box_input.setPixmap(QtGui.QPixmap.fromImage(showImage))

    def close_video(self):
        # self.radioButton_video.setChecked(False)
        # self.pushButton_stop.setEnabled(True)
        self.a = 1
        self.timer_camera.stop()  # 关闭定时器
        self.cap.release()
        self.Box_input.clear()
        self.Box_out1.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = codeShow()
    myWin.show()
    sys.exit(app.exec_())
