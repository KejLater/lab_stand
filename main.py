import sys, os
from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QIODevice
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
import pandas as pd


class Data:    # class for interaction with DataFrame (DF) and tableWidget (table) where data is stored
               # visible tableWidget (table) is just derivative of DF
               # instead of adding new data to table I clear it and fill again by function update_tableWidget()

    def __init__(self):
        self.sortingOrder = True  # reverses sorting order
        self.meterNames = ['V1', 'V2', 'V3', 'V4', 'A1', 'A2', 'A3', 'A4']  # names for columns
        self.DF = pd.DataFrame(columns=self.meterNames)  # creates DF to save results


    def sort_df_by_column(self, name):  # sorts data in DF

        if self.DF.size:  # checks if DF is not empty

            self.DF = self.DF.sort_values(by=name, ignore_index=True, ascending=self.sortingOrder)
            self.sortingOrder = not (self.sortingOrder)  # reverses sorting order during next call
            self.update_tableWidget()  # clears table and fills it with updated DF


    def export_df_to_csv(self):  # exports DF to csv

        dir = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', filter='*.csv')[0]  # calls dialogue window
        if dir:  # checks if user did not cancel export
            self.DF.to_csv(dir, index=False, decimal=',', sep=';')


    def reset_df_and_table(self):  # clears both table and DF

        button = QtWidgets.QMessageBox.question(self, "Подтверждение", "Really?")  # confirmation from user

        if button == QtWidgets.QMessageBox.Yes:  # if user confirmed

            self.DF = pd.DataFrame(columns=self.meterNames)  # creates new DF
            self.update_tableWidget()  # clears table and fills it with updated DF


    def remove_last_from_df(self):  # dropes the last row from both dataframe and table

        if self.DF.size:  # checks if table is not empty

            self.DF = self.DF.drop(labels=[len(self.DF) - 1], axis=0)
            self.update_tableWidget()  # clears table and fills it with updated DF


    def add_data_to_df(self):  # adds line of values to the end of DF

        self.DF.loc[len(self.DF)] = [meter.value() for meter in self.meters]  # adds data from meters to DF
        self.update_tableWidget()  # clears table and fills it with updated DF


    def update_tableWidget(self):  # clears table and fills it with updated DF

        self.tableWidget.clearContents()  # clears table completly but not DF
        self.tableWidget.setRowCount(0)  # makes rowCount (horizontal dimension) equal to zero

        for i, row in self.DF.iterrows():  # iterates the whole DF

            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)  # adds new row to table

            for j in range(self.tableWidget.columnCount()):  # iterates table

                self.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(row[j])))  # sets item [i, j]


    def build_graph(self):

        Vs = [self.V1_y, self.V2_y, self.V3_y, self.V4_y]
        Is = [self.A1_y, self.A2_y, self.A3_y, self.A4_y]
        CBxs = Vs + Is

        colors = ['#FF7F50', '#A52A2A', '#458B00', '#20B2AA', '#1E90FF', '#800080', '#FF3E96', '#7F7F7F']
        names = ' '
        n = 0
        if self.DF.size and any([box.isChecked() for box in CBxs]):

            from matplotlib import pyplot as plt
            plt.axhline(y=0, color='black', linewidth=0.5)
            x = self.DF[self.choose_X.currentText()]
            if 'V' in self.choose_X.currentText():
                plt.xlabel(f'{self.choose_X.currentText()}, В')
            elif "A" in self.choose_X.currentText():
                plt.xlabel(f'{self.choose_X.currentText()}, мА')
            if any([box.isChecked() for box in Vs]):
                for box in Vs:
                    if box.isChecked():
                        y = self.DF[box.objectName()[0:-2]]
                        plt.plot(x, y, color=colors[n], label=box.objectName()[0:-2], marker='o', markersize=4)
                        names = names + f'{box.objectName()[0:-2]}, '
                        n = n + 1
                plt.ylabel(f"{names} В")
            else:
                for box in Is:
                    if box.isChecked():
                        y = self.DF[box.objectName()[0:-2]]
                        plt.plot(x, y, color=colors[n], label=box.objectName()[0:-2], marker='o', markersize=4)
                        names = names + f'{box.objectName()[0:-2]}, '
                        n = n + 1
                plt.ylabel(f"{names} мА")
            plt.legend()
            plt.grid()
            plt.show()



class SerialPort:

    def __init__(self):

        self.serial = QSerialPort()
        self.update_ports()    # when proram opens, list of ports gets added to menu
        self.data = '0@0@0@0@0@0@0@0'    # data for initialisation


    def update_ports(self):
        self.portList.clear()
        self.portList.addItems([port.portName() for port in QSerialPortInfo().availablePorts()])


    def open_selected_port(self, selected_port):
        if self.serial.isOpen():
            self.serial.close()

        if selected_port in [port.portName() for port in QSerialPortInfo().availablePorts()]:
            self.serial = QSerialPort()
            self.serial.setBaudRate(QSerialPort.Baud9600)
            self.serial.setPortName(selected_port)
            self.serial.setDataTerminalReady(True)
            self.serial.open(QIODevice.ReadWrite)  # opens port for interaction

        else:
            self.update_ports()

        if self.serial.isOpen():
            self.serial.readyRead.connect(self.read_port)
            self.show_port_opened()

        else:
            self.show_port_error()


    def read_port(self):
        if self.serial.canReadLine():
            self.data = str(self.serial.readLine(), 'utf-8').strip()    # turns bytes to str withuot '\n'


    def close_port(self):

        if self.serial.isOpen():
            self.serial.close()

        if not self.serial.isOpen():
            self.show_port_closed()

        else:
            self.show_port_error()



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