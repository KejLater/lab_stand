from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('interface.ui', self)
        self.connections()
        self.show()

    def connections(self):
        self.V1_b.stateChanged.connect(self.updateNumber)

    def updateNumber(self, state):
        if state == Qt.Checked:
            from randomer import RNG
            from time import sleep
            while True:
                print(RNG())
                self.V1.display(RNG())
                sleep(1)
        else:
            self.V1.display(0)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()