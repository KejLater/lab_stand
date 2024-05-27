"""This module is responsible for working with Serial Port and collecting and sending data to port"""

from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore import QIODevice


class SerialPort:  # class for interaction with port

    def __init__(self):

        self.serial = QSerialPort()  # creates object of class to deal with connections
        self.update_choose_port_list()  # updates list of available ports
        self.data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]  # data for initialisation

    def update_choose_port_list(self):  # updates list of available ports
        self.choose_port_list.clear()  # clears widget
        self.choose_port_list.addItems([port.portName() for port in QSerialPortInfo().availablePorts()])  # adds ports to widget

    def open_selected_port(self, selected_port):  # opens port chosen in widget

        if self.serial.isOpen():  # closes port if it was previously opened
            self.serial.close()


        if selected_port in [port.portName() for port in QSerialPortInfo().availablePorts()]:  # checks if port lost

            self.serial.setBaudRate(12000000)  # sets mbps
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

        import time
        import os
        import crccheck
        from typing import Tuple, List
        import struct

        formR = "<H8f7BH"
        packet_len = 43

        # checks if data is readable
        buff_size = 43
        buff = self.serial.read(buff_size)
        header_pos = buff.find(b'\x27\xff')
        while header_pos < 0:
            buff = self.serial.read(buff_size)
            header_pos = buff.find(b'\x27\xff')
        skipped = header_pos
        packet_bin = buff[header_pos:]
        packet_bin += self.serial.read((packet_len - len(buff[header_pos:])))
        a = struct.unpack(formR, packet_bin)
        crc_in = a[-1]
        crc_calc = crccheck.crc.Crc(width=16, poly=0x8005, initvalue=0x0000, reflect_input=True,
                                    reflect_output=True,
                                    xor_output=0x0000)
        crc_out = crc_calc.calc(packet_bin[:-2])

        # print(packet_bin[:-2].hex())
        # print(hex(crc_in))
        # print(hex(crc_out))
        # print(struct.unpack("<H", packet_bin[:2]))
        if crc_in != crc_out:
            print(a)
            print("BAD CRC")
            print()
        else:
            print(a)
            print()

        self.data = a  # turns bytes to str withuot '\n'

    def close_port(self):  # closes port

        if self.serial.isOpen():  # checks if port is opened
            self.serial.close()  # closes port

        if not self.serial.isOpen():  # makes changes to UI if port is closed
            self.show_port_closed()

        else:  # makes UI show error if port is still opened
            self.show_port_error()

    def send_to_port(self, data):  # sends data to port

        import struct
        import crccheck

        packet_len = 43
        magic = 0xe621  # shows beginning of sequence
        portAconf: int = 0  # pins 0-7 R/W
        portBconf: int = 0  # pins 8-15 R/W
        portCconf: int = 0  # pins 16-23 R/W
        portAdata: int = 0  # pins 0-7 0/1 if W
        portBdata: int = 0  # pins 8-15 0/1 if W
        portCdata: int = 0  # pins 16-23 0/1 if W
        debug0: int = 7
        debug1: int = 8
        debug2: int = 9
        debug3: int = 10
        formS = "<H6BH4BH"

        if self.serial.isOpen():
        #if True:  # is needed to test if no STM is connected

            data = data.replace(',', '')  # replaces , with ''
            data = data.replace('.', '')  # replaces . with ''
            data = int(data) * 10

            for i in range(8):  # iterates ports 0-7

                if self.iosA[i].currentText() == '0':  # if pin status is 0, writes 1 to portAconf byte (2^i in dec)
                    portAconf = portAconf + 2 ** i

                elif self.iosA[i].currentText() == '1':  # if pin status is 1, writes 1 to portAconf byte and 1 to portAdata (2^i in dec)
                    portAconf = portAconf + 2 ** i
                    portAdata = portAdata + 2 ** i


            for i in range(8):  # iterates ports 8-15

                if self.iosB[i].currentText() == '0':  # if pin status is 0, writes 1 to portAconf byte (2^i in dec)
                    portBconf = portBconf + 2 ** i

                elif self.iosB[i].currentText() == '1':  # if pin status is 1, writes 1 to portAconf byte and 1 to portAdata (2^i in dec)
                    portBconf = portBconf + 2 ** i
                    portBdata = portBdata + 2 ** i


            for i in range(8):  # iterates ports 16-23

                if self.iosC[i].currentText() == '0':  # if pin status is 0, writes 1 to portAconf byte (2^i in dec)
                    portCconf = portCconf + 2 ** i

                elif self.iosC[i].currentText() == '1':  # if pin status is 1, writes 1 to portAconf byte and 1 to portAdata (2^i in dec)
                    portCconf = portCconf + 2 ** i
                    portCdata = portCdata + 2 ** i

            print(bin(portAconf), bin(portBconf), bin(portCconf))
            print(bin(portAdata), bin(portBdata), bin(portCdata))

            crc_calc = crccheck.crc.Crc(width=16, poly=0x8005, initvalue=0x0000, reflect_input=True,
                                        reflect_output=True,
                                        xor_output=0x0000)  # calculates crc
            package = bytearray(
                [(magic >> 8 & 0xFF), (magic & 0xFF), portAconf, portBconf, portCconf, portAdata, portBdata,
                 portCdata, (data >> 8 & 0xFF), (data & 0xFF), debug0, debug1, debug2, debug3])  # packs to bytes

            crc = crc_calc.calc(package)  # adds crc

            mail = struct.pack(formS, magic, portAconf, portBconf, portCconf, portAdata, portBdata,
                               portCdata, data, debug0, debug1, debug2, debug3, crc)  # forms message

            self.serial.write(mail)  # sends message
