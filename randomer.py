"""This module is responsible for working with all the collected data"""

import pandas as pd
from PyQt5 import QtWidgets
import functools


class Data:
    """class for interaction with DataFrame (DF) and table_widget (table) where data is stored"""

    def __init__(self):
        self.sortingOrder = False  # reverses sorting order
        self.meterNames = ['V1', 'V2', 'V3', 'V4', 'A1', 'A2', 'A3', 'A4', 'N']  # label for columns
        self.DF = pd.DataFrame(columns=self.meterNames).astype(float)  # creates DF to store results
        self.DF['N'] = self.DF['N'].astype(int)  # makes all N integers
        self.N = 1

    def _update_table_widget_decorator(func):
        """decorator for calling update_table_widget() when needed"""

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self = args[0]
            func(*args, **kwargs)
            self.update_table_widget()
        return wrapper

    @_update_table_widget_decorator
    def sort_df_by_column(self, name):
        """sorts data in DF"""

        if len(self.DF):  # checks if DF is not empty

            self.DF = self.DF.sort_values(by=name, ascending=self.sortingOrder, ignore_index=True)
            self.sortingOrder = not (self.sortingOrder)  # reverses sorting order for next call

    def export_csv(self):
        """exports DF to csv"""

        dir = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', filter='*.csv')[0]  # calls dialogue window
        if dir:  # checks if user did not cancel export
            self.DF.to_csv(dir, index=False, decimal=',', sep=';')

    @_update_table_widget_decorator
    def reset_df_and_table(self):
        """clears both table and DF"""

        button = QtWidgets.QMessageBox.question(self, "Подтверждение", "Really?")  # confirmation from user

        if button == QtWidgets.QMessageBox.Yes:  # if user confirmed

            self.DF = pd.DataFrame(columns=self.meterNames)  # creates new DF rewriting variable
            self.N = 1


    @_update_table_widget_decorator
    def remove_last_from_df(self):  # drops the last row from both dataframe and table

        if len(self.DF):  # checks if table is not empty

            self.DF = self.DF.drop(labels=[len(self.DF) - 1], axis=0)


    @_update_table_widget_decorator
    def add_data_to_df(self):
        """adds line of values to the end of DF"""

        self.DF.loc[len(self.DF)] = [meter.value() for meter in self.meters] + [self.N]  # adds data from meters to DF

        self.N = self.N + 1


    @_update_table_widget_decorator
    def delete_by_N(self, n):
        """clears table and fills it with updated DF"""

        if len(self.DF):
            if int(n) in self.DF['N'].astype(int).tolist():

                self.DF = self.DF.drop(self.DF[self.DF['N'].astype(int) == int(n)].index)

    def update_table_widget(self):
        """instead of adding new data to table_widget I clear it and fill again by function update_table_widget()"""

        self.DF = self.DF.reset_index(drop=True)

        # table_widget is in main.py
        self.table_widget.clearContents()  # clears table completly but not DF
        self.table_widget.setRowCount(0)  # makes rowCount (horizontal dimension) equal to zero

        for i in range(self.DF.shape[0]):  # iterates the whole DF

            self.table_widget.setRowCount(self.table_widget.rowCount() + 1)  # adds new row to table

            for j in range(self.DF.shape[1]-1):  # iterates table by column

                self.table_widget.setItem(i, j, QtWidgets.QTableWidgetItem(
                f"{self.DF.iloc[i].iloc[j]}"))  # sets item [i, j]

            self.table_widget.setItem(i, 8, QtWidgets.QTableWidgetItem(
                f"{int(self.DF.iloc[i].iloc[8])}"))  # sets item [i, j]

        self.update_choose_delete_list()


    def update_choose_delete_list(self):
        """updates list of possible N"""

        self.choose_delete_list.clear()
        self.choose_delete_list.addItems(self.DF['N'].astype(int).astype(str).tolist())


    def build_graph_one_window(self):
        """plots I and V in the same subplot, not used now"""

        meases = [', В']*4 + [', мА']*4 + ['']  # needed to be added to xlabel

        Vs = [self.V1_y, self.V2_y, self.V3_y, self.V4_y]  # list of checkboxes for Y axis for V1-V4
        Is = [self.A1_y, self.A2_y, self.A3_y, self.A4_y]  # list of checkboxes for Y axis for A1-A4
        CBxs = Vs + Is

        from matplotlib import pyplot as plt
        import matplotlib.animation as animation
        plt.rcParams["font.family"] = "Century Gothic"

        fig, axV = plt.subplots()
        axA = axV.twinx()

        def animate(i):
            x = self.DF[self.choose_X_list.currentText()]

            y_V1 = self.DF['V1']
            y_V2 = self.DF['V2']
            y_V3 = self.DF['V3']
            y_V4 = self.DF['V4']

            y_A1 = self.DF['A1']
            y_A2 = self.DF['A2']
            y_A3 = self.DF['A3']
            y_A4 = self.DF['A4']

            N = self.DF['N']


            axV.clear()
            axA.clear()
            axV.grid()
            axA.grid()
            axV.set_ylabel('V, В')
            axV.axhline(y=0, color='black', linewidth=0.5)
            line_V1 = axV.plot(x, y_V1, c='#FF7F50', label='V1', marker='o', markersize=4, visible=Vs[0].isChecked())
            line_V2 = axV.plot(x, y_V2, c='#A52A2A', label='V2', marker='o', markersize=4, visible=Vs[1].isChecked())
            line_V3 = axV.plot(x, y_V3, c='#458B00', label='V3', marker='o', markersize=4, visible=Vs[2].isChecked())
            line_V4 = axV.plot(x, y_V4, c='#20B2AA', label='V4', marker='o', markersize=4, visible=Vs[3].isChecked())
            axV.legend(loc='upper left')
            axV.set_xlabel(self.choose_X_list.currentText() +
                           meases[self.choose_X_list.currentIndex()])  # chooses if volts or mA are in label


            axA.set_ylabel('I, мА')
            axA.axhline(y=0, color='black', linewidth=0.5)
            line_A1 = axA.plot(x, y_A1, c='#1E90FF', label='A1', marker='o', markersize=4, visible=Is[0].isChecked())
            line_A2 = axA.plot(x, y_A2, c='#800080', label='A2', marker='o', markersize=4, visible=Is[1].isChecked())
            line_A3 = axA.plot(x, y_A3, c='#FF3E96', label='A3', marker='o', markersize=4, visible=Is[2].isChecked())
            line_A4 = axA.plot(x, y_A4, c='#7F7F7F', label='A4', marker='o', markersize=4, visible=Is[3].isChecked())
            axA.legend(loc='upper right')


        self.ani = animation.FuncAnimation(fig, animate, interval=500)
        plt.show()

    def build_graph(self):
        """plots I and V in 2 vertical subplots, is in use now"""

        meases = [', мВ']*4 + [', мА']*4 + ['']  # needed to be added to xlabel

        Vs = [self.V1_y, self.V2_y, self.V3_y, self.V4_y]  # list of checkboxes for Y axis for V1-V4
        Is = [self.A1_y, self.A2_y, self.A3_y, self.A4_y]  # list of checkboxes for Y axis for A1-A4
        CBxs = Vs + Is

        from matplotlib import pyplot as plt
        import matplotlib.animation as animation

        plt.rcParams["font.family"] = "Century Gothic"

        fig, (axV, axA) = plt.subplots(nrows=2, ncols=1, sharex=True)  # two plots with common oX

        def animate(i):
            """regular update of picture"""

            # choose_X_list is in main.py
            # takes value from choose_X_widget for oX and updates values from DF
            x = self.DF[self.choose_X_list.currentText()]

            # updates value from DF
            y_V1 = self.DF['V1']
            y_V2 = self.DF['V2']
            y_V3 = self.DF['V3']
            y_V4 = self.DF['V4']

            y_A1 = self.DF['A1']
            y_A2 = self.DF['A2']
            y_A3 = self.DF['A3']
            y_A4 = self.DF['A4']

            # N = self.DF['N']  # not needed

            axV.clear()  # clears first plot
            axA.clear()  # clears second plot
            axV.grid()  # adds grid to first
            axA.grid()  # adds grid to second
            axV.set_ylabel('V, В')  # adds label to first
            axV.axhline(y=0, color='black', linewidth=0.5)  # draws thin black y=0 line

            # makes corresponding plot visible if checkbox is checked
            axV.plot(x, y_V1, c='#FF7F50', label='V1', marker='o', markersize=4, visible=Vs[0].isChecked())
            axV.plot(x, y_V2, c='#A52A2A', label='V2', marker='o', markersize=4, visible=Vs[1].isChecked())
            axV.plot(x, y_V3, c='#458B00', label='V3', marker='o', markersize=4, visible=Vs[2].isChecked())
            axV.plot(x, y_V4, c='#20B2AA', label='V4', marker='o', markersize=4, visible=Vs[3].isChecked())

            axV.legend()  # adds legend to first
            axA.set_xlabel(self.choose_X_list.currentText() +
                           meases[self.choose_X_list.currentIndex()])  # chooses if volts or mA are in label

            axA.set_ylabel('I, мА')  # adds label to second
            axA.axhline(y=0, color='black', linewidth=0.5)  # draws thin black y=0 line

            # makes corresponding plot visible if checkbox is checked
            axA.plot(x, y_A1, c='#1E90FF', label='A1', marker='o', markersize=4, visible=Is[0].isChecked())
            axA.plot(x, y_A2, c='#800080', label='A2', marker='o', markersize=4, visible=Is[1].isChecked())
            axA.plot(x, y_A3, c='#FF3E96', label='A3', marker='o', markersize=4, visible=Is[2].isChecked())
            axA.plot(x, y_A4, c='#7F7F7F', label='A4', marker='o', markersize=4, visible=Is[3].isChecked())

            axA.legend()  # adds legend to second

        self.ani = animation.FuncAnimation(fig, animate, interval=500)  # executes animation
        plt.show()