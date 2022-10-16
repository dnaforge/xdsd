import sys

#from app import app
from DSDVis.interface.ui_control import UiControl

from PyQt5 import QtWidgets

app = QtWidgets.QApplication(sys.argv)

if __name__ == "__main__":
    window = UiControl()
    window.show()
    sys.exit(app.exec())
