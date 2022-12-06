from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QIODevice
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('interface.ui', self)
        self.initializations()    #just not to change __init__ anymore
        self.show()

    def initializations(self):
        self.MC = SerialPort()    #Creating SerialPort object to connect MicroController
        self.update_portList(self.MC.ports)

        self.connect_MC.clicked.connect(self.MC.openChosenPort)
        self.connect_MC.clicked.connect(self.show_MC_connected)


    def checkable_initializations(self):

        self.V1_checkbox.stateChanged.connect(self.update_V1)
        self.V2_checkbox.stateChanged.connect(self.update_V2)
        self.V3_checkbox.stateChanged.connect(self.update_V3)
        self.V4_checkbox.stateChanged.connect(self.update_V4)

        self.A1_checkbox.stateChanged.connect(self.update_A1)
        self.A2_checkbox.stateChanged.connect(self.update_A2)
        self.A3_checkbox.stateChanged.connect(self.update_A3)
        self.A4_checkbox.stateChanged.connect(self.update_A4)

    def show_MC_connected(self):
        if self.MC.connected:
            self.connect_label.setText('подключено')
            self.connect_label.setStyleSheet("background-color: lightgreen")
            self.checkable_initializations()

        else:
            self.connect_label.setText('ошибка')


    def update_portList(self, array):
        self.portList.addItems(array)

    def update_V1(self, state):
        if state == Qt.Checked:
            val = float(self.MC.data)
            self.V1.display(val)
            #print('But now I am working')
        else:
            self.V1.display(0)

    def update_V2(self, state):    #test function
        if state == Qt.Checked:
            val = float(self.MC.data)
            self.V2.display(val)
        else:
            self.V2.display(0)

    def update_V3(self, state):    #test function
        if state == Qt.Checked:
            val = float(self.MC.data)
            self.V3.display(val)
        else:
            self.V3.display(0)

    def update_V4(self, state):    #test function
        if state == Qt.Checked:
            val = float(self.MC.data)
            self.V4.display(val)
        else:
            self.V4.display(0)

    def update_A1(self, state):    #test function
        if state == Qt.Checked:
            val = float(self.MC.data)
            self.A1.display(val)
        else:
            self.A1.display(0)

    def update_A2(self, state):    #test function
        if state == Qt.Checked:
            val = float(self.MC.data)
            self.A2.display(val)
        else:
            self.A2.display(0)

    def update_A3(self, state):    #test function
        if state == Qt.Checked:
            val = float(self.MC.data)
            self.A3.display(val)
        else:
            self.A3.display(0)

    def update_A4(self, state):    #test function
        if state == Qt.Checked:
            val = float(self.MC.data)
            self.A4.display(-val)
        else:
            self.A4.display(0)

class SerialPort:
    def __init__(self):
        self.COM_setup()
        self.connected = False

    def COM_setup(self):
        self.serial = QSerialPort()   #Creating object of class QSerialPort
        self.serial.setBaudRate(QSerialPort.Baud9600)
        self.ports = [port.portName() for port in QSerialPortInfo().availablePorts()]
        del self.ports[0]
        #self.ports.append('COM5')



    def openChosenPort(self):
        port = window.portList.currentText()
        self.serial.setPortName(port)
        self.serial.setDataTerminalReady(True)
        self.connected = self.serial.open(QIODevice.ReadWrite)

        if self.connected:
            self.serial.readyRead.connect(self.onRead)



    def onRead(self):
        self.data = str(self.serial.readLine(), 'utf-8').strip()    #Turning bytes to str withuot '\n'
        #print('onRead is working')


class MyThread(QThread):
    mySignal = pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.val = 0

    def run(self):
        while True:
            self.val += 1  # Получаем определённые данные
            self.mySignal.emit(self.val)  # Передаем данные для отображения
            QThread.msleep(1000)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    app.exec_()