from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QIODevice
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('interface.ui', self)
        self.connections()    #just not to cahnge __init__ anymore
        self.show()

    def connections(self):
        self.MC = SerialPort()    #Creating SerialPort object to connect MicroController
        self.update_portList(self.MC.ports)
        self.connect_MC.clicked.connect(self.MC.openChosenPort)

        self.V1_checkbox.stateChanged.connect(self.update_V1)
        self.V2_checkbox.stateChanged.connect(self.update_V2)  # test function


    def update_portList(self, array):
        self.portList.addItems(array)

    def update_V1(self, state):
        if state == Qt.Checked:
            val = float(self.MC.data)
            self.V1.display(val)
        else:
            self.V1.display(0)

    def update_V2(self, state):    #test function
        if state == Qt.Checked:
            val = float(self.MC.data)
            self.V2.display(val)
        else:
            self.V2.display(0)


class SerialPort:
    def __init__(self):
        self.COM_setup()

    def COM_setup(self):
        self.serial = QSerialPort()   #Creating object of class QSerialPort
        self.serial.setBaudRate(QSerialPort.Baud9600)
        self.ports = [port.portName() for port in QSerialPortInfo().availablePorts()]
        del self.ports[0]



    def openChosenPort(self):
        port = window.portList.currentText()
        self.serial.setPortName(port)
        self.serial.setDataTerminalReady(True)
        self.serial.open(QIODevice.ReadWrite)
        window.connect_label.setText('подключено')
        self.serial.readyRead.connect(self.onRead)



    def onRead(self):
        self.data = str(self.serial.readLine(), 'utf-8').strip()    #Turning bytes to str withuot '\n'



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
    window = Ui()
    app.exec_()