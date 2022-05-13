import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont
import pandas as pd
import numpy as np

def showdata(tablewidget, dataframe):

    if not isinstance(tablewidget, list):
        tablewidget=[tablewidget]
        dataframe = [dataframe, ]
    i = 0
    while i < len(tablewidget):
        tablewidget[i].setRowCount(dataframe[i].shape[0])
        tablewidget[i].setColumnCount(dataframe[i].shape[1])
        tablewidget[i].setHorizontalHeaderLabels(dataframe[i].columns.tolist())
        r = 0
        while r < dataframe[i].shape[0]:
            c = 0
            while c<dataframe[i].shape[1]:
                temp = QTableWidgetItem(str((dataframe[i].iloc[r])[c]))
                temp.setFont(QFont("times", 16, QFont.Serif))
                tablewidget[i].setItem(r, c, temp)
                c = c + 1
            r = r + 1
        i = i + 1
    return tablewidget
