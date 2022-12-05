from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore import QIODevice

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('interface.ui', self)
        self.connections()
        self.show()

    def connections(self):
        self.V1_b.stateChanged.connect(self.updateNumber)
        self.Arduino()




    def updateNumber(self, state):
        if state == Qt.Checked:
            from randomer import RNG
            print(self.serial.readLine())
            self.V1.display(self.serial.readLine())

        else:
            self.V1.display(0)

    def Arduino(self):
        self.serial = QSerialPort()
        self.serial.setBaudRate(9600)
        portList = []
        ports = QSerialPortInfo().availablePorts()
        for port in ports:
            portList.append(port.portName())
        #print(portList)
        port = portList[1]
        print(port)
        #self.comL.addItems(portList)
        self.serial.setPortName(port)
        self.serial.open(QIODevice.ReadWrite)
        #self.serial.write(b'551565')
        self.serial.readyRead.connect(self.onRead)




    def onRead(self):
        print(self.serial.readLine())


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()