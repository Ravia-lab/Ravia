import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from ravia_ki.ui.dashboard import RaViaDashboard
from ravia_ki.utils.icons import get_best_icon_path


def main():
    app = QApplication(sys.argv)

    window = RaViaDashboard()

    icon = get_best_icon_path()
    if icon:
        window.setWindowIcon(QIcon(icon))

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

