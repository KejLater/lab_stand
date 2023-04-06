import sys, os

from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QIODevice
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo

import pandas as pd


class Data:    # class for interaction with DataFrame (df) and tableWidget (table) where data is stored
                # visible tableWidget (table) is just derivative of df
                # instead of adding new data to table I clear it and fill again by function updateTable()

    def __init__(self):

        self.sorting_order = True    # reverses sorting order
        self.meter_names = ['V1', 'V2', 'V3', 'V4', 'A1', 'A2', 'A3', 'A4']    # names for columns
        self.df = pd.DataFrame(columns=self.meter_names)  # creates df to save results

    def sort_by(self, name):    # sorts data in df

        if self.tableWidget.rowCount():    # checks if table is not empty

            self.df = self.df.sort_values(by=name, ignore_index=True, ascending=self.sorting_order)
            self.sorting_order = not(self.sorting_order)    # reverses sorting order during next call
            self.updateTable()    #clears table and fills it with updated df


    def export_csv(self):    # exports df to csv

        dir = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', filter='*.csv')[0]    # calls dialogue window
        if dir:    # checks if user did not cancel export
            self.df.to_csv(dir, index=False)


    def resetTable(self):    # clears both table and df

        button = QtWidgets.QMessageBox.question(self, "Подтверждение", "Really?")    # confirmation from user

        if button == QtWidgets.QMessageBox.Yes:    # if user confirmed

            self.df = pd.DataFrame(columns=self.meter_names)    # creates new df
            self.updateTable()    # clears table and fills it with updated df

    def removeLast(self):    # dropes the last row from both dataframe and table

        if self.tableWidget.rowCount():    # checks if table is not empty

            self.df = self.df.drop(labels=[len(self.df)-1], axis=0)
            self.updateTable()    # clears table and fills it with updated df

    def addData(self):    # adds line of values to the end of df

        self.df.loc[len(self.df)] = [meter.value() for meter in self.meters]    # adds data from meters to df
        self.updateTable()    # clears table and fills it with updated df


    def updateTable(self):    # clears table and fills it with updated df

        self.tableWidget.clearContents()  # clears table completly but not df
        self.tableWidget.setRowCount(0)  # makes rowCount (hor dimension) equal to zero

        for i, row in self.df.iterrows():    # iterates the whole df

            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)    # adds new row to table

            for j in range(self.tableWidget.columnCount()):    # iterates table

                self.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(row[j])))    # sets item [i, j]


    def graph(self):    # creates mathplotlib thread with graph

        if self.tableWidget.rowCount():    # checks if table is not empty
            from matplotlib import pyplot as plt

            plt.axhline(y=0, color='black')    # adds black line y=0

            x = self.df[self.choose_X.currentText()]    # takes list of x values from df
            y = self.df[self.choose_Y.currentText()]    # takes list of y values from df

            if 'V' in self.choose_X.currentText():    # chooses volts or milliampers for x label
                plt.xlabel(f'{self.choose_X.currentText()}, В')
            elif "A" in self.choose_X.currentText():
                plt.xlabel(f'{self.choose_X.currentText()}, мА')

            if 'V' in self.choose_Y.currentText():    # chooses volts or milliampers for y label
                plt.ylabel(f'{self.choose_Y.currentText()}, В')
            elif "A" in self.choose_X.currentText():
                plt.ylabel(f'{self.choose_Y.currentText()}, мА')

            plt.plot(x, y)    # builds graph
            plt.grid()    # adds grid to graph
            plt.show()    # shows graph



class MainWindow(QtWidgets.QMainWindow, Data):    # class with program and COM-port interaction

    def __init__(self):

        super().__init__()    # inherits Data class

        try:
            UIFile = os.path.join(sys._MEIPASS, 'interface.ui')    # this line works during compilation to .exe

        except AttributeError:    # in pure Python sys raises this error
            UIFile = 'interface.ui'    # path for pure Python

        uic.loadUi(UIFile, self)    # loads UI from .ui file

        self.hotkeys()    # ties hotkeys to functions
        self.initializations()    # ties buttons to functions
        self.show()


    def hotkeys(self):

        self.addData_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+D"), self)
        self.addData_shortcut.activated.connect(self.addData)

        self.graph_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+G"), self)
        self.graph_shortcut.activated.connect(self.graph)

        self.serialSend_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Enter"), self)
        self.serialSend_shortcut.activated.connect(lambda: self.serialSend(self.inputVoltage.text()))


    def initializations(self):

        self.meters = [self.V1, self.V2, self.V3, self.V4,
                       self.A1, self.A2, self.A3, self.A4]    # list of volt- and ampermeters (meters)
        self.checkboxes = [self.V1_checkbox, self.V2_checkbox,
                           self.V3_checkbox, self.V4_checkbox,
                           self.A1_checkbox, self.A2_checkbox,
                           self.A3_checkbox, self.A4_checkbox]     # checkboxes to siwtch meter off or on

        self.connected = False    # variable to track connection status
        self.data = '0@0@0@0@0@0@0@0'    # primary data for meters

        self.choose_X.addItems(self.meter_names)    # adds V1, V2... to list where user chooses X
        self.choose_Y.addItems(self.meter_names)    # adds V1, V2... to list where user chooses Y
        self.choose_sort.addItems(self.meter_names)     # adds V1, V2... to list where user chooses column to sort
        self.exportCSV.clicked.connect(self.export_csv)    # ties button to function
        self.reset.clicked.connect(self.resetTable)    # ties button to function
        self.remove_last.clicked.connect(self.removeLast)    # ties button to function
        self.add_values.clicked.connect(self.addData)    # ties button to function
        self.graph_button.clicked.connect(self.graph)    # ties button to function
        self.sort_launch.clicked.connect(lambda: self.sort_by(self.choose_sort.currentText()))    # ties button to function

        self.update_ports()    # when program opens, list of ports gets added to menu
        self.updatePorts.clicked.connect(self.update_ports)   # button updates list of ports if user needs

        self.connect_MC.clicked.connect(lambda: self.openChosenPort(self.portList.currentText()))   #open choosen port
                                                                                                    # with speed 9600
        self.close_btn.clicked.connect(self.close)    # ties button to function

        self.setVoltage.clicked.connect(lambda: self.serialSend(self.inputVoltage.text()))    # ties button to function
        self.auto_launch.clicked.connect(    # ties button to function
            lambda: self.auto_vac(self.auto_begin.text(), self.auto_end.text(), self.auto_step.text()))


    def update_ports(self):    # clears list of ports and adds available

        self.portList.clear()    # clears widget list
        self.ports = [port.portName() for port in QSerialPortInfo().availablePorts()]    # creates list of ports
        self.portList.addItems(self.ports)    # adds list to widget


    def openChosenPort(self, port):    # opens choosen by user port with BaudRate 9600 and changes title "Подключено"

        from time import sleep
        if self.connected:    # checks if port is conected

            self.serial.close()    # closes port if True

        self.serial = QSerialPort()    # creating object of class
        self.serial.setBaudRate(QSerialPort.Baud9600)    # open port with speed 9600
        self.serial.setPortName(port)    # sets name of port choose by user
        self.serial.setDataTerminalReady(True)    # makes terminal ready
        self.connected = self.serial.open(QIODevice.ReadWrite)    # opens port for interaction

        if self.connected:    # checks if port is connected

            self.serial.readyRead.connect(self.onRead)    # makes onRead constantly work if True

            self.connect_label.setText('подключено')    # changes color and title to "Подключено" if True
            self.connect_label.setStyleSheet("background-color: lightgreen")

        else:
            self.connect_label.setText('ошибка')    # changes color and title to "Ошибка" if False
            self.connect_label.setStyleSheet("background-color: red")


    def onRead(self):    # constantly reads data from port and makes meters update

        if self.serial.canReadLine():    # checks if line can be read
            self.data = str(self.serial.readLine(), 'utf-8').strip()    # turns bytes to utf-8 string withuot '\n'
            self.updateAll()    # triggers update of meters


    def serialSend(self, data):    # send data to port

        if self.connected:    # checks if port is connected

            permittedSymbols = "0123456789. "    # permited symbols for input
            data = data.replace(' ', '')    # replaces ' ' with ''
            data = data.replace(',', '.')    # replaces "," with "."

            if data.replace('.', '').isdigit() and data.count('.') in [0, 1] and data != '' and data[0] != '.':
                                                                                        # checks if data is fine
                import struct
                data = int(float(data) * 1000)    # multiplies float on 1000
                                                  # to send integer to COM-port with three symbols after period
                self.serial.write(struct.pack("<H", data))    # sends unsigned int to port


    def close(self):

        if self.connected:    # checks if port is connected
            self.serial.close()    # closes conection
            self.connected = False    # turns status variable to False

            if not self.connected:
                self.connect_label.setText('не подключено')    # makes changes to color and title if True
                self.connect_label.setStyleSheet("background-color: red")

            else:
                self.connect_label.setText('ошибка')    # changes color and title to "Ошибка" if False
                self.connect_label.setStyleSheet("background-color: red")


    def multiplyString(self, string):    # this function is not used
        if '.' not in string:
            string = string + '.0'
        string = string.split('.')

        if len(string[1]) <= 3:
            res = string[0] + string[1].ljust(3, "0")

        else:
            res = string[0] + string[1][0:3]

        return int(res)


    def auto_vac(self, begin, end, step):    # IN PROCESS
        from numpy import linspace
        import time
        voltages = linspace(0, 10, 11)
        #voltages = linspace(float(begin), float(end), int(step))
        voltages = [round(v, 2) for v in voltages]

        for voltage in voltages:
            self.serialSend(str(voltage))
            print(self.data)


    def data_converter(self):    # convertes string with seven @ to list

        if self.data.count("@") == 7:    # checks if seven @ are in string
            array = self.data.split('@')    # splits string
            return [round(float(n), 2) for n in array]    # turns elements of list from str to rounded float

        else:
            return [0 for _ in range(8)]    # if @ are not in list returns list of 0


    def updateAll(self):    # updates meters switched by user

        values = self.data_converter()    # gets kist with eight floats

        for i in range(0, len(values)):    # iterates values by index

            if self.checkboxes[i].isChecked():    # checks if user switched on meter

                self.meters[i].display(values[i])    # displays float

            else:

                self.meters[i].display(0)    # turns meter to zero if not choosen



if __name__ == "__main__":    # launches program
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    app.exec_()