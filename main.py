import sys, os
from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QIODevice
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo

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

        self.hotkeys()  # init hotkeys
        self.initializations()  # init fnctions
        self.show()


    def hotkeys(self):    # ties hotkeys to functions
        self.addData_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+D"), self)
        self.addData_shortcut.activated.connect(self.add_data_to_df)  # adds shortcut

        self.graph_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+G"), self)
        self.graph_shortcut.activated.connect(self.build_graph)  # adds shortcut

        #self.serialSend_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Enter"), self)  # adds shortcut
        #self.serialSend_shortcut.activated.connect(lambda: self.send_to_port(self.inputVoltage.text()))

        self.serialSend_shortcut1 = QtWidgets.QShortcut(QtGui.QKeySequence(Qt.EnterKeyGo ), self)  # adds shortcut
        self.serialSend_shortcut1.activated.connect(lambda: self.send_to_port(self.inputVoltage.text()))


    def initializations(self):
        self.meters = [self.V1, self.V2, self.V3, self.V4,
                       self.A1, self.A2, self.A3, self.A4]  # list of volt- and ampermeters

        self.checkboxes = [self.V1_checkbox, self.V2_checkbox,
                           self.V3_checkbox, self.V4_checkbox,
                           self.A1_checkbox, self.A2_checkbox,
                           self.A3_checkbox, self.A4_checkbox]  # checkboxes to siwtch meter off or on

        self.choose_X.addItems(self.meterNames)  # adds V1, V2... A4 to list where user chooses X for graph

        self.update_N()

        self.thread = MyThread()  # starts Thread to read data
        self.thread.mySignal.connect(self.update_meters)
        self.thread.start()


        # buttons
        self.export_csv_button.clicked.connect(self.export_df_to_csv)  # csv export
        self.reset_button.clicked.connect(self.reset_df_and_table)  # clears table
        self.remove_last_button.clicked.connect(self.remove_last_from_df)  # removes the last result
        self.add_values_button.clicked.connect(self.add_data_to_df)  # Adding numbers to the tabl
        self.graph_button.clicked.connect(self.build_graph)  # Build build_graph
        self.sort_launch_button.clicked.connect(lambda: self.sort_df_by_column(self.choose_X.currentText()))

        self.update_ports_button.clicked.connect(self.update_ports)  # updates list of ports
        self.connect_mc_button.clicked.connect(lambda: self.open_selected_port(self.portList.currentText()))  # opens port
        self.close_port_button.clicked.connect(self.close_port)  # closes port

        self.set_voltage_button.clicked.connect(lambda: self.send_to_port(self.inputVoltage.text()))  # sends data to port

        self.delete_n_button.clicked.connect(lambda: self.remove_by_N(self.choose_delete.currentText()))



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