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

            self.serial.setBaudRate(QSerialPort.Baud115200)  # sets BaudRate
            self.serial.setPortName(selected_port)  # selects port
            self.serial.setDataTerminalReady(True)  # prepares port
            self.serial.open(QIODevice.ReadWrite)  # opens port for interaction

        else:  # updates port list if chosen port lost
            self.update_choose_port_list()

        if self.serial.isOpen():  # makes fuction read data from port and changes UI if successful

            #self.serial.readyRead.connect(self.read_port)
            self.show_port_opened()

        else:  # makes UI show error if problems occured
            self.show_port_error()


    def read_port(self):  # reads data from port

        import time
        import os
        import crccheck
        from typing import Tuple, List
        import struct

        formR = "<H8fH"
        packet_len = 36

        def skip_to_header(s) -> Tuple[bytes, int]:
            buff_size = 36
            buff = s.read(buff_size)
            header_pos = buff.find(b'\x27\xff')
            while header_pos < 0:
                buff = s.read(buff_size)
                header_pos = buff.find(b'\x27\xff')
            return buff[header_pos:], header_pos

        if self.serial.canReadLine():  # checks if data is readable

            #self.data = str(self.serial.readLine(), 'utf-8').strip()    # turns bytes to str withuot '\n'
            rem, skipped = skip_to_header(self.serial)
            packet_bin = rem
            packet_bin += s.read(packet_len - len(rem))
            a = struct.unpack(form, packet_bin)
            crc_in = a[-1]
            crc_calc = crccheck.crc.Crc(width=16, poly=0x8005, initvalue=0x0000, reflect_input=True,
                                        reflect_output=True, xor_output=0x0000)
            crc_out = crc_calc.calc(packet_bin[:-2])

            # print(packet_bin[:-2].hex())
            print(hex(crc_in))
            print(hex(crc_out))
            # print(struct.unpack("<H", packet_bin[:2]))
            if crc_in != crc_out:
                print(a)
                print("BAD CRC")
                print()
            else:
                print(a)
                print()


    def close_port(self):  # closes port

        if self.serial.isOpen():  # checks if port is opened
            self.serial.close()  # closes port

        if not self.serial.isOpen():  # makes changes to UI if port is closed
            self.show_port_closed()

        else:  # makes UI show error if port is still opened
            self.show_port_error()

    def send_to_port(self, data):  # sends data to port  #TODO

        import struct

        import crccheck

        packet_len = 43

        magic = 0xe621

        portAconf = 0
        portBconf = 0
        portCconf = 0

        portAdata = 0
        portBdata = 0
        portCdata = 0

        debug0 = 7
        debug1 = 8
        debug2 = 9
        debug3 = 10

        formS = "<H6BH4BH"

        #if self.serial.isOpen():
        if True:

            data = data.replace(',', '')  # replaces , with ''
            data = int(data) * 10
            data = struct.pack("<H", data)  # transform data into uint16

            data = 0xFF

            for i in range(8):
                if self.iosA[i].currentText() == '0':
                    portAconf = portAconf + 2 ** i

                elif self.iosA[i].currentText() == '1':
                    portAconf = portAconf + 2 ** i
                    portAdata = portAdata + 2 ** i

            for i in range(8):
                if self.iosB[i].currentText() == '0':
                    portBconf = portBconf + 2 ** i

                elif self.iosB[i].currentText() == '1':
                    portBconf = portBconf + 2 ** i
                    portBdata = portBdata + 2 ** i

            for i in range(8):
                if self.iosC[i].currentText() == '0':
                    portCconf = portCconf + 2 ** i

                elif self.iosC[i].currentText() == '1':
                    portCconf = portCconf + 2 ** i
                    portCdata = portCdata + 2 ** i

            print(bin(portAconf), bin(portBconf), bin(portCconf))
            print(bin(portAdata), bin(portBdata), bin(portCdata))

            crc_calc = crccheck.crc.Crc(width=16, poly=0x8005, initvalue=0x0000, reflect_input=True,
                                            reflect_output=True,
                                            xor_output=0x0000)
            print(2)
            package = bytearray(
                    [(magic >> 8 & 0xFF), (magic & 0xFF), portAconf, portBconf, portCconf, portAdata, portBdata,
                     portCdata, (data >> 8 & 0xFF), (data & 0xFF), debug0, debug1, debug2, debug3])
            print(1)
            crc = crc_calc.calc(package)

            mail = struct.pack(formS, magic, portAconf, portBconf, portCconf, portAdata, portBdata,
                                   portCdata, data, debug0, debug1, debug2, debug3, crc)

            #self.serial.write(mail)

