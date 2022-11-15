from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.V1 = QtWidgets.QLCDNumber(self.centralwidget)
        self.V1.setGeometry(QtCore.QRect(90, 50, 81, 41))
        self.V1.setObjectName("V1")
        self.V3 = QtWidgets.QLCDNumber(self.centralwidget)
        self.V3.setGeometry(QtCore.QRect(90, 130, 81, 41))
        self.V3.setObjectName("V3")
        self.V2 = QtWidgets.QLCDNumber(self.centralwidget)
        self.V2.setGeometry(QtCore.QRect(90, 90, 81, 41))
        self.V2.setObjectName("V2")
        self.V4 = QtWidgets.QLCDNumber(self.centralwidget)
        self.V4.setGeometry(QtCore.QRect(90, 170, 81, 41))
        self.V4.setObjectName("V4")
        self.A1 = QtWidgets.QLCDNumber(self.centralwidget)
        self.A1.setGeometry(QtCore.QRect(90, 220, 81, 41))
        self.A1.setObjectName("A1")
        self.A2 = QtWidgets.QLCDNumber(self.centralwidget)
        self.A2.setGeometry(QtCore.QRect(90, 260, 81, 41))
        self.A2.setObjectName("A2")
        self.A3 = QtWidgets.QLCDNumber(self.centralwidget)
        self.A3.setGeometry(QtCore.QRect(90, 300, 81, 41))
        self.A3.setObjectName("A3")
        self.A4 = QtWidgets.QLCDNumber(self.centralwidget)
        self.A4.setGeometry(QtCore.QRect(90, 340, 81, 41))
        self.A4.setObjectName("A4")
        self.V1_b = QtWidgets.QCheckBox(self.centralwidget)
        self.V1_b.setGeometry(QtCore.QRect(60, 60, 16, 16))
        self.V1_b.setText("")
        self.V1_b.setObjectName("V1_b")
        self.V2_b = QtWidgets.QCheckBox(self.centralwidget)
        self.V2_b.setGeometry(QtCore.QRect(60, 100, 16, 16))
        self.V2_b.setText("")
        self.V2_b.setObjectName("V2_b")
        self.V_b = QtWidgets.QCheckBox(self.centralwidget)
        self.V_b.setGeometry(QtCore.QRect(60, 140, 16, 16))
        self.V_b.setText("")
        self.V_b.setObjectName("V_b")
        self.V4_b = QtWidgets.QCheckBox(self.centralwidget)
        self.V4_b.setGeometry(QtCore.QRect(60, 180, 16, 16))
        self.V4_b.setText("")
        self.V4_b.setObjectName("V4_b")
        self.A1_b = QtWidgets.QCheckBox(self.centralwidget)
        self.A1_b.setGeometry(QtCore.QRect(60, 230, 16, 16))
        self.A1_b.setText("")
        self.A1_b.setObjectName("A1_b")
        self.A2_b = QtWidgets.QCheckBox(self.centralwidget)
        self.A2_b.setGeometry(QtCore.QRect(60, 270, 16, 16))
        self.A2_b.setText("")
        self.A2_b.setObjectName("A2_b")
        self.A3_b = QtWidgets.QCheckBox(self.centralwidget)
        self.A3_b.setGeometry(QtCore.QRect(60, 310, 16, 16))
        self.A3_b.setText("")
        self.A3_b.setObjectName("A3_b")
        self.A4_b = QtWidgets.QCheckBox(self.centralwidget)
        self.A4_b.setGeometry(QtCore.QRect(60, 350, 16, 16))
        self.A4_b.setText("")
        self.A4_b.setObjectName("A4_b")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 22))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.V1_b.stateChanged.connect(self.changeTitle)    #Пишем зависимости
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))


    def changeTitle(self):
        from randomer import res
        print(res())
        #if self.V1.state
        self.V1.display(res())




if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())