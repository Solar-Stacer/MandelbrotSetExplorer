import subprocess

try:
    import ctypes
    import importlib
    import pathlib
    import sys

    sys.dont_write_bytecode = True
    import time

    from DialogClasses import *
    import numpy as np
    import Assets
except ImportError as e:
    importlib.import_module("tkinter.messagebox").showerror(type(e).__name__, str(e))
    print(e)
    time.sleep(3)
    sys.exit()

np.set_printoptions(threshold=sys.maxsize)


class MandelbrotTextLayer(qtw.QGraphicsObject):
    def __init__(self, parent=None):
        self.update_status = ""
        self.xy_zoom: tuple[float, float, float] = (0.0, 0.0, 1.0)
        self.font = qtg.QFont()
        self.font.setFamily("Lucida Console")
        self.font.setPointSize(10)
        super().__init__(parent)

    @qtc.Slot(float, float, float)
    def setLocation(self, x, y, zoom):
        self.xy_zoom = (x, y, zoom)
        self.update()

    @qtc.Slot(bool)
    def setUpdateStatus(self, boolean):
        if boolean:
            self.update_status = "Calculating..."
        else:
            self.update_status = ""
        self.update()

    def boundingRect(self):
        return qtc.QRectF(0, 0, SCENE_WIDTH, SCENE_HEIGHT)

    def paint(self, painter, option, widget=...):
        painter.setPen(qtg.QPen(qtg.Qt.GlobalColor.red, 7))
        painter.setFont(self.font)
        painter.drawText(10, 20, self.update_status)

        painter.setPen(qtg.QPen(qtg.Qt.GlobalColor.green, 7))
        painter.drawText(10, SCENE_HEIGHT - 10, f"{"{0} + {1}i, zoom: {2}".format(*self.xy_zoom)}")


class MandelbrotSetRegion(qtw.QGraphicsObject):
    SetUpdateStatus = qtc.Signal(bool)
    SetLocation = qtc.Signal(float, float, float)

    def __init__(self):
        super().__init__()
        self.setFlag(qtw.QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True)
        self.drag_offset = qtc.QPointF()
        self.zoom = 1
        self.moved_by_x = 0
        self.moved_by_y = 0

        self.grid = np.zeros(IMAGE_WIDTH * IMAGE_HEIGHT * 3, dtype=np.uint8).reshape(IMAGE_HEIGHT, IMAGE_WIDTH, 3)
        self.frame = qtg.QImage()
        self.drawFrame()

    def drawFrame(self):
        self.SetUpdateStatus.emit(True)
        qtw.QApplication.processEvents()

        flattened_grid = self.grid.flatten()
        c_grid_pointer = flattened_grid.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8))
        c_lib.set_mandelbrot_point(c_grid_pointer, IMAGE_WIDTH, IMAGE_HEIGHT,
                                   self.moved_by_x, self.moved_by_y, self.zoom)

        self.grid = flattened_grid.reshape(IMAGE_HEIGHT, IMAGE_WIDTH, 3)

        self.frame = qtg.QImage(self.grid.data,
                                self.grid.shape[1],
                                self.grid.shape[0],
                                self.grid.strides[0],
                                qtg.QImage.Format.Format_RGB888)

        self.SetUpdateStatus.emit(False)
        self.SetLocation.emit(self.moved_by_x, self.moved_by_y, self.zoom)
        self.update()

    def saveFrame(self):
        file_path = qtw.QFileDialog.getSaveFileName(None, "Save PNG", "mandelbrot.png", "PNG (*.png)")[0]
        if file_path:
            self.frame.save(f"{file_path}")

    def keyPressEvent(self, event, /):
        moving_constant = self.zoom / 2
        zooming_constant = 1.5
        if event.key() == qtc.Qt.Key.Key_W:
            self.moved_by_y += -moving_constant
            self.drawFrame()
        elif event.key() == qtc.Qt.Key.Key_A or event.key() == qtc.Qt.Key.Key_Left:
            self.moved_by_x += -moving_constant
            self.drawFrame()
        elif event.key() == qtc.Qt.Key.Key_S:
            self.moved_by_y += moving_constant
            self.drawFrame()
        elif event.key() == qtc.Qt.Key.Key_D or event.key() == qtc.Qt.Key.Key_Right:
            self.moved_by_x += moving_constant
            self.drawFrame()
        elif event.key() == qtc.Qt.Key.Key_Up:
            self.zoom /= zooming_constant
            self.drawFrame()
        elif event.key() == qtc.Qt.Key.Key_Down:
            self.zoom *= zooming_constant
            self.drawFrame()
        elif event.key() == qtc.Qt.Key.Key_Escape:
            self.moved_by_x, self.moved_by_y = 0, 0
            self.zoom = 1
            self.drawFrame()

    def obtainLocation(self):
        return complex(self.moved_by_x, self.moved_by_y), self.zoom

    def changeLocation(self, x: float, y: float, zoom_factor: float):
        self.moved_by_x, self.moved_by_y = x, y
        self.zoom = zoom_factor
        self.drawFrame()

    def boundingRect(self):
        return qtc.QRectF(0, 0, SCENE_WIDTH, SCENE_HEIGHT)

    def paint(self, painter, option, /, widget=...):
        painter.setRenderHint(qtg.QPainter.RenderHint.Antialiasing, False)
        painter.setRenderHint(qtg.QPainter.RenderHint.SmoothPixmapTransform, False)
        painter.drawImage(0, 0, self.frame.scaled(SCENE_WIDTH, SCENE_HEIGHT))
        painter.setPen(qtg.QPen(qtg.QColor("red"), 2))
        painter.setBrush(qtg.Qt.BrushStyle.NoBrush)
        painter.drawPolyline([
            qtc.QPointF(SCENE_WIDTH / 2, SCENE_HEIGHT / 2 + 10),
            qtc.QPointF(SCENE_WIDTH / 2, SCENE_HEIGHT / 2 - 10),
        ])
        painter.drawPolyline([
            qtc.QPointF(SCENE_WIDTH / 2 + 10, SCENE_HEIGHT / 2),
            qtc.QPointF(SCENE_WIDTH / 2 - 10, SCENE_HEIGHT / 2),
        ])


class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mandelbrot Set Explorer")

        self.mbs_region = MandelbrotSetRegion()
        self.mbs_text_layer = MandelbrotTextLayer()
        self.mbs_region.SetUpdateStatus.connect(self.mbs_text_layer.setUpdateStatus)
        self.mbs_region.SetLocation.connect(self.mbs_text_layer.setLocation)

        self.save_shortcut = qtg.QShortcut(qtg.QKeySequence("Ctrl+S"), self)
        self.save_shortcut.activated.connect(self.mbs_region.saveFrame)
        self.save_shortcut = qtg.QShortcut(qtg.QKeySequence("Ctrl+P"), self)
        self.save_shortcut.activated.connect(self.showChangeLocation)
        self.save_shortcut = qtg.QShortcut(qtg.QKeySequence("Ctrl+A"), self)
        self.save_shortcut.activated.connect(self.showAbout)
        self.save_shortcut = qtg.QShortcut(qtg.QKeySequence("Ctrl+H"), self)
        self.save_shortcut.activated.connect(self.showHowToUse)

        self.scene = qtw.QGraphicsScene()
        self.scene.addItem(self.mbs_region)
        self.scene.addItem(self.mbs_text_layer)
        self.scene.setSceneRect(0, 0, SCENE_WIDTH, SCENE_HEIGHT)
        self.mbs_region.setFocus()

        self.view = qtw.QGraphicsView()
        self.view.setScene(self.scene)
        self.view.setFrameStyle(qtw.QFrame.Shape.NoFrame)
        self.view.setFixedSize(SCENE_WIDTH, SCENE_HEIGHT)

        self.setCentralWidget(self.view)
        self.setFixedSize(self.sizeHint())
        self.showHowToUse()
        self.show()

    def showHowToUse(self):
        how_to_use_dialog = HowToUseDialog(self)
        how_to_use_dialog.exec()
        how_to_use_dialog.deleteLater()

    def showAbout(self):
        about_dialog = AboutDialog(self)
        about_dialog.exec()
        about_dialog.deleteLater()

    def showChangeLocation(self):
        change_location_dialog = ChangeLocationDialog(self)
        while True:
            rtn_val = change_location_dialog.exec()
            if rtn_val == qtw.QDialog.DialogCode.Accepted:
                (complex_number_string, zoom_factor_string,
                 complex_add_check, zoom_multiply_check) = change_location_dialog.obtainFieldData()
                try:
                    if complex_number_string != "":
                        complex_number = complex(complex_number_string.replace("i", "j").replace(" ", ""))
                        if complex_add_check:
                            complex_number += self.mbs_region.obtainLocation()[0]
                    else:
                        complex_number = self.mbs_region.obtainLocation()[0]

                    if zoom_factor_string != "":
                        zoom_factor = float(zoom_factor_string)
                        if zoom_factor <= 0:
                            raise ValueError("Invalid zoom factor.")
                        if zoom_multiply_check:
                            zoom_factor *= self.mbs_region.obtainLocation()[1]
                    else:
                        zoom_factor = self.mbs_region.obtainLocation()[1]
                except Exception as exc:
                    qtw.QMessageBox.critical(self, type(exc).__name__, str(exc))
                    continue
                self.mbs_region.changeLocation(x=complex_number.real, y=complex_number.imag, zoom_factor=zoom_factor)
            break
        change_location_dialog.deleteLater()


if __name__ == "__main__":
    app = qtw.QApplication(sys.argv)
    app.setWindowIcon(qtg.QIcon(":/icon.png"))

    constant = app.primaryScreen().size().height() - 200

    DEPTH_BASE = 10
    DEPTH_FACTOR = 1000
    MINIMUM_ITERATION = 500
    MBS_MIN_X, MBS_MAX_X = -2.3, 2.3
    MBS_MIN_Y, MBS_MAX_Y = -1.5, 1.5
    W_H_RATIO = (MBS_MIN_X - MBS_MAX_X) / (MBS_MIN_Y - MBS_MAX_Y)

    RESOLUTION = 1000
    IMAGE_WIDTH, IMAGE_HEIGHT = int(RESOLUTION * W_H_RATIO), int(RESOLUTION)

    SCENE_WIDTH, SCENE_HEIGHT = int(constant * W_H_RATIO), int(constant)

    # win32: gcc -shared -O3 -fopenmp -march=native -static -o bin/Mandelbrot.dll Mandelbrot.c
    # linux: gcc -shared -O3 -fopenmp -march=native -static -o bin/Mandelbrot.so Mandelbrot.c

    platform = sys.platform

    if platform.startswith("win"):
        library_path = pathlib.Path("bin/Mandelbrot.dll").absolute()
        compile_command = [
            "gcc", "-shared", "-O3", "-fopenmp", "-march=native",
            "-static", "-o", str(library_path), "Mandelbrot.c"
        ]
    elif platform.startswith("linux"):
        library_path = pathlib.Path("bin/Mandelbrot.so").absolute()
        compile_command = [
            "gcc", "-shared", "-O3", "-fopenmp", "-march=native",
            "-static", "-o", str(library_path), "Mandelbrot.c"
        ]
    else:
        raise OSError("Unsupported operating system.")

    try:
        c_lib = ctypes.CDLL(str(library_path))
    except OSError:
        print(f"Mandelbrot library not found. Compiling using:\n{' '.join(compile_command)}")

        library_path.parent.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(compile_command, capture_output=True, text=True)
        if result.returncode != 0:
            print("\nCompilation failed:")
            print(result.stderr)
            input("Press enter key to exit...")
            sys.exit(1)

        print("\nCompilation successful!")
        c_lib = ctypes.CDLL(str(library_path))

    c_lib.set_mandelbrot_point.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_int, ctypes.c_int,
                                           ctypes.c_double, ctypes.c_double, ctypes.c_double]
    c_lib.set_mandelbrot_point.restype = None

    c_lib.set_global_settings.argtypes = [ctypes.c_int, ctypes.c_int,
                                          ctypes.c_double, ctypes.c_double,
                                          ctypes.c_double, ctypes.c_double,
                                          ctypes.c_double, ctypes.c_double,
                                          ctypes.c_double]
    c_lib.set_global_settings.restype = None
    c_lib.set_global_settings(ctypes.c_int(IMAGE_WIDTH), ctypes.c_int(IMAGE_HEIGHT),
                              ctypes.c_double(MBS_MIN_X), ctypes.c_double(MBS_MAX_X),
                              ctypes.c_double(MBS_MIN_Y), ctypes.c_double(MBS_MAX_Y),
                              ctypes.c_double(DEPTH_FACTOR), ctypes.c_double(MINIMUM_ITERATION),
                              ctypes.c_double(DEPTH_BASE))

    main = MainWindow()

    sys.exit(app.exec())
