# rheagui.py (scaffolded minimal launcher)
from PyQt5 import QtWidgets
import sys
try:
    from rhea import Rhea
except Exception as e:
    print(f"[rheagui] Warning: could not import rhea.py: {e}")
    Rhea = None

def main():

    app = QtWidgets.QApplication(sys.argv)
    w = QtWidgets.QWidget()
    w.setWindowTitle("Rhea Control Panel — EdenOS (Scaffold)")
    w.resize(640, 360)
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
