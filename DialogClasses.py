try:
    import importlib
    import sys
    import time

    import PySide6.QtCore as qtc
    import PySide6.QtGui as qtg
    import PySide6.QtWidgets as qtw

    import Assets
except ImportError as e:
    importlib.import_module("tkinter.messagebox").showerror(type(e).__name__, str(e))
    print(e)
    time.sleep(3)
    sys.exit()


class ChangeLocationDialog(qtw.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Change Location")

        self.complex_label = qtw.QLabel("Complex number (x + yi):")
        self.complex_field = qtw.QLineEdit()
        self.complex_add_check_label = qtw.QLabel("Add to current complex number")
        self.complex_add_check = qtw.QCheckBox()

        self.zoom_label = qtw.QLabel("Current zoom (closer <- 1 -> distant):")
        self.zoom_field = qtw.QLineEdit()
        self.zoom_multiply_check_label = qtw.QLabel("Multiply to current zoom")
        self.zoom_multiply_check = qtw.QCheckBox()

        self.apply_button = qtw.QPushButton("Apply")
        self.apply_button.clicked.connect(self.acceptDialog)

        self.cancel_button = qtw.QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancelDialog)

        self.button_layout = qtw.QHBoxLayout()
        self.button_layout.addWidget(self.apply_button)
        self.button_layout.addWidget(self.cancel_button)

        self.main_layout = qtw.QGridLayout()
        self.main_layout.addWidget(self.complex_label, 0, 0)
        self.main_layout.addWidget(self.complex_field, 0, 1)

        self.main_layout.addWidget(self.zoom_label, 1, 0)
        self.main_layout.addWidget(self.zoom_field, 1, 1)

        self.main_layout.addWidget(self.complex_add_check_label, 0, 3)
        self.main_layout.addWidget(self.zoom_multiply_check_label, 1, 3)

        self.main_layout.addWidget(self.complex_add_check, 0, 2)
        self.main_layout.addWidget(self.zoom_multiply_check, 1, 2)

        self.main_layout.addLayout(self.button_layout, 2, 1)

        self.setLayout(self.main_layout)

    def obtainFieldData(self) -> tuple[str, str, bool, bool]:
        return (self.complex_field.text(),
                self.zoom_field.text(),
                self.complex_add_check.isChecked(),
                self.zoom_multiply_check.isChecked())

    def acceptDialog(self):
        self.accept()

    def cancelDialog(self):
        self.reject()


class AboutDialog(qtw.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        icon = qtg.QIcon(":/icon.png")

        self.setWindowTitle("Help")
        self.setModal(True)
        self.setContentsMargins(0, 0, 30, 30)

        self.text = '''
        <h1>About</h1>
        <p style="font-size: 15px;">Made by <b><i>Solar Stacer</i></b>, in Python using:
        <ul>
        <li><a href="https://doc.qt.io/qtforpython-6/">PySide6</a>, the official Python bindings for the native GUI development 
        framework for C++, Qt, by The Qt Company,</li>
        <li><a href="https://numpy.org/">Numpy</a>, a Python library for array computing,</li>
        </ul>
        </p>
        '''

        icon_label = qtw.QLabel()
        pixmap = icon.pixmap(qtc.QSize(100, 100))
        icon_label.setPixmap(pixmap)

        text_label = qtw.QLabel()
        text_label.setWordWrap(True)
        text_label.setOpenExternalLinks(True)
        text_label.setText(self.text)

        text_label.setAlignment(qtg.Qt.AlignmentFlag.AlignTop)

        scroll_area = qtw.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(qtw.QFrame.Shape.NoFrame)
        scroll_area.setWidget(text_label)

        scroll_area.setHorizontalScrollBarPolicy(qtc.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(qtc.Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        layout_1 = qtw.QVBoxLayout()
        layout_1.addWidget(icon_label)
        layout_1.setAlignment(icon_label, qtc.Qt.AlignmentFlag.AlignTop)
        layout_1.setContentsMargins(10, 10, 10, 10)

        main_layout = qtw.QHBoxLayout()
        main_layout.addLayout(layout_1)
        main_layout.addWidget(scroll_area)

        self.setLayout(main_layout)


class HowToUseDialog(qtw.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setModal(True)

        icon = qtg.QIcon(":/icon.png")

        icon_label = qtw.QLabel()
        pixmap = icon.pixmap(qtc.QSize(100, 100))
        icon_label.setPixmap(pixmap)

        md_file = qtc.QFile(":/README.md")
        if md_file.open(qtc.QIODevice.OpenModeFlag.ReadOnly):
            text = str(md_file.readAll(), encoding="utf-8")
            md_file.close()
        else:
            print(f"Qt Error: {md_file.errorString()}")
            return

        self.setWindowIcon(icon)

        screen_resolution = qtg.QGuiApplication.primaryScreen().size()
        self.setFixedSize(screen_resolution.width() - 400, screen_resolution.height() - 450)

        md_text_browser = qtw.QTextBrowser()
        md_text_browser.setFont(qtg.QFont("Segoe UI", 11))
        md_text_browser.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                border: none;
            }
        """)
        md_text_browser.setOpenExternalLinks(True)
        md_text_browser.setMarkdown(text)

        layout = qtw.QVBoxLayout()
        layout.addWidget(icon_label)
        layout.setAlignment(icon_label, qtc.Qt.AlignmentFlag.AlignTop)
        layout.setContentsMargins(10, 10, 10, 10)

        main_layout = qtw.QHBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(md_text_browser)

        self.setLayout(main_layout)
        self.setWindowTitle("How to Use?")


if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)
    h_t_u_dialog = HowToUseDialog()
    a_dialog = AboutDialog()
    c_l_dialog = ChangeLocationDialog()
    h_t_u_dialog.show()
    a_dialog.show()
    c_l_dialog.show()
    sys.exit(app.exec())
