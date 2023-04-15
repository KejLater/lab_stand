import sys, os
from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QIODevice
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo

from randomer import Data
from port_interaction import SerialPort

class MainWindow(QtWidgets.QMainWindow, Data, SerialPort):

    def __init__(self):
        super().__init__()

        try:
            UIFile = os.path.join(sys._MEIPASS, 'interface.ui') #It is for EXE packaging
        except:
            UIFile = 'interface.ui' #It is for pure Python

        uic.loadUi(UIFile, self)
        SerialPort.__init__(self)

        self.hotkeys() #Init hotkeys
        self.initializations()    #just not to change __init__ anymore
        self.show()


    def hotkeys(self):    # ties hotkeys to functions
        self.addData_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+D"), self)
        self.addData_shortcut.activated.connect(self.add_data_to_df)

        self.graph_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+G"), self)
        self.graph_shortcut.activated.connect(self.build_graph)

        self.serialSend_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Enter"), self)
        self.serialSend_shortcut.activated.connect(lambda: self.send_to_port(self.inputVoltage.text()))


    def initializations(self):
        self.meters = [self.V1, self.V2, self.V3, self.V4,
                       self.A1, self.A2, self.A3, self.A4]    #list of volt- and ampermeters

        self.checkboxes = [self.V1_checkbox, self.V2_checkbox,
                           self.V3_checkbox, self.V4_checkbox,
                           self.A1_checkbox, self.A2_checkbox,
                           self.A3_checkbox, self.A4_checkbox]    # checkboxes to siwtch meter off or on

        self.choose_X.addItems(self.meterNames)    # adds V1, V2... A4 to list where user chooses X for graph
        self.choose_sort.addItems(self.meterNames)

        self.thread = MyThread()
        self.thread.mySignal.connect(self.update_meters)
        self.thread.start()

        self.exportCSV.clicked.connect(self.export_df_to_csv)  # csv export
        self.reset.clicked.connect(self.reset_df_and_table)  # clears table
        self.remove_last.clicked.connect(self.remove_last_from_df)  # removes the last result
        self.add_values.clicked.connect(self.add_data_to_df)  # Adding numbers to the tabl
        self.graph_button.clicked.connect(self.build_graph)  # Build build_graph
        self.sort_launch.clicked.connect(lambda: self.sort_df_by_column(self.choose_sort.currentText()))

        self.updatePorts.clicked.connect(self.update_ports) #update list of ports
        self.connect_MC.clicked.connect(lambda: self.open_selected_port(self.portList.currentText()))
        self.close_btn.clicked.connect(self.close_port)

        self.setVoltage.clicked.connect(lambda: self.send_to_port(self.inputVoltage.text()))
        self.auto_launch.clicked.connect(
            lambda: self.auto_vac(self.auto_begin.text(), self.auto_end.text(), self.auto_step.text()))


    def auto_vac(self, begin, end, step):
        from numpy import linspace
        #import time
        #permittedSymbols = "0123456789. "
        #begin = begin.replace(' ', '')
        #begin = begin.replace(' ', '')
        #begin = begin.replace(' ', '')

        #if end > begin and begin != '' and end != '' and n != '': pass
        voltages = linspace(float(begin), float(end), int(step))
        import time
        voltages = linspace(0, 10, 11)
        #voltages = linspace(float(begin), float(end), int(step))
        voltages = [round(v, 2) for v in voltages]

        for voltage in voltages:
            self.send_to_port(str(voltage))
            QThread.msleep(100)
            #time.sleep(1)
            self.update_meters()
            #print(self.data)
            self.add_data_to_df()
            print(self.data)


    def convert_data_from_port(self):
        if self.data.count("@") == 7:  # checks if seven @ are in string
            array = self.data.split('@')  # splits string
            return [float(n) for n in array]  # turns elements of list from str to rounded float

        else:
            return [0 for _ in range(8)]  # if @ are not in list returns list of 0


    def show_port_closed(self):
        self.connect_label.setText('не подключено')
        self.connect_label.setStyleSheet("background-color: red")


    def show_port_error(self):
        self.connect_label.setText('ошибка')
        self.connect_label.setStyleSheet("background-color: red")


    def show_port_opened(self):
        self.connect_label.setText('подключено')
        self.connect_label.setStyleSheet("background-color: lightgreen")


    def update_meters(self):
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