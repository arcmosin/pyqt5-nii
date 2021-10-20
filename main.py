# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import numpy as np
from MyDialog import Ui_Dialog
from MyFigure import *
from pathlib import Path
import nibabel as nib



class MainDialogImgBW(QDialog,Ui_Dialog):
    def __init__(self):
        super(MainDialogImgBW,self).__init__()
        self.setupUi(self)
        self.setWindowTitle("显示matplotlib绘制图形")
        self.setMinimumSize(0,0)

        self.nii_path=''
        self.mask_path = ''
        self.shape=1
        self.check=0

        #第五步：定义MyFigure类的一个实例
        self.F = MyFigure(width=3, height=2, dpi=100)
        #self.F.plotsin()
        #第六步：在GUI的groupBox中创建一个布局，用于添加MyFigure类的实例（即图形）后其他部件。
        self.gridlayout = QGridLayout(self.groupBox)  # 继承容器groupBox
        self.gridlayout.addWidget(self.F,0,1)

        self.pushButton.clicked.connect(self.bindButton)
        self.pushButton_2.clicked.connect(self.bindButton2)
        self.horizontalSlider.valueChanged.connect(self.bindSlider)
        self.spinBox.valueChanged.connect(self.bindSpinbox)
        self.radioButton.clicked.connect(self.bindradiobutton)
        self.radioButton_2.clicked.connect(self.bindradiobutton)

    def Calculate(self,data1,data2):
        slice_idx = self.horizontalSlider.value()
        mean=0
        var=0
        arr=[]
        array1 = list(data1[:, :, slice_idx - 1])
        array2 = list(data2[:, :, slice_idx - 1])
        if not any(1 in x for x in array2):
            self.textBrowser.clear()
            self.textBrowser.append("原始图像已加载\n勾画图像已加载\n均值：\n方差：\n")
        else:
            for i in range(0,len(array1)):
                for j in range(0,len(array1[0])):
                    if array2[i][j]==1:
                        arr.append(array1[i][j])
            mean=int(np.mean(arr))
            var=int(np.var(arr))
            self.textBrowser.clear()
            self.textBrowser.append(f"原始图像已加载\n勾画图像已加载\n均值：{mean}\n方差：{var}\n")


    def showimage(self,slice_idx):
        data_nii = nib.load(Path(self.nii_path))
        data1=data_nii.get_fdata()
        self.shape = data1.shape[-1]
        self.horizontalSlider.setRange(1,data1.shape[-1])
        self.spinBox.setRange(1,data1.shape[-1])

        if not self.mask_path=='':
            data_mask = nib.load(Path(self.mask_path))
            data2 = data_mask.get_fdata()

        fig = self.F.figure
        fig.clear()
        ax = fig.add_subplot(111)  # 将画布划成1*1的大小并将图像放在1号位置，给画布加上一个坐标轴
        ax.imshow(data1[:, :, slice_idx - 1], cmap='gray')

        if self.check==1:
            array1 = list(data2[:, :, slice_idx - 1])
            a = len(array1)
            b = len(array1[0])
            pic = [[0] * a for i in range(b)]
            for i in range(a):
                for j in range(b):
                    if array1[i][j] == 0:
                        pic[i][j] = [0, 0, 0, 0]
                    else:
                        pic[i][j] = [255, 0, 0, 100]

            ax.imshow(pic, cmap='viridis')
            del array1
            del pic
        if not self.mask_path == '':
            self.Calculate(data1, data2)

        fig.canvas.draw()

    def bindradiobutton(self):
        if self.radioButton.isChecked():
            self.check = 0
        else:
            self.check = 1
        slice_idx = self.horizontalSlider.value()
        self.showimage(slice_idx)

    def bindSlider(self):
        slice_idx = self.horizontalSlider.value()
        self.spinBox.setValue(slice_idx)
        self.showimage(slice_idx)

    def bindSpinbox(self):
        slice_idx = self.spinBox.value()
        self.horizontalSlider.setValue(slice_idx)
        self.showimage(slice_idx)

    def bindButton(self):
        file_name = QFileDialog.getOpenFileName(None, "Open File", "./", "nii(*.nii.gz;*.nii)")
        self.nii_path = file_name[0]
        slice_idx = self.horizontalSlider.value()
        self.textBrowser.append("nii图像已加载\n")
        self.showimage(slice_idx)

    def bindButton2(self):
        file_name = QFileDialog.getOpenFileName(None, "Open File", "./", "nii(*.nii.gz;*.nii)")
        self.mask_path = file_name[0]
        self.textBrowser.append("mask图像已加载\n")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainDialogImgBW()
    main.show()
    #app.installEventFilter(main)
    sys.exit(app.exec_())
