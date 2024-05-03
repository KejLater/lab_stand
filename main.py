import sys, os
from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QIODevice
import qdarktheme
# from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo

from randomer import Data
from port_interaction import SerialPort


class MainWindow(QtWidgets.QMainWindow, Data, SerialPort):

    def __init__(self):  # pyinstaller.exe --onefile --add-data="interface.ui;." --icon=icon.svg --noconsole main.py
        super().__init__()
        qdarktheme.setup_theme()  # makes app dark
        try:
            UIFile = os.path.join(sys._MEIPASS, 'interface.ui')  # packages to exe
        except AttributeError:
            UIFile = 'interface.ui'  # executes it if launched in python

        #self.setWindowIcon(QtGui.QIcon('icon.ico'))

        uic.loadUi(UIFile, self)  # loads UI from .ui
        SerialPort.__init__(self)  # inherites SerialPort class
        Data.__init__(self)  # inherites Data class

        self.hotkeys()  # init hotkeys
        self.initializations()  # init fnctions
        self.buttons()  # init buttons
        self.init_io()  # init 24 lists of ports and reset

        self.show()

    def hotkeys(self):  # ties hotkeys to functions

        self.add_data_to_df_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+A"), self)
        self.add_data_to_df_shortcut.activated.connect(self.add_data_to_df)  # adds shortcut

        self.graph_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+G"), self)
        self.graph_shortcut.activated.connect(self.build_graph)  # adds shortcut

        self.serialSend_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Return"), self)  # adds shortcut
        self.serialSend_shortcut.activated.connect(lambda: self.send_to_port(self.input_voltage.text()))

    def initializations(self):

        self.meters = [self.V1, self.V2, self.V3, self.V4,
                       self.A1, self.A2, self.A3, self.A4]  # list of volt- and ampermeters

        self.checkboxes = [self.V1_checkbox, self.V2_checkbox,
                           self.V3_checkbox, self.V4_checkbox,
                           self.A1_checkbox, self.A2_checkbox,
                           self.A3_checkbox, self.A4_checkbox]  # checkboxes to siwtch meter off or on

        self.choose_X_list.addItems(self.meterNames)  # adds V1, V2... A4 to list where user chooses X for graph

        self.sort_data_list.addItems(self.meterNames)  # adds meterNames to sorting list

        self.update_choose_delete_list()  # updates list of N to delete, not mandatory here

        self.thread = MyThread()  # starts Thread to read data
        self.thread.mySignal.connect(self.update_meters)
        self.thread.start()


    def buttons(self):  # init buttons

        self.export_csv_button.clicked.connect(self.export_csv)  # csv export
        self.reset_df_and_table_button.clicked.connect(self.reset_df_and_table)  # clears table
        self.remove_last_from_df_button.clicked.connect(self.remove_last_from_df)  # removes the last result
        self.add_data_to_df_button.clicked.connect(self.add_data_to_df)  # adding numbers to the tabl
        self.build_graph_button.clicked.connect(self.build_graph)  # build build_graph
        self.sort_df_by_column_button.clicked.connect(
            lambda: self.sort_df_by_column( [
                self.sort_data_list.item(x).text() for x in range(self.sort_data_list.count())] ))  # sort values in table

        self.update_choose_port_list_button.clicked.connect(self.update_choose_port_list)  # updates list of ports
        self.open_selected_port_button.clicked.connect(
            lambda: self.open_selected_port(self.choose_port_list.currentText()))  # opens port
        self.close_port_button.clicked.connect(self.close_port)  # closes port

        self.set_voltage_button.clicked.connect(
            lambda: self.send_to_port(self.input_voltage.text()))  # sends pins and voltage to port

        self.delete_by_N_button.clicked.connect(
            lambda: self.delete_by_N(self.choose_delete_list.currentText()))  # delete N button

        self.reset_io_button.clicked.connect(
            lambda: self.init_io(self.io_reset_list.currentText()))  # reset lists of pins, NOT values

    def init_io(self, letter='R'):  # inits lists to choose status of port and ties btn to func

        self.ios_lcd = [self.lcd_io_0, self.lcd_io_1, self.lcd_io_2, self.lcd_io_3, self.lcd_io_4,
                     self.lcd_io_5, self.lcd_io_6, self.lcd_io_7, self.lcd_io_8, self.lcd_io_9,
                     self.lcd_io_10, self.lcd_io_11, self.lcd_io_12, self.lcd_io_13, self.lcd_io_14,
                     self.lcd_io_15, self.lcd_io_16, self.lcd_io_17, self.lcd_io_18, self.lcd_io_19,
                     self.lcd_io_20, self.lcd_io_21, self.lcd_io_22, self.lcd_io_23]  # LCDs of pins

        self.iosA = [self.io_0_list, self.io_1_list, self.io_2_list, self.io_3_list, self.io_4_list,
                     self.io_5_list, self.io_6_list, self.io_7_list]  # first 8 pins lists

        self.iosB = [self.io_8_list, self.io_9_list, self.io_10_list, self.io_11_list, self.io_12_list,
                     self.io_13_list, self.io_14_list, self.io_15_list]  # second 8 pins lists

        self.iosC = [self.io_16_list, self.io_17_list, self.io_18_list, self.io_19_list, self.io_20_list,
                     self.io_21_list, self.io_22_list, self.io_23_list]  # third 8 pins lists

        self.ios = self.iosA + self.iosB + self.iosC

        self.io_reset_list.clear()  # reset "reset" list

        if letter == 'R':  # adds chosen letter first after reset of pins
            self.io_reset_list.addItems(('R', '1', '0'))

        elif letter == '0':
            self.io_reset_list.addItems(('0', 'R', '1'))

        elif letter == '1':
            self.io_reset_list.addItems(('1', 'R', '0'))

        if letter == 'R':  # makes chosen letter first after reset
            for io in self.ios:
                io.clear()
                io.addItems(('R', '1', '0'))

        elif letter == '0':
            for io in self.ios:
                io.clear()
                io.addItems(('0', 'R', '1'))

        elif letter == '1':
            for io in self.ios:
                io.clear()
                io.addItems(('1', 'R', '0'))

    def convert_data_from_port(self):  # converting data received from port_interaction into list
        return list(self.data)

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

        for i in range(8):  # checks if checkox is checked and displays corresponding LCD value
            if self.checkboxes[i].isChecked():
                self.meters[i].display(values[i + 1])

            else:  # if checkbox is not checked displays 0
                self.meters[i].display(0)

        port = [int(values[9]), int(values[10]), int(values[11])]
        # print(port)
        mask = [int(0b10000000), int(0b01000000), int(0b00100000), int(0b00010000),
                int(0b00001000), int(0b00000100), int(0b00000010), int(0b00000001)]
        for i in range(3):
            for j in range(8):

                self.ios_lcd[i*8+j].display(bool((port[i] & mask[j])))  # displays pin value if R is set

class MyThread(QThread):  # permanently updates meters
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
