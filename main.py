from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('interface.ui', self)
        self.show()

        self.checkbox()

    def checkbox(self):
        self.V1_b.stateChanged.connect(self.updateNumber)


    def updateNumber(self, state):
        if state == Qt.Checked:
            from randomer import RNG
            self.V1.display(RNG())
        else:
            self.V1.display(0)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    app.exec_()