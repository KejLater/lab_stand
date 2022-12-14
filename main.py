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
        self.MC = SerialPort()    #Creating SerialPort object to connect MicroController
        self.update_portList(self.MC.ports)

        self.updatePorts.clicked.connect(self.update_portList)
        self.connect_MC.clicked.connect(self.MC.openChosenPort)
        self.connect_MC.clicked.connect(self.show_MC_connected)     #After successful connection change light and unlock LCDs




    def data_converter(self):
        array = self.MC.data.split('@')
        return {"V1":float(array[0]), "V2":float(array[1])}

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


    def update_portList(self, array):
        self.portList.addItems(self.MC.ports)

    def updateAll(self):
        
        if self.V1_checkbox.isChecked():
            val = self.data_converter()["V1"]
            self.V1.display(val)
            #print('But now I am working')
        else:
            self.V1.display(0)


        if self.V2_checkbox.isChecked():
            val = self.data_converter()['V2']
            self.V2.display(val)
        else:
            self.V2.display(0)


        if self.V3_checkbox.isChecked():
            val = self.data_converter()
            self.V3.display(val)
        else:
            self.V3.display(0)


        if self.V4_checkbox.isChecked():
            val = self.data_converter()
            self.V4.display(val)
        else:
            self.V4.display(0)


        if self.A1_checkbox.isChecked():
            val = self.data_converter()
            self.A1.display(val)
        else:
            self.A1.display(0)


        if self.A2_checkbox.isChecked():
            val = self.data_converter()
            self.A2.display(val)
        else:
            self.A2.display(0)


        if self.A3_checkbox.isChecked():
            val = self.data_converter()
            self.A3.display(val)
        else:
            self.A3.display(0)


        if self.A4_checkbox.isChecked():
            val = self.data_converter()
            self.A4.display(-val)
        else:
            self.A4.display(0)

class SerialPort:
    def __init__(self):
        self.COM_setup()
        self.connected = False
        self.data = 0

    def COM_setup(self):
        self.serial = QSerialPort()   #Creating object of class QSerialPort
        self.serial.setBaudRate(QSerialPort.Baud9600)
        self.ports = [port.portName() for port in QSerialPortInfo().availablePorts()]
        #print(self.ports)
        del self.ports[0]
        #self.ports.append('COM5')



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
        #window.V1.display(float(self.data))
        #print('onRead is working')


class MyThread(QThread):
    mySignal = pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.value = 0

    def run(self):
        while True:
            print(window.MC.data)
            self.mySignal.emit(self.value)
            QThread.msleep(100)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    app.exec_()