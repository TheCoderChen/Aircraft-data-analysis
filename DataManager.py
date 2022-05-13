# 疑问：由于循环调用子函数，会不会存在栈的问题？
import pandas as pd
import os

class TDatabase:

    def __init__(self, projectPath):
        self.dataList = []  # 元素为TBattleData
        self.folder_list = []

        # 映射表，键值对，可以写死，也可以从外部读入。
        self.mapper = {'longtitude':'longt','latitude':'lant',
                       'height':'height','row':'roll','pitch':'pitch',
                       'pianhang':'pianHang','time':'Time', '时间':'Time', '经度':'longt', '纬度':'lant', '高程':'height',
                       '速度':'speed', '方向':'direction'}
        self.saveFilePath = projectPath + "/" + "Path.txt" # 项目目录下的一个路径
        # 若存在，则是打开旧项目，就读取path
        if os.path.exists(self.saveFilePath):
            self.restoreTBattleData()
        # 不存在，就是创建新项目，就创建path
        else:
            open(self.saveFilePath, 'a')

    #给一个母文件路径，读取的所有文件都属于一场战斗
    def loadTBattleData(self, path):
        print("读取路径："+path)
        print(os.path.exists(path))
        if os.path.exists(path):
            self.folder_list.append(path)
            self.dataList.append(TBattleData(path, self.mapper))

    def saveTBattleData(self):
        #w+表示覆盖写入
        with open(self.saveFilePath, 'w+') as file:
            for data in self.dataList:
                file.write(data.battlePath+'\n')
                # 将路径写入默认的path
                print("保存路径"+data.battlePath)
        pass

    #当打开上一次的文件时，新的TDatabase对象在init函数自动调用
    def restoreTBattleData(self):
        with open(self.saveFilePath, encoding='utf-8') as file:
            content = file.readlines()
        for line in content:
            # print(line.rstrip())
            self.loadTBattleData(line.rstrip())  # rstrip()删除字符串末尾的空行

    def getData(self, battleIndex, tableIndex = [-1], row = [-1], column = [-1]):
        # 错误
        if battleIndex < 0 or battleIndex >= len(self.dataList):
            return None
        # 正确
        result = (self.dataList[battleIndex]).getData(tableIndex, row, column)

        return result


    def getDataByPath(self, battlePath, tablePath):
        for battle in self.dataList:
            if battle.battlePath == battlePath:
                for table in battle.dataList:
                    if table.FilePath == tablePath:
                        return table.DataFrame

        pass

    # 只返回列名
    def getColNameByPath(self, battlePath, tablePath):
        data = self.getDataByPath(battlePath, tablePath)
        if data is None:
            return None

        return data.columns.tolist()






class TBattleData:
    """一个场次的数据:往往包含多个文件,甚至有多个子文件夹.
        一般在一个文件夹下面.
    """
    def __init__(self, parentFolderPath, mapper):
        self.dataList = []  # 元素为TDataTable对象
        self.battlePath = parentFolderPath

        allFolderPath = []
        allFolderPath.append(parentFolderPath)
        #得到所有可读根文件路径
        while len(allFolderPath) > 0:
            allChildFolder = [] #会存储此次子文件中的文件夹目录
            for singleFolderPath in allFolderPath:
                if not os.path.exists(singleFolderPath):
                    continue

                allChild = os.listdir(singleFolderPath)

                for child in allChild:
                    childPath = singleFolderPath + "/" + child
                    # 不是一个文件夹,是文件
                    if not os.path.isdir(childPath):
                        #print("文件")
                        #print(childPath)
                        self.dataList.append(TDataTable(childPath, mapper))
                    else:
                        #print("文件夹")
                        #print(childPath)
                        allChildFolder.append(childPath)
            allFolderPath = allChildFolder
            #print(allFolderPath)

    def getData(self, tableIndex, row, column):
        result = []
        #如果只有一个数，那就在列表0位置，此时可能为-1；如果多于1个，那所有值都不能为0
        if tableIndex[0] == -1:
            for data in self.dataList:
                result.append(data.DataFrame)
            return result
        else:
            for index in tableIndex:
                if index < 0 or index >= len(self.dataList):
                    # 不能容忍错误
                    return None
                # 正确
                else:
                    result.append( self.dataList[index].getData(row, column) )

            return result



class TDataTable:
    """
    存储一个表格数据.来源往往是csv文件,txt文件等。
    mapper 为dict对象. key为需要映射的原始字段名称,value为映射后标准字段名称.
    """
    def __init__(self, tablePath, mapper):  # mapper为TMapper实体
        self.State = 1
        if tablePath.endswith(".csv"):
            self.DataFrame = pd.read_csv(tablePath)
            self.FilePath = tablePath
            newColumnName = []
            for i in self.DataFrame.columns:
                newColumnName.append(mapper[i])
            self.DataFrame.columns = newColumnName
            # print(type(self.DataFrame.columns))
            # print(self.DataFrame.loc[0, 'longtitude'])
        elif tablePath.endswith(".txt"):
            pass
        else:
            self.State = -1


    def getData(self, row, column):
        Num_row = self.DataFrame.shape[0]
        Num_col = self.DataFrame.shape[1]
        #全部行
        allRow = row
        allColumn = column
        if row[0] == -1:
            allRow = list(range(0, Num_row))
        #全部列
        if column[0] == -1:
            allColumn = list(range(0, Num_col))

        result = self.DataFrame.iloc[allRow, allColumn]

        return result


