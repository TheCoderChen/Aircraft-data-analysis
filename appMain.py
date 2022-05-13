from datetime import datetime

from PyQt5.QtCore import QDateTime, QDate
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileSystemModel, QFileDialog, QWidget
from ui_MainWindow import *
from tableshow import *
from DataManager import *
from ui_newProjectWindow import *
from matplotlibwidget import *
import os

class TProject:
    def __init__(self):
        self.dataBase = None
        self.project_dir = ''
        self.project_name = ''
        self.folder_list = []
        self.flag = 0 # 0为未打开项目，1为新建项目，2为打开项目

    # 创建项目
    def createProject(self, project_dir, project_name):
        self.project_name = project_name
        self.project_dir = project_dir
        self.dataBase = TDatabase(projectPath=project_dir)
        self.flag = 1
        # with open(project_dir + '/' + project_name + '.txt', 'w') as f:
        #     pass

    # 添加资源文件夹
    def addFolder(self, folder_dirs):
        self.folder_list = folder_dirs
        for folder_dir in folder_dirs:
            self.dataBase.loadTBattleData(folder_dir)
            # with open(self.project_dir + '/' + self.project_name + '.txt', 'a') as f:
            #     f.write(folder_dir + '\n')

    def openProject(self, project_dir):
        self.project_dir = project_dir
        self.dataBase = TDatabase(projectPath=project_dir)
        self.folder_list = self.dataBase.folder_list
        self.flag = 2

    def saveProject(self):
        self.dataBase.saveTBattleData()

    def getTableData(self, folder_dir, table_dir):
        df = self.dataBase.getDataByPath(folder_dir, table_dir)
        return df

    def draw(self, widget, data, data_index):
        widget.set(data=data, data_index=data_index, bar=True)
        widget.refresh()


project = TProject()

class AppMain(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)  # 构造 MainWindow 窗体
        self.ui = Ui_MainWindow()  # 实例化Ui_MainWindow
        self.ui.setupUi(self)  # 初始化窗体

        # 创建项目菜单响应
        self.ui.actionNewProject.triggered.connect(self.newProject)
        self.ui.actionOpenProject.triggered.connect(self.openProject)
        self.ui.actionSaveProject.triggered.connect(self.saveProject)

        self.newProjectWindow = NewProjectWindow()
        self.newProjectWindow.my_Signal.connect(self.showFolder)
        self.fileModel = None
        self.initUi()
        # 切换数据tab的响应
        self.ui.tabWidget_2.currentChanged.connect(self.tabchange)
        # 绘制按钮的响应
        self.ui.drawBtn.clicked.connect(self.clickDraw)
        #改变时间的响应（两个时间条联动）
        self.ui.dateTimeEdit.dateTimeChanged.connect(self.datatimechange1)
        self.ui.dateTimeEdit_2.dateTimeChanged.connect(self.datatimechange2)
        self.ui.horizontalSlider.valueChanged.connect(self.sliderchange1)
        self.ui.horizontalSlider_2.valueChanged.connect(self.sliderchange2)
        self.ui.searchBtn.clicked.connect(self.search)


    def initUi(self):
        self.ui.tabWidget_2.removeTab(1)
        self.ui.tabWidget_2.removeTab(0)
        self.ui.tabWidget_2.tabCloseRequested.connect(self.tabClose)
        self.ui.dateTimeEdit.setMinimumDateTime(QDateTime(QDate(2000, 1, 1)))
        self.ui.dateTimeEdit.setMaximumDateTime(QDateTime(QDate(2000, 2, 1)))


    def tabClose(self, index):
        self.ui.tabWidget_2.removeTab(index)

    def search(self):
        search_str = self.ui.searchEdit.text()
        if search_str == '':
            return
        # 遍历model， 如果有匹配的，则选中treeview中对应的行
        for i in range(self.fileModel.rowCount()):
            if self.fileModel.item(i).text() == search_str:
                self.ui.treeView.setCurrentIndex(self.fileModel.index(i))
                return

    def newProject(self):
        self.newProjectWindow.show()

    def openProject(self):
        project_dir = QFileDialog.getExistingDirectory(self, r'打开项目文件夹', "./")
        if project_dir == '':
            return
        saveFilePath = project_dir + "/" + "Path.txt" # 项目目录下的一个路径

        if not os.path.exists(saveFilePath):
            reply = QMessageBox.warning(self, "警告", "该项目不存在，请先创建项目", QMessageBox.Ok|QMessageBox.Cancel, QMessageBox.Ok)
            # 如何点击了OK，则跳转到新建项目界面
            if reply == QMessageBox.Ok:
                self.newProjectWindow.show()
            return
        project.openProject(project_dir)
        self.showFolder()

    def showFolder(self):
        self.fileModel = QFileSystemModel()
        if len(project.folder_list) == 0:
            QMessageBox.information(self, "提示", "项目为空！", QMessageBox.Yes)
            return
        self.fileModel.setRootPath(project.folder_list[0])
        self.ui.treeView.setModel(self.fileModel)
        self.ui.treeView.setRootIndex(self.fileModel.index(project.folder_list[0]))  # 根目录生效
        for i in [1, 2, 3]:
            self.ui.treeView.setColumnHidden(i, True)
        self.ui.treeView.selectionModel().currentChanged.connect(self.onCurrentChanged)

    def saveProject(self):
        # 如果项目存在， 提示请先打开一个项目
        if project.flag == 0:
            messageBox = QMessageBox()
            # 设置为警告
            messageBox.setIcon(QMessageBox.Warning)
            messageBox.setWindowTitle("提示")
            messageBox.setText("请先新建或打开一个项目！")
            # 添加按钮新建项目、打开项目
            Qyes1 = messageBox.addButton("新建项目", QMessageBox.YesRole)
            Qyes2 = messageBox.addButton("打开项目", QMessageBox.YesRole)
            QNo = messageBox.addButton("取消", QMessageBox.NoRole)
            messageBox.exec_()
            # 如果点击了新建项目，则跳转到新建项目界面
            if messageBox.clickedButton() == Qyes1:
                messageBox.close()
                self.newProjectWindow.show()

            # 如果点击了打开项目，则跳转到打开项目界面
            elif messageBox.clickedButton() == Qyes2:
                messageBox.close()
                self.openProject()

            return
        project.saveProject()
        # 提示保存成功
        QMessageBox.information(self, "提示", "保存成功！", QMessageBox.Yes)

    def onCurrentChanged(self, current, previous):
        # 判断选中的是文件还是文件夹
        if self.fileModel.isDir(current):
            pass
        else:
            # 获取所有的 tab 名
            tab_names = []
            for i in range(self.ui.tabWidget_2.count()):
                tab_names.append(self.ui.tabWidget_2.tabText(i))
            # 判断是否已经存在该文件
            if self.fileModel.fileName(current) in tab_names:
                self.ui.tabWidget_2.setCurrentIndex(tab_names.index(self.fileModel.fileName(current)))
            else:
                # 获取选中文件路径
                file_path = self.fileModel.filePath(current)
                # 获取选中文件根路径
                root_path = self.fileModel.rootPath()
                df = project.getTableData(root_path, file_path)
                tableWidget = self.addTab(current)
                showdata(tableWidget, df)
                tableWidget.resizeColumnsToContents()
                tableWidget.resizeRowsToContents()

    def addTab(self, current):
        # 获取当前tab数
        tab_count = self.ui.tabWidget_2.count()
        # 创建新的tab
        new_tab = QWidget()

        #绑定tab和所对应文件
        new_tab.file_path = self.fileModel.filePath(current)
        new_tab.root_path = self.fileModel.rootPath()

        #储存tab对应数据的时间表
        new_tab.data_time=project.getTableData(new_tab.root_path, new_tab.file_path)["Time"].tolist()

        # 创建新的table
        new_table = QTableWidget()
        # 将table添加到tab
        new_tab.setLayout(QVBoxLayout())
        new_tab.layout().addWidget(new_table)
        # 将tab添加到tabWidget
        self.ui.tabWidget_2.addTab(new_tab, current.data())
        # 设置当前tab
        self.ui.tabWidget_2.setCurrentIndex(tab_count)
        # 返回新的table
        return new_table

    def tabchange(self):
        # ps这个current index  是从左到右依次增加的
        current_widget = self.ui.tabWidget_2.currentWidget()
        df = project.getTableData(current_widget.root_path, current_widget.file_path)
        columns = df.columns.tolist()
        columns.remove("Time")
        self.ui.comboBox.clear()
        self.ui.comboBox.insertItems(0, columns)
        # self.ui.comboBox.insertItems(0, '轨迹图')

        # 时间条和时间框的范围
        self.ui.horizontalSlider.setMaximum(len(current_widget.data_time) - 1)
        self.ui.horizontalSlider.setMinimum(0)
        self.ui.horizontalSlider_2.setMaximum(len(current_widget.data_time) - 1)
        self.ui.horizontalSlider_2.setMinimum(0)
        self.ui.dateTimeEdit.setMinimumDateTime(QDateTime.fromString(df["Time"].iloc[0], "yyyy-MM-dd"))
        self.ui.dateTimeEdit.setMaximumDateTime(QDateTime.fromString(df["Time"].iloc[-1], "yyyy-MM-dd"))
        self.ui.dateTimeEdit_2.setMinimumDateTime(QDateTime.fromString(df["Time"].iloc[0], "yyyy-MM-dd"))
        self.ui.dateTimeEdit_2.setMaximumDateTime(QDateTime.fromString(df["Time"].iloc[-1], "yyyy-MM-dd"))

        #时间框和时间条的值
        self.ui.dateTimeEdit.setDateTime(QDateTime.fromString(df["Time"].iloc[0], "yyyy-MM-dd"))
        self.ui.dateTimeEdit_2.setDateTime(QDateTime.fromString(df["Time"].iloc[-1], "yyyy-MM-dd"))
        self.ui.horizontalSlider.setValue(0)
        self.ui.horizontalSlider_2.setValue(len(current_widget.data_time)-1)

    def clickDraw(self):
        current_widget = self.ui.tabWidget_2.currentWidget()
        df = project.getTableData(current_widget.root_path, current_widget.file_path)
        # 获取时间起始和终止的数据
        start_time = self.ui.dateTimeEdit.dateTime().toString("yyyy-MM-dd")
        end_time = self.ui.dateTimeEdit_2.dateTime().toString("yyyy-MM-dd")
        # 将时间转化为datetime
        start_time = datetime.strptime(start_time, "%Y-%m-%d")
        end_time = datetime.strptime(end_time, "%Y-%m-%d")
        # 裁剪数据df
        df['Time'] = df['Time'].astype('datetime64')
        df = df[(df["Time"] >= start_time) & (df["Time"] <= end_time)]
        # 将Time设置为index
        df.set_index("Time", inplace=True)

        project.draw(self.ui.MatWidget, df, [self.ui.comboBox.currentText()])
        # 跳转到图片tab
        self.ui.tabWidget.setCurrentIndex(1)

    def datatimechange1(self):
         timet = self.ui.dateTimeEdit.dateTime()
         current_widget = self.ui.tabWidget_2.currentWidget()
         m=60*60*24
         nexttime=timet
         print(1)
         for timet2 in current_widget.data_time:
             if abs(QDateTime.fromString(timet2,"yyyy-MM-dd").toTime_t()-timet.toTime_t())<=m:
                 m=abs(QDateTime.fromString(timet2,"yyyy-MM-dd").toTime_t()-timet.toTime_t())
                 nexttime = QDateTime.fromString(timet2,"yyyy-MM-dd")
         print(1)
         nextindex=current_widget.data_time.index(nexttime.toString("yyyy-MM-dd"))
         print(1)
         self.ui.dateTimeEdit.setDateTime(nexttime)
         print(1)
         self.ui.horizontalSlider.setValue(nextindex)


    def datatimechange2(self):
        timet = self.ui.dateTimeEdit_2.dateTime()
        current_widget = self.ui.tabWidget_2.currentWidget()
        m = 60 * 60 * 24
        nexttime = timet

        for timet2 in current_widget.data_time:
            if abs(QDateTime.fromString(timet2, "yyyy-MM-dd").toTime_t() - timet.toTime_t()) <= m:
                m = abs(QDateTime.fromString(timet2, "yyyy-MM-dd").toTime_t() - timet.toTime_t())
                nexttime = QDateTime.fromString(timet2, "yyyy-MM-dd")

        nextindex = current_widget.data_time.index(nexttime.toString("yyyy-MM-dd"))
        self.ui.dateTimeEdit_2.setDateTime(nexttime)
        self.ui.horizontalSlider_2.setValue(nextindex)

    def sliderchange1(self):

        current_widget = self.ui.tabWidget_2.currentWidget()
        nexttime = QDateTime.fromString(current_widget.data_time[self.ui.horizontalSlider.value()], "yyyy-MM-dd")
        self.ui.dateTimeEdit.setDateTime(nexttime)

    def sliderchange2(self):

        current_widget = self.ui.tabWidget_2.currentWidget()
        nexttime = QDateTime.fromString(current_widget.data_time[self.ui.horizontalSlider_2.value()], "yyyy-MM-dd")
        self.ui.dateTimeEdit_2.setDateTime(nexttime)


class NewProjectWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.ProjectAddressBtn.clicked.connect(self.getProjectAddress)
        self.ui.AddFolderBtn.clicked.connect(self.addFolder)
        self.ui.SubFolderBtn.clicked.connect(self.subFolder)
        self.ui.OKBtn.clicked.connect(self.ok)
        self.ui.OKBtn_2.clicked.connect(self.close)
        # 让多窗口之间传递信号 刷新主窗口信息
    my_Signal = QtCore.pyqtSignal(str)

    def getProjectAddress(self):
        project_dir = QFileDialog.getExistingDirectory(self, r'新建项目路径', "./")
        self.ui.ProjectAddressEdit.setText(project_dir)

    def addFolder(self):
        folder_dir = QFileDialog.getExistingDirectory(self, r'选择资源文件夹', "./")
        self.ui.FolderListWidget.addItem(folder_dir)

    def subFolder(self):
        self.ui.FolderListWidget.takeItem(self.ui.FolderListWidget.currentRow())

    def ok(self):
        # 获取文件夹列表
        FolderList = []
        for i in range(self.ui.FolderListWidget.count()):
            FolderList.append(self.ui.FolderListWidget.item(i).text())
        # 获取项目路径
        project_dir = self.ui.ProjectAddressEdit.text()
        # 如果为空，则弹出提示
        if project_dir == "":
            QMessageBox.warning(self, "警告", "项目路径不能为空！")
            return
        project_name = self.ui.ProjectNameEdit.text()
        if project_name == "":
            QMessageBox.warning(self, "警告", "项目名称不能为空！")
        # 如果不存在项目路径，则创建
        if not os.path.exists(project_dir):
            os.mkdir(project_dir)
        # 创建项目文件夹
        project_dir = os.path.join(project_dir, project_name)
        os.mkdir(project_dir)

        project.createProject(project_dir, project_name)
        project.addFolder(FolderList)
        self.close()
        content = '1'
        self.my_Signal.emit(content)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = AppMain()
    main.show()
    sys.exit(app.exec_())

