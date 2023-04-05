import sys, os
from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QIODevice
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
import pandas as pd


class Data:
    def __init__(self):
        self.sorting_order = True

    def sort_by(self, name):
        #print(1)
        if self.tableWidget.rowCount():
            #print(self.tableWidget.rowCount())

            #print(name)

            #self.df = self.df.sort_values(by=name, ascending=self.sorting_order)
            self.df = self.df.sort_values(by=name, ignore_index=True, ascending=self.sorting_order)
            #print(self.sorting_order)
            self.sorting_order = not(self.sorting_order)
            #print(self.sorting_order)

            self.updateTable()

    def export_csv(self):
        dir = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', filter='*.csv')[0]
        #print(dir)
        if dir:
            self.df.to_csv(dir, index=False)

    def clear_table(self): #Clear tables but not DataFrame
        self.tableWidget.clear()
        headers = self.df.columns.values.tolist()
        self.tableWidget.setHorizontalHeaderLabels(headers)
        self.tableWidget.setRowCount(0)

    def resetTable(self): #Clearing both table and Dataframe
        button = QtWidgets.QMessageBox.question(self, "Подтверждение", "Really?")
        if button == QtWidgets.QMessageBox.Yes:
            self.df = pd.DataFrame(columns=[meter.objectName() for meter in self.meters])
            self.updateTable()

    def removeLast(self): #Removes the last row from both dataframe and table
        if self.tableWidget.rowCount():
            self.df.drop(labels=[len(self.df)-1], axis=0, inplace=True)
            self.updateTable()

    def addData(self):
        self.df.loc[len(self.df)] = [meter.value() for meter in self.meters] #Adds data from meters to DataFrame, turning string into float
        self.updateTable()
        #self.current_row += 1

    def updateTable(self):
        self.clear_table()
        #print(self.df.iterrows())
        for i, row in self.df.iterrows():
            #print(i, row)
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)

            for j in range(self.tableWidget.columnCount()):
                self.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(row[j])))

    def graph(self):


        CBxs = [self.V1_y, self.V2_y, self.V3_y, self.V4_y, self.A1_y, self.A2_y, self.A3_y, self.A4_y]
        Vs = [self.V1_y, self.V2_y, self.V3_y, self.V4_y]
        Is = [self.A1_y, self.A2_y, self.A3_y, self.A4_y]

        conny = dict(zip(CBxs, self.meters))
        colors = ['#FF7F50', '#A52A2A', '#458B00', '#20B2AA', '#1E90FF', '#800080', '#FF3E96', '#7F7F7F']
        names = ' '
        n = 0


        if self.tableWidget.rowCount() and any([box.isChecked() for box in CBxs]) and not(any([box.isChecked() for box in Vs])
                                                                                          and any([box.isChecked() for box in Is])):
            from matplotlib import pyplot as plt
            plt.axhline(y=0, color='black')
            x = self.df[self.choose_X.currentText()]

            if 'V' in self.choose_X.currentText():
                plt.xlabel(f'{self.choose_X.currentText()}, В')
            elif "A" in self.choose_X.currentText():
                plt.xlabel(f'{self.choose_X.currentText()}, мА')



            if any([box.isChecked() for box in Vs]):
                for box in Vs:
                    if box.isChecked():
                        y = self.df[box.objectName()[0:-2]]

                        plt.plot(x, y, color=colors[n], label=box.objectName()[0:-2])
                        names = names + f'{box.objectName()[0:-2]}, '
                        n = n + 1
                plt.ylabel(f"{names} В")

            else:
                for box in Is:
                    if box.isChecked():
                        y = self.df[box.objectName()[0:-2]]
                        plt.plot(x, y, color=colors[n], label=box.objectName()[0:-2])
                        names = names + f'{box.objectName()[0:-2]}, '
                        n = n + 1
                plt.ylabel(f"{names} мА")
            plt.legend()
            plt.grid()
            plt.show()

class SerialPort:
    def __init__(self):
        #self.COM_setup()
        self.update_ports() #when proram opens, list of ports gets added to menu
        self.connected = False #variable to track connection status
        self.data = '0@0@0@0@0@0@0@0' #data for initialisation

    def COM_setup(self): #REMOVE
        self.serial = QSerialPort()
        self.serial.setBaudRate(QSerialPort.Baud9600)
        #self.update_ports()


    def update_ports(self):
        self.portList.clear()
        self.ports = [port.portName() for port in QSerialPortInfo().availablePorts()]
        self.portList.addItems(self.ports)


    def openChosenPort(self, port):
        from time import sleep
        if self.connected:
            self.serial.close()
        self.serial = QSerialPort()
        self.serial.setBaudRate(QSerialPort.Baud9600)
        self.serial.setPortName(port)
        self.serial.setDataTerminalReady(True)
        self.connected = self.serial.open(QIODevice.ReadWrite)
        #print(self.connected)
        if self.connected:
            self.serial.readyRead.connect(self.onRead)



    def onRead(self):

        if self.serial.canReadLine():
            self.data = str(self.serial.readLine(), 'utf-8').strip()    #Turning bytes to str withuot '\n'


    def close(self):
        #print(2)
        self.serial.close()
        #print(1)
        self.connected = False

    def multiplyString(self, string): #Not used
        if '.' not in string:
            string = string + '.0'
        string = string.split('.')

        if len(string[1]) <= 3:
            res = string[0] + string[1].ljust(3, "0")

        else:
            res = string[0] + string[1][0:3]

        return int(res)

    def serialSend(self, data):
        #print(data)
        permittedSymbols = "0123456789. "
        data = data.replace(' ', '')
        data = data.replace(',', '.')
        if data.replace('.', '').isdigit() and data.count('.') in [0, 1] and data != '' and data[0]!='.':
            #print(data)
            #print(data)
            import struct
            data = int(float(data)*1000)
            #txs = ','.join(map(str, data)) + '\n'
            #print(data.encode())
            self.serial.write(struct.pack("<H", data))
            #self.serial.write(data.encode())


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

    def hotkeys(self):
        self.addData_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+D"), self)
        self.addData_shortcut.activated.connect(self.addData)

        self.graph_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+G"), self)
        self.graph_shortcut.activated.connect(self.graph)

        self.serialSend_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Enter"), self)
        self.serialSend_shortcut.activated.connect(lambda: self.serialSend(self.inputVoltage.text()))


    def initializations(self):
        self.meters = [self.V1, self.V2, self.V3, self.V4, self.A1, self.A2, self.A3, self.A4] #List of volt- and ampermeters
        self.checkboxes = [self.V1_checkbox, self.V2_checkbox, self.V3_checkbox, self.V4_checkbox,
                       self.A1_checkbox, self.A2_checkbox, self.A3_checkbox, self.A4_checkbox] #Checkboxes to choose if to siwtch volt/ampermeter pr not

        self.df = pd.DataFrame(columns=[meter.objectName() for meter in self.meters]) #dataframe to save results
        #self.tableWidget.selectionModel().selectionChanged.connect(self.on_selectionChanged) #TEST
        #self.df = pd.read_csv(r"C:\Users\desktop\Downloads\test.csv")
        #self.updateTable()
        #print(self.tableWidget.itemAt(0, 0).text())
        #self.df = pd.read_csv(r"C:\Users\desktop\Downloads\test.csv").sort_values(by="V2")
        #print(self.df)
        #self.updateTable()

        self.choose_X.addItems([meter.objectName() for meter in self.meters]) #add V1, V2... to list where user chooses X
        self.choose_sort.addItems([meter.objectName() for meter in self.meters])  #add V1, V2... to list where user chooses column to sort

        self.exportCSV.clicked.connect(self.export_csv)  # csv export
        self.reset.clicked.connect(self.resetTable)  # clears table
        self.remove_last.clicked.connect(self.removeLast)  # removes the last result
        self.add_values.clicked.connect(self.addData)  # Adding numbers to the tabl
        self.graph_button.clicked.connect(self.graph)  # Build graph
        self.sort_launch.clicked.connect(lambda: self.sort_by(self.choose_sort.currentText()))

        #print(self.ports)
        #self.MC = SerialPort()    #Creating SerialPort object to connect MicroController
        #self.update_portList()
        self.updatePorts.clicked.connect(self.update_ports) #update list of ports
        #print(self.portList.currentText())
        self.connect_MC.clicked.connect(lambda: self.openChosenPort(self.portList.currentText()))
        self.connect_MC.clicked.connect(self.show_MC_connected)     #After successful connection change light and unlock LCDs



    def auto_vac(self, begin, end, step):
        from numpy import linspace
        import time
        voltages = linspace(0, 10, 11)
        #voltages = linspace(float(begin), float(end), int(step))
        voltages = [round(v, 2) for v in voltages]

        for voltage in voltages:
            self.serialSend(str(voltage))
            print(self.data)


    def data_converter(self):
        if '@' in self.data:
            array = self.data.split('@')
            return [round(float(n), 2) for n in array]
            return array
        else:
            return ["0" for _ in range(8)]

    def show_MC_disconnected(self):
        if not self.connected:
            self.connect_label.setText('не подключено')
            self.connect_label.setStyleSheet("background-color: red")

    def show_MC_connected(self):
        if self.connected:
            self.connect_label.setText('подключено')
            self.connect_label.setStyleSheet("background-color: lightgreen")

            self.thread = MyThread()
            self.thread.mySignal.connect(self.updateAll)
            self.thread.start()

            self.setVoltage.clicked.connect(lambda: self.serialSend(self.inputVoltage.text()))
            self.auto_launch.clicked.connect(lambda: self.auto_vac(self.auto_begin.text(), self.auto_end.text(), self.auto_step.text()))

            self.close_btn.clicked.connect(self.close)
            self.close_btn.clicked.connect(self.show_MC_disconnected)

        else:
            self.connect_label.setText('ошибка')
            self.connect_label.setStyleSheet("background-color: red")


    def update_portList(self):
        self.portList.clear()
        #self.MC.update_ports()
        self.portList.addItems(self.ports)

    def updateAll(self):
        values = self.data_converter()

        for i in range(0, len(values)): #excluding V1
            if self.checkboxes[i].isChecked():
                self.meters[i].display(values[i])
                #self.meters[i].display(1)
            else:
                self.meters[i].display(0)




class MyThread(QThread):
    mySignal = pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.period = 10

    def run(self):
        while True:
            self.mySignal.emit(0)
            #print("MyThread working")
            QThread.msleep(self.period)

class MyThreadForAuto(QThread):
    mySignal = pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.period = 10

    def run(self):
        while True:
            self.mySignal.emit(0)
            #print("MyThread working")
            QThread.msleep(self.period)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    app.exec_()