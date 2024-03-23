import sys, os
from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QIODevice
#from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo

from randomer import Data
from port_interaction import SerialPort

class MainWindow(QtWidgets.QMainWindow, Data, SerialPort):

    def __init__(self):  # pyinstaller.exe --onefile --add-data="interface.ui;." --noconsole main.py
        super().__init__()

        try:
            UIFile = os.path.join(sys._MEIPASS, 'interface.ui')  # packages to exe
        except AttributeError:
            UIFile = 'interface.ui'  # executes it if launnched in python

        uic.loadUi(UIFile, self)  # loads UI from .ui
        SerialPort.__init__(self)  # inherites SerialPort class
        Data.__init__(self)

        self.hotkeys()  # init hotkeys
        self.initializations()  # init fnctions

        self.init_io()

        self.show()


    def hotkeys(self):    # ties hotkeys to functions
        self.add_data_to_df_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+D"), self)
        self.add_data_to_df_shortcut.activated.connect(self.add_data_to_df)  # adds shortcut

        self.graph_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+G"), self)
        self.graph_shortcut.activated.connect(self.build_graph)  # adds shortcut

        self.serialSend_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Return"), self)  # adds shortcut
        self.serialSend_shortcut.activated.connect(lambda: self.send_to_port(self.input_voltage.text()))

        self.serialSend_shortcut1 = QtWidgets.QShortcut(QtGui.QKeySequence(Qt.EnterKeyGo ), self)  # adds shortcut
        self.serialSend_shortcut1.activated.connect(lambda: self.send_to_port(self.input_voltage.text()))


    def initializations(self):
        self.meters = [self.V1, self.V2, self.V3, self.V4,
                       self.A1, self.A2, self.A3, self.A4]  # list of volt- and ampermeters

        self.checkboxes = [self.V1_checkbox, self.V2_checkbox,
                           self.V3_checkbox, self.V4_checkbox,
                           self.A1_checkbox, self.A2_checkbox,
                           self.A3_checkbox, self.A4_checkbox]  # checkboxes to siwtch meter off or on

        self.choose_X_list.addItems(self.meterNames)  # adds V1, V2... A4 to list where user chooses X for graph

        self.update_choose_delete_list()

        self.thread = MyThread()  # starts Thread to read data
        self.thread.mySignal.connect(self.update_meters)
        self.thread.start()


        # buttons
        self.export_csv_button.clicked.connect(self.export_csv)  # csv export
        self.reset_df_and_table_button.clicked.connect(self.reset_df_and_table)  # clears table
        self.remove_last_from_df_button.clicked.connect(self.remove_last_from_df)  # removes the last result
        self.add_data_to_df_button.clicked.connect(self.add_data_to_df)  # Adding numbers to the tabl
        self.build_graph_button.clicked.connect(self.build_graph)  # Build build_graph
        self.sort_df_by_column_button.clicked.connect(lambda: self.sort_df_by_column(self.choose_X_list.currentText()))

        self.update_choose_port_list_button.clicked.connect(self.update_choose_port_list)  # updates list of ports
        self.open_selected_port_button.clicked.connect(lambda: self.open_selected_port(self.choose_port_list.currentText()))  # opens port
        self.close_port_button.clicked.connect(self.close_port)  # closes port

        self.set_voltage_button.clicked.connect(lambda: self.send_to_port(self.input_voltage.text()))  # sends data to port

        self.delete_by_N_button.clicked.connect(lambda: self.delete_by_N(self.choose_delete_list.currentText()))

    def init_io(self):  # inits lists to choose status of port and ties btn to func #TODO

        self.iosA = [self.io_0_list, self.io_1_list, self.io_2_list, self.io_3_list, self.io_4_list,
                    self.io_5_list, self.io_6_list, self.io_7_list]

        self.iosB = [self.io_8_list, self.io_9_list, self.io_10_list, self.io_11_list, self.io_12_list,
                     self.io_13_list, self.io_14_list, self.io_15_list]

        self.iosC = [self.io_16_list, self.io_17_list, self.io_18_list, self.io_19_list, self.io_20_list,
                     self.io_21_list, self.io_22_list, self.io_23_list]

        self.ios = self.iosA + self.iosB + self.iosC

        for io in self.ios:
            #io.addItems(('0', '1', 'R'))
            #io.addItems(('0', '1', 'R'))
            io.addItems(('R', '1', '0'))

        self.set_io_button.clicked.connect(self.set_io)


    def set_io(self):  # TODO

        import crccheck
        import struct

        packet_len = 43

        magic = 0xe621

        adc = 0

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

        package = bytearray(
            [(magic >> 8 & 0xFF), (magic & 0xFF), portAconf, portBconf, portCconf, portAdata, portBdata,
             portCdata, (adc >> 8 & 0xFF), (adc & 0xFF), debug0, debug1, debug2, debug3])

        crc = crc_calc.calc(package)

        mail = struct.pack(formS, magic, portAconf, portBconf, portCconf, portAdata, portBdata,
                           portCdata, adc, debug0, debug1, debug2, debug3, crc)

        self.serial.write(mail)


    def convert_data_from_port(self):
        
        if self.data.count("@") == 7:  # checks if seven @ are in string
            array = self.data.split('@')  # splits string
            return [float(n) for n in array]  # turns elements of list from str to float

        else:
            return [0 for _ in range(8)]  # if @ are not in list returns list of 0


    def show_port_closed(self):  # changes UI if port closed
        self.connect_label.setText('не подключено')
        self.connect_label.setStyleSheet("background-color: red")


    def show_port_error(self):  # changes UI if something went wrong
        self.connect_label.setText('ошибка')
        self.connect_label.setStyleSheet("background-color: red")


    def show_port_opened(self):  # changes UI if port opened
        self.connect_label.setText('подключено')
        self.connect_label.setStyleSheet("background-color: lightgreen")


    def update_meters(self):  # updates meter if switched
        values = self.convert_data_from_port()
        for i in range(8):
            if self.checkboxes[i].isChecked():
                self.meters[i].display(values[i])

            else:
                self.meters[i].display(0)


class MyThread(QThread):
    mySignal = pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        super().__init__()

    def run(self):
        while True:
            self.mySignal.emit(0)
            QThread.msleep(10)




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    app.exec_()