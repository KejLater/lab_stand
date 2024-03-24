import pandas as pd
from PyQt5 import QtWidgets

class Data:  # class for interaction with DataFrame (DF) and table_widget (table) where data is stored
             # visible table_widget (table) is just derivative of DF
             # instead of adding new data to table I clear it and fill again by function update_tableWidget()
             # len(delf.DF) - number of rows

    def __init__(self):
        self.sortingOrder = False  # reverses sorting order
        self.meterNames = ['V1', 'V2', 'V3', 'V4', 'A1', 'A2', 'A3', 'A4', 'N']  # label for columns
        self.DF = pd.DataFrame(columns=self.meterNames).astype(float)  # creates DF to store results
        self.DF['N'] = self.DF['N'].astype(int)
        self.N = 1


    def sort_df_by_column(self, name):  # sorts data in DF

        if len(self.DF):  # checks if DF is not empty

            self.DF = self.DF.sort_values(by=name, ascending=self.sortingOrder, ignore_index=True)
            self.sortingOrder = not (self.sortingOrder)  # reverses sorting order for next call
            self.update_table_widget()  # clears table and fills it with updated DF


    def export_csv(self):  # exports DF to csv
        # import os  # for handling error
        dir = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', filter='*.csv')[0]  # calls dialogue window
        if dir:  # checks if user did not cancel export
            self.DF.to_csv(dir, index=False, decimal=',', sep=';')


    def reset_df_and_table(self):  # clears both table and DF

        button = QtWidgets.QMessageBox.question(self, "Подтверждение", "Really?")  # confirmation from user

        if button == QtWidgets.QMessageBox.Yes:  # if user confirmed

            self.DF = pd.DataFrame(columns=self.meterNames)  # creates new DF rewriting variable
            self.N = 1
            self.update_table_widget()  # clears table and fills it with updated DF


    def remove_last_from_df(self):  # dropes the last row from both dataframe and table

        if len(self.DF):  # checks if table is not empty

            self.DF = self.DF.drop(labels=[len(self.DF) - 1], axis=0)
            self.update_table_widget()  # clears table and fills it with updated DF


    def add_data_to_df(self):  # adds line of values to the end of DF

        self.DF.loc[len(self.DF)] = [meter.value() for meter in self.meters] + [self.N]  # adds data from meters to DF

        self.N = self.N + 1
        self.update_table_widget()  # clears table and fills it with updated DF


    def delete_by_N(self, n):
        if len(self.DF):
            if int(n) in self.DF['N'].astype(int).tolist():

                self.DF = self.DF.drop(self.DF[self.DF['N'].astype(int) == int(n)].index)

                self.update_table_widget()


    def update_table_widget(self):  # clears table and fills it with updated DF

        self.DF = self.DF.reset_index(drop=True)

        self.table_widget.clearContents()  # clears table completly but not DF
        self.table_widget.setRowCount(0)  # makes rowCount (horizontal dimension) equal to zero

        for i in range(self.DF.shape[0]):  # iterates the whole DF

            self.table_widget.setRowCount(self.table_widget.rowCount() + 1)  # adds new row to table

            for j in range(self.DF.shape[1]-1):  # iterates table by column

                self.table_widget.setItem(i, j, QtWidgets.QTableWidgetItem(
                f"{int(self.DF.iloc[i].iloc[j])}"))  # sets item [i, j]

            self.table_widget.setItem(i, 8, QtWidgets.QTableWidgetItem(
                f"{int(self.DF.iloc[i].iloc[8])}"))  # sets item [i, j]

        self.update_choose_delete_list()


    def update_choose_delete_list(self):

        self.choose_delete_list.clear()
        self.choose_delete_list.addItems(self.DF['N'].astype(int).astype(str).tolist())


    def build_graph(self):

        meases = [', В']*4 + [', мА']*4 + ['']  # needed to be added to xlabel

        Vs = [self.V1_y, self.V2_y, self.V3_y, self.V4_y]  # list of checkboxes for Y axis for V1-V4
        Is = [self.A1_y, self.A2_y, self.A3_y, self.A4_y]  # list of checkboxes for Y axis for A1-A4
        CBxs = Vs + Is


        if len(self.DF) and any([box.isChecked() for box in CBxs]):

            from matplotlib import pyplot as plt

            fig, axV = plt.subplots()
            axA = axV.twinx()
            axV.axhline(y=0, color='black', linewidth=0.5)
            axA.axhline(y=0, color='black', linewidth=0.5)
            axV.set_ylabel('V, В')
            axA.set_ylabel('I, мА')
            axV.grid()
            axA.grid()


            x = self.DF[self.choose_X_list.currentText()]
            
            axV.set_xlabel(self.choose_X_list.currentText() +
                           meases[self.choose_X_list.currentIndex()])  # chooses if volts or mA are in label


            y_V1 = self.DF['V1']
            y_V2 = self.DF['V2']
            y_V3 = self.DF['V3']
            y_V4 = self.DF['V4']

            y_A1 = self.DF['A1']
            y_A2 = self.DF['A2']
            y_A3 = self.DF['A3']
            y_A4 = self.DF['A4']

            N = self.DF['N']

            line_V1 = axV.plot(x, y_V1, c='#FF7F50', label='V1', marker='o', markersize=4, visible=Vs[0].isChecked())
            line_V2 = axV.plot(x, y_V2, c='#A52A2A', label='V2', marker='o', markersize=4, visible=Vs[1].isChecked())
            line_V3 = axV.plot(x, y_V3, c='#458B00', label='V3', marker='o', markersize=4, visible=Vs[2].isChecked())
            line_V4 = axV.plot(x, y_V4, c='#20B2AA', label='V4', marker='o', markersize=4, visible=Vs[3].isChecked())
            axV.legend(loc='upper left')

            line_A1 = axA.plot(x, y_A1, c='#1E90FF', label='A1', marker='o', markersize=4, visible=Is[0].isChecked())
            line_A2 = axA.plot(x, y_A2, c='#800080', label='A2', marker='o', markersize=4, visible=Is[1].isChecked())
            line_A3 = axA.plot(x, y_A3, c='#FF3E96', label='A3', marker='o', markersize=4, visible=Is[2].isChecked())
            line_A4 = axA.plot(x, y_A4, c='#7F7F7F', label='A4', marker='o', markersize=4, visible=Is[3].isChecked())
            axA.legend(loc='upper right')

            plt.show()