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
        self.meters = [self.V1, self.V2, self.V3, self.V4, self.A1, self.A2, self.A3, self.A4]
        self.checkboxes = [self.V1_checkbox, self.V2_checkbox, self.V3_checkbox, self.V4_checkbox,
                       self.A1_checkbox, self.A2_checkbox, self.A3_checkbox, self.A4_checkbox]

        self.MC = SerialPort()    #Creating SerialPort object to connect MicroController

        self.update_portList()
        self.updatePorts.clicked.connect(self.update_portList)


        self.connect_MC.clicked.connect(self.MC.openChosenPort)
        self.connect_MC.clicked.connect(self.show_MC_connected)     #After successful connection change light and unlock LCDs

    def graph(self, x, y):
        from matplotlib import pyplot as plt

        plt.scatter(x, y)
        plt.grid()
        plt.show()


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
        #print(self.data)


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