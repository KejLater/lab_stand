from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QIODevice
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo



class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        self.test = True
        super().__init__()
        uic.loadUi('interface.ui', self)
        self.initializations()    #just not to change __init__ anymore
        self.show()

    def initializations(self):
        self.current_row = 0

        self.meters = [self.V1, self.V2, self.V3, self.V4, self.A1, self.A2, self.A3, self.A4] #List of volt- and ampermeters
        self.checkboxes = [self.V1_checkbox, self.V2_checkbox, self.V3_checkbox, self.V4_checkbox,
                       self.A1_checkbox, self.A2_checkbox, self.A3_checkbox, self.A4_checkbox]

        self.dict_table = {meter:[] for meter in self.meters}

        self.MC = SerialPort()    #Creating SerialPort object to connect MicroController
        self.update_portList()
        self.updatePorts.clicked.connect(self.update_portList)
        self.connect_MC.clicked.connect(self.MC.openChosenPort)
        self.connect_MC.clicked.connect(self.show_MC_connected)     #After successful connection change light and unlock LCDs

        self.add_values.clicked.connect(self.addData) #Adding numbers to the table
        self.graph_button.clicked.connect(self.graph) #Build graph

    def graph(self):
        from matplotlib import pyplot as plt
        colors = ['#FF7F50', '#A52A2A', '#458B00', '#20B2AA', '#1E90FF', '#800080', '#FF3E96', '#7F7F7F']
        n = 0
        RBtns = [self.V1_x, self.V2_x, self.V3_x, self.V4_x, self.I1_x, self.I2_x, self.I3_x, self.I4_x]
        CBxs = [self.V1_y, self.V2_y, self.V3_y, self.V4_y, self.I1_y, self.I2_y, self.I3_y, self.I4_y]
        connx = dict(zip(RBtns, self.meters))
        conny = dict(zip(CBxs, self.meters))

        for button in RBtns: #Choosing X
            if button.isChecked():
                x = self.dict_table[connx[button]]

        for box in CBxs:
            if box.isChecked():
                y = self.dict_table[conny[box]]
                plt.plot(x, y, color=colors[n])
                n = n + 1

        plt.grid()
        plt.show()

    def addData(self):
        from random import randint, random

        self.tableWidget.insertRow(self.current_row)
        for i in range(8):
            value = self.meters[i].value() + round(random(), 2) #TEST
            self.tableWidget.setItem(self.current_row, i, QtWidgets.QTableWidgetItem(str(value)))
            self.dict_table[self.meters[i]].append(value)


        self.current_row += 1
        #print(self.dict_table)


    def data_converter(self):
        if '@' in self.MC.data:
            array = self.MC.data.split('@')
            return [float(n) for n in array]
        else:
            #print(2)
            return [0 for _ in range(8)]

    def show_MC_connected(self):
        if self.MC.connected:
            self.connect_label.setText('подключено')
            self.connect_label.setStyleSheet("background-color: lightgreen")

            self.thread = MyThread()
            self.thread.mySignal.connect(self.updateAll)
            self.thread.start()

        else:
            self.connect_label.setText('ошибка')
            self.connect_label.setStyleSheet("background-color: red")


    def update_portList(self):
        self.portList.clear()
        self.MC.update_ports()
        self.portList.addItems(self.MC.ports)

    def updateAll(self):
        #print(self.MC.data)
        values = self.data_converter()
        for i in range(len(values)):
            if self.checkboxes[i].isChecked():
                self.meters[i].display(values[i])
                #self.meters[i].display(1)
            else:
                self.meters[i].display(0)




class SerialPort:
    def __init__(self):
        self.COM_setup()
        self.connected = False
        self.data = '0@0@0@0@0@0@0@0'

    def COM_setup(self):
        self.serial = QSerialPort()   #Creating object of class QSerialPort
        self.serial.setBaudRate(QSerialPort.Baud9600)
        self.update_ports()


    def update_ports(self):
        self.ports = [port.portName() for port in QSerialPortInfo().availablePorts()]
        del self.ports[0]

    def openChosenPort(self):
        from time import sleep
        if self.connected:
            self.serial.close()
        port = window.portList.currentText()
        self.serial.setPortName(port)
        self.serial.setDataTerminalReady(True)
        self.connected = self.serial.open(QIODevice.ReadWrite)


        if self.connected:
            self.serial.readyRead.connect(self.onRead)

    def onRead(self):
        self.data = str(self.serial.readLine(), 'utf-8').strip()    #Turning bytes to str withuot '\n'
        print(self.data)


class MyThread(QThread):
    mySignal = pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.value = 0

    def run(self):
        while True:
            self.mySignal.emit(self.value)
            QThread.msleep(100)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    app.exec_()