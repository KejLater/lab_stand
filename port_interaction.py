from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore import QIODevice
class SerialPort:  # class for interaction with port

    def __init__(self):

        self.serial = QSerialPort()  # creates object of class to deal with connections
        self.update_choose_port_list()    # updates list of available ports
        self.data = '0@0@0@0@0@0@0@0'    # data for initialisation


    def update_choose_port_list(self):  # updates list of available ports
        self.choose_port_list.clear()  # clears widget
        self.choose_port_list.addItems([port.portName() for port in QSerialPortInfo().availablePorts()])  # adds ports
                                                                                                  # to widget


    def open_selected_port(self, selected_port):  # opens port chosen in widget

        if self.serial.isOpen():  # closes port if it was previously opened
            self.serial.close()

        if selected_port in [port.portName() for port in QSerialPortInfo().availablePorts()]:  # checks if port lost

            self.serial.setBaudRate(QSerialPort.Baud9600)  # sets BaudRate
            self.serial.setPortName(selected_port)  # selects port
            self.serial.setDataTerminalReady(True)  # prepares port
            self.serial.open(QIODevice.ReadWrite)  # opens port for interaction

        else:  # updates port list if chosen port lost
            self.update_choose_port_list()

        if self.serial.isOpen():  # makes fuction read data from port and changes UI if successful
            self.serial.readyRead.connect(self.read_port)
            self.show_port_opened()

        else:  # makes UI show error if problems occured
            self.show_port_error()


    def read_port(self):  # reads data from port
        if self.serial.canReadLine():  # checks if data is readable
            self.data = str(self.serial.readLine(), 'utf-8').strip()    # turns bytes to str withuot '\n'


    def close_port(self):  # closes port

        if self.serial.isOpen():  # checks if port is opened
            self.serial.close()  # closes port

        if not self.serial.isOpen():  # makes changes to UI if port is closed
            self.show_port_closed()

        else:  # makes UI show error if port is still opened
            self.show_port_error()

    def send_to_port(self, data):  # sends data to port

        import struct

        if self.serial.isOpen():

            data = data.replace(',', '')  # replaces , with ''
            data = int(data) * 10
            self.serial.write(struct.pack("<H", data))  # sending data to port as two bytes

