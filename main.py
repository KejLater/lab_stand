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
        self.V1_checkbox.stateChanged.connect(self.update_V1)
        self.V2_checkbox.stateChanged.connect(self.update_V2)   #test function
        self.COM_setup()




    def update_V1(self, state):
        if state == Qt.Checked:
            from randomer import RNG
            #print(self.serial.readLine())
            val = float(self.data)
            #print(type(val))
            self.V1.display(val)
        else:
            self.V1.display(0)

    def update_V2(self, state):    #test function
        if state == Qt.Checked:
            from randomer import RNG
            #print(self.serial.readLine())
            val = float(self.data)
            #print(type(val))
            self.V2.display(-val)
        else:
            self.V2.display(0)

    def COM_setup(self):
        self.serial = QSerialPort()   #Creating object of class QSerialPort
        self.serial.setBaudRate(QSerialPort.Baud9600)
        ports = [port.portName() for port in QSerialPortInfo().availablePorts()]
        #print(ports)
        port = ports[1]
        #print(port)
        #self.comL.addItems(portList)
        self.serial.setPortName(port)
        self.serial.setDataTerminalReady(True)
        self.serial.open(QIODevice.ReadWrite)
        #self.serial.write(b'1')
        self.serial.readyRead.connect(self.onRead)




    def onRead(self):
        self.data = str(self.serial.readAll(), 'utf-8').strip()    #Turning bytes to str withuot '\n'
        #print(data)


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