
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
        self.setWindowTitle("显示nii图像")
        self.setMinimumSize(0,0)

        #创建存放nii文件路径的属性
        self.nii_path=''
        #创建存放mask文件路径的属性
        self.mask_path = ''
        #创建记录nii文件里面图片数量的属性
        self.shape=1
        #创建用于检查radio button选择标记的属性，选择'nii图像'，为0，现在‘mask图像’，为1
        self.check = 0

        #定义MyFigure类的一个实例
        self.F = MyFigure(width=3, height=2, dpi=100)
        #在GUI的groupBox中创建一个布局，用于添加MyFigure类的实例（即图形）后其他部件。
        self.gridlayout = QGridLayout(self.groupBox)  # 继承容器groupBox
        self.gridlayout.addWidget(self.F,0,1)

        self.pushButton.clicked.connect(self.bindButton)
        self.pushButton_2.clicked.connect(self.bindButton2)
        self.pushButton_3.clicked.connect(self.bindButton3)
        self.horizontalSlider.valueChanged.connect(self.bindSlider)
        self.spinBox.valueChanged.connect(self.bindSpinbox)
        self.radioButton.clicked.connect(self.bindradiobutton)
        self.radioButton_2.clicked.connect(self.bindradiobutton)


    def Calculate(self,data1,data2):
        slice_idx = self.horizontalSlider.value()
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
            pic=np.mat(data2[:, :, slice_idx - 1])
            array_zero=np.zeros(pic.shape)
            pic=np.array([pic*255,array_zero,array_zero,pic*100])
            pic=pic.transpose((1,2,0))
            pic=np.uint(pic)
            ax.imshow(pic, cmap='viridis')

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

    def bindButton3(self):
        slice_idx = self.spinBox.value()
        data_nii = nib.load(Path(self.nii_path))
        data1 = data_nii.get_fdata()
        csv_save=data1[:, :, slice_idx - 1]
        if (self.mask_path!='') & self.check==1:
            data_mask = nib.load(Path(self.mask_path))
            data2 = data_mask.get_fdata()
            array1 = list(data2[:, :, slice_idx - 1])
            a = len(array1)
            b = len(array1[0])
            for i in range(0,a):
                for j in range(0,b):
                    if array1[i][j] == 0:
                        csv_save[i][j] = 0
                    else:
                        pass
        csv_save1=np.uint8(csv_save)
        np.savetxt(f"{slice_idx}.csv",csv_save1, delimiter=",",fmt='%u')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainDialogImgBW()
    main.show()
    sys.exit(app.exec_())
