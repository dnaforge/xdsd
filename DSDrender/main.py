import sys

from app import app
from src.interface.ui_control import UiControl

if __name__ == "__main__":
    window = UiControl()
    window.show()
    sys.exit(app.exec())
