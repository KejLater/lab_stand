from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore import QIODevice

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('interface.ui', self)
        self.connections() #just not to cahnge __init__
        self.show()

    def connections(self):
        self.V1_checkbox.stateChanged.connect(self.updateNumber)
        self.V2_checkbox.stateChanged.connect(self.updateNumber1)
        self.COM_setup()




    def updateNumber(self, state):
        if state == Qt.Checked:
            from randomer import RNG
            #print(self.serial.readLine())
            val = float(self.data)
            #print(type(val))
            self.V1.display(val)
        else:
            self.V1.display(0)

    def updateNumber1(self, state):
        if state == Qt.Checked:
            from randomer import RNG
            #print(self.serial.readLine())
            val = float(self.data)
            #print(type(val))
            self.V2.display(-val)
        else:
            self.V2.display(0)

    def COM_setup(self):
        self.serial = QSerialPort()
        self.serial.setBaudRate(QSerialPort.Baud9600)
        portList = []
        ports = QSerialPortInfo().availablePorts()
        for port in ports:
            portList.append(port.portName())
        #print(portList)
        port = portList[1]
        #print(port)
        #self.comL.addItems(portList)
        self.serial.setPortName(port)
        self.serial.setDataTerminalReady(True)
        self.serial.open(QIODevice.ReadWrite)
        #self.serial.write(b'1')
        self.serial.readyRead.connect(self.onRead)




    def onRead(self):
        self.data = str(self.serial.readAll(), 'utf-8').strip()
        #print(data)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()