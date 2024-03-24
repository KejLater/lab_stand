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

        Vs = [self.V1_y, self.V2_y, self.V3_y, self.V4_y]  # list of checkboxes for Y axis for V1-V4
        Is = [self.A1_y, self.A2_y, self.A3_y, self.A4_y]  # list of checkboxes for Y axis for A1-A4
        CBxs = Vs + Is

        colors = ['#FF7F50', '#A52A2A', '#458B00', '#20B2AA',
                    '#1E90FF', '#800080', '#FF3E96', '#7F7F7F']  # eight possible colors for lines
        label = ''  # string for X and Y labels

        if len(self.DF) and any([box.isChecked() for box in CBxs]):

            from matplotlib import pyplot as plt

            fig, axV = plt.subplots()
            axA = axV.twinx()
            axV.axhline(y=0, color='black', linewidth=0.5)
            axV.set_ylabel('V, В')
            axA.axhline(y=0, color='black', linewidth=0.5)
            axA.set_ylabel('I, мА')

            graphs = []    # var to install legend

            x = self.DF[self.choose_X_list.currentText()]

            if 'V' in self.choose_X_list.currentText():  # chooses if volts or mA are in label
                axV.set_xlabel(f'{self.choose_X_list.currentText()}, В')
            elif "A" in self.choose_X_list.currentText():
                axV.set_xlabel(f'{self.choose_X_list.currentText()}, мА')
            else:
                axV.set_xlabel('N')

            for box in Vs:

                if box.isChecked():

                    y = self.DF[box.objectName()[0:-2]]
                    line = axV.plot(x, y, colors.pop(), label=box.objectName()[0:-2], marker='o', markersize=4)
                    graphs.append(line[0])


            for box in Is:

                if box.isChecked():

                    y = self.DF[box.objectName()[0:-2]]
                    line = axA.plot(x, y, colors.pop(), label=box.objectName()[0:-2], marker='o', markersize=4)
                    graphs.append(line[0])

            axV.legend(graphs, [l.get_label() for l in graphs])
            axV.grid()
            axA.grid()
            plt.show()