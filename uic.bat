echo off


pyuic5 -o ui_MainWindow.py  MainWindow.ui

pyuic5 -o ui_newProjectWindow.py  newProjectWindow.ui

pyrcc5 .\icon\res.qrc -o res_rc.py

