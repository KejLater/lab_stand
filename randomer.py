import pandas as pd
from PyQt5 import QtWidgets

class Data:  # class for interaction with DataFrame (DF) and tableWidget (table) where data is stored
             # visible tableWidget (table) is just derivative of DF
             # instead of adding new data to table I clear it and fill again by function update_tableWidget()
             # len(delf.DF) - number of rows

    def __init__(self):
        self.sortingOrder = True  # reverses sorting order
        self.meterNames = ['V1', 'V2', 'V3', 'V4', 'A1', 'A2', 'A3', 'A4']  # label for columns
        self.DF = pd.DataFrame(columns=self.meterNames)  # creates DF to store results


    def sort_df_by_column(self, name):  # sorts data in DF

        if len(self.DF):  # checks if DF is not empty

            self.DF = self.DF.sort_values(by=name, ignore_index=True, ascending=self.sortingOrder)
            self.sortingOrder = not (self.sortingOrder)  # reverses sorting order for next call
            self.update_tableWidget()  # clears table and fills it with updated DF


    def export_df_to_csv(self):  # exports DF to csv
        # import os  # for handling error
        dir = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', filter='*.csv')[0]  # calls dialogue window
        if dir:  # checks if user did not cancel export
            self.DF.to_csv(dir, index=False, decimal=',', sep=';')


    def reset_df_and_table(self):  # clears both table and DF

        button = QtWidgets.QMessageBox.question(self, "Подтверждение", "Really?")  # confirmation from user

        if button == QtWidgets.QMessageBox.Yes:  # if user confirmed

            self.DF = pd.DataFrame(columns=self.meterNames)  # creates new DF rewriting variable
            self.update_tableWidget()  # clears table and fills it with updated DF


    def remove_last_from_df(self):  # dropes the last row from both dataframe and table

        if len(self.DF):  # checks if table is not empty

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

            for j in range(self.tableWidget.columnCount()):  # iterates table by column

                self.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(row[j])))  # sets item [i, j]


    def build_graph(self):

        Vs = [self.V1_y, self.V2_y, self.V3_y, self.V4_y]  # list of checkboxes for Y axis for V1-V4
        Is = [self.A1_y, self.A2_y, self.A3_y, self.A4_y]  # list of checkboxes for Y axis for A1-A4
        CBxs = Vs + Is

        Vs_logic = any([box.isChecked() for box in Vs])
        Is_logic = any([box.isChecked() for box in Is])

        colors = ['#FF7F50', '#A52A2A', '#458B00', '#20B2AA',
                  '#1E90FF', '#800080', '#FF3E96', '#7F7F7F'] # eight possible colors for lines
        label = ''  # string for X and Y labels

        if len(self.DF) and (Vs_logic ^ Is_logic):

            from matplotlib import pyplot as plt
            plt.axhline(y=0, color='black', linewidth=0.5)

            x = self.DF[self.choose_X.currentText()]

            if 'V' in self.choose_X.currentText():  # chooses if volts or mA are in label
                plt.xlabel(f'{self.choose_X.currentText()}, В')
            elif "A" in self.choose_X.currentText():
                plt.xlabel(f'{self.choose_X.currentText()}, мА')

            if any([box.isChecked() for box in Vs]):
                for box in Vs:
                    if box.isChecked():
                        y = self.DF[box.objectName()[0:-2]]
                        plt.plot(x, y, colors.pop(), label=box.objectName()[0:-2], marker='o', markersize=4)
                        label = label + f'{box.objectName()[0:-2]}, '

                plt.ylabel(f"{label} В")
            else:
                for box in Is:
                    if box.isChecked():
                        y = self.DF[box.objectName()[0:-2]]
                        plt.plot(x, y, colors.pop(), label=box.objectName()[0:-2], marker='o', markersize=4)
                        label = label + f'{box.objectName()[0:-2]}, '

                plt.ylabel(f"{label} мА")
            plt.legend()
            plt.grid()
            plt.show()

