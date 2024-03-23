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
        self.buttons()  #  init buttons
        self.init_io()  #  inits 24 lists of ports and reset

        self.show()


    def hotkeys(self):    # ties hotkeys to functions
        self.add_data_to_df_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+D"), self)
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

        self.update_choose_delete_list()

        self.thread = MyThread()  # starts Thread to read data
        self.thread.mySignal.connect(self.update_meters)
        self.thread.start()


    def buttons(self):  #  inits buttons

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

        self.reset_io_button.clicked.connect(lambda: self.init_io(self.io_reset_list.currentText()))  # reset of pins list, NOT values

    def init_io(self, letter='R'):  # inits lists to choose status of port and ties btn to func 

        self.iosA = [self.io_0_list, self.io_1_list, self.io_2_list, self.io_3_list, self.io_4_list,
                    self.io_5_list, self.io_6_list, self.io_7_list]

        self.iosB = [self.io_8_list, self.io_9_list, self.io_10_list, self.io_11_list, self.io_12_list,
                     self.io_13_list, self.io_14_list, self.io_15_list]

        self.iosC = [self.io_16_list, self.io_17_list, self.io_18_list, self.io_19_list, self.io_20_list,
                     self.io_21_list, self.io_22_list, self.io_23_list]

        self.ios = self.iosA + self.iosB + self.iosC

        self.io_reset_list.clear()
        self.io_reset_list.addItems(('R', '1', '0'))

        if letter == 'R':
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