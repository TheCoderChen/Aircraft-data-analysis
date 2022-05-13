import sys
import random

import pandas as pd
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QSizePolicy, QWidget
from numpy import random, cos, sin, linspace
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from matplotlib.figure import Figure
from matplotlib import pyplot as plt


# from mpl_toolkits.basemap import Basemap


class MyMplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=8, height=8, dpi=100):
        # 配置中文显示
        plt.rcParams['font.family'] = ['SimHei']  # 用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
        self.fig = Figure(figsize=(width, height), dpi=dpi)  # 新建一个figure
        '''定义FigureCanvas的尺寸策略，这部分的意思是设置FigureCanvas，使之尽可能的向外填充空间。'''
        FigureCanvasQTAgg.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvasQTAgg.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvasQTAgg.updateGeometry(self)

    def testfig_1(self):
        axes = self.fig.add_subplot(111, projection='3d')
        axes.clear()
        self.fig.suptitle('测试静态图')
        z = linspace(0, 13, 1000)
        x = 5 * sin(z)
        y = 5 * cos(z)
        zd = 13 * random.random(100)
        xd = 5 * sin(zd)
        yd = 5 * cos(zd)
        axes.scatter3D(xd, yd, zd, cmap='Blues')  # 绘制散点图
        axes.plot3D(x, y, z, 'gray')  # 绘制空间曲线

    def testfig_2(self):
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.testfig_2_update)  # 每隔一段时间就会触发一次update_figure函数。
        timer.start(1000)  # 触发的时间间隔为1秒。

    def testfig_2_update(self):
        axes = self.fig.add_subplot(221, projection='3d')
        axes.clear()
        self.fig.suptitle('测试动态图')
        l = [random.randint(0, 10) for i in range(4)]
        axes.plot([0, 1, 2, 3], l, 'r')
        axes.set_ylabel('动态图：Y轴')
        axes.set_xlabel('动态图：X轴')
        axes.grid(True)

    def fig_clear(self):
        self.fig.clear()

    def line1d_with_time(self, data):
        self.fig_clear()
        axes = axes = self.fig.add_subplot(111)
        axes.plot(data)

    def line2d(self, datax, datay):
        self.fig_clear()
        axes = axes = self.fig.add_subplot(111)
        axes.plot(datax, datay)

    def line3d(self, datax, datay, dataz):
        self.fig_clear()
        axes = axes = self.fig.add_subplot(111, projection='3d')
        axes.plot(datax, datay, dataz)



class MatplotlibWidget(QWidget):
    def __init__(self, parent=None):
        super(MatplotlibWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        self.mpl = None
        self.mpl_bar = False

    def refresh(self):
        item_list = list(range(self.layout.count()))
        item_list.reverse()
        for i in item_list:
            item = self.layout.itemAt(i)
            self.layout.removeItem(item)
            if item.widget():
                item.widget().deleteLater()
        self.layout.addWidget(self.mpl)
        if self.mpl_bar:
            self.layout.addWidget(NavigationToolbar2QT(self.mpl, self))
        print(self.findChildren(MyMplCanvas))

    def set(self, data=None, bar=False, data_index=None, **setting):
        self.mpl = MyMplCanvas(self)
        if data_index is None:
            data_index = []
        self.mpl_bar = bar
        if type(data) is pd.DataFrame:
            pass
        else:
            return False
        mapper = {'longtitude': 'longt', 'latitude': 'lant',
                  'height': 'height', 'row': 'roll', 'pitch': 'pitch',
                  'pianhang': 'pianHang', 'time': 'Time', '时间': 'Time', '经度': 'longt', '纬度': 'lant',
                  '高程': 'height',
                  '速度': 'speed', '方向': 'direction'}
        for i in data_index:
            if i not in list(mapper.values()):
                data_index.remove(i)
        if len(data_index) == 1:
            draw_data = data[data_index[0]]
            self.mpl.line1d_with_time(draw_data)
        elif len(data_index) == 2:
            if 'Time' in data_index:
                data_index.remove('Time')
                self.mpl.line1d_with_time(data[data_index[0]])
            else:
                self.mpl.line2d(data[data_index[0]], data[data_index[1]])
        elif len(data_index) == 3:
            if 'Time' in data_index:
                data_index.remove('Time')
                self.mpl.line2d(data[data_index[0]], data[data_index[1]])
            else:
                self.mpl.line3d(data[data_index[0]], data[data_index[1]], data[data_index[2]])

    def set_test(self, bar=True, no=0):
        self.mpl_bar = bar
        if no == 0:
            self.mpl.fig_clear()
        elif no == 1:
            self.mpl.testfig_1()
        elif no == 2:
            self.mpl.testfig_2()
        else:
            pass


def temp_data():
    ans = pd.read_csv(r'C:\Users\CK\Desktop\demo(1)\demo(1)\Battle1\data1.csv')
    return ans


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = MatplotlibWidget()
    ui.set(temp_data(), False, ['height', 'asofjhasu8o'])
    ui.refresh()
    print(ui.findChildren(MyMplCanvas))
    # ui.set(temp_data(), False, ['height', 'longt'])
    # ui.refresh()
    print(ui.findChildren(MyMplCanvas))
    ui.show()
    sys.exit(app.exec_())
