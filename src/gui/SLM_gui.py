'''
SLM_gui.py: handles the SLM control dock

All widgets are defined in QtCreator in `gui.ui` under the `SLM_Control` dock.
'''

from PyQt6.QtCore import Qt, QObject, QRunnable, QSize, QThreadPool, pyqtSignal
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QApplication, QFileDialog, QWidget, QHBoxLayout,
    QLabel, QSpinBox, QDoubleSpinBox, QListWidgetItem,
)
import requests

from src.device.device_types import SLMSettings, SLM_SERVER_URL as SERVER_URL


# worker for off-thread HTTP requests to avoid freezes and crashes

class _SLMWorkerSignals(QObject):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

class _SLMWorker(QRunnable):
    def __init__(self, task):
        super().__init__()
        self.task = task
        self.signals = _SLMWorkerSignals()

    def run(self):
        try:
            result = self.task()
            self.signals.finished.emit(result)
        except Exception as e:
            self.signals.error.emit(str(e))


# helper widgets 

class _ResizeFilter(QObject):
    """Fires a callback whenever the watched widget is resized."""
    def __init__(self, callback, parent=None):
        super().__init__(parent)
        self._callback = callback

    def eventFilter(self, obj, event):
        if event.type() == event.Type.Resize:
            self._callback()
        return False


class _ImageRowWidget(QWidget):
    def __init__(self, filename: str, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)

        self.filename = filename
        self.name_label = QLabel(filename)
        self.name_label.setMinimumWidth(80)

        self.shift_right_spin = QSpinBox()
        self.shift_right_spin.setRange(-5000, 5000)
        self.shift_right_spin.setPrefix("→ ")
        self.shift_right_spin.setToolTip("Shift right (px)")

        self.shift_up_spin = QSpinBox()
        self.shift_up_spin.setRange(-5000, 5000)
        self.shift_up_spin.setPrefix("↑ ")
        self.shift_up_spin.setToolTip("Shift up (px)")

        self.rotate_spin = QSpinBox()
        self.rotate_spin.setRange(0, 359)
        self.rotate_spin.setPrefix("⟳ ")
        self.rotate_spin.setToolTip("Rotation (deg)")

        self.hold_spin = QDoubleSpinBox()
        self.hold_spin.setRange(0, 100000)
        self.hold_spin.setValue(100.0)
        self.hold_spin.setSuffix(" ms")
        self.hold_spin.setToolTip("Hold time (ms)")

        for w in (self.name_label, self.shift_right_spin,
                  self.shift_up_spin, self.rotate_spin, self.hold_spin):
            layout.addWidget(w)

    def snapshot(self):
        return (self.filename, self.shift_right_spin.value(),
                self.shift_up_spin.value(), self.rotate_spin.value(),
                self.hold_spin.value())

    def apply(self, filename, shift_right, shift_up, rotate, hold):
        self.filename = filename
        self.name_label.setText(filename)
        self.shift_right_spin.setValue(shift_right)
        self.shift_up_spin.setValue(shift_up)
        self.rotate_spin.setValue(rotate)
        self.hold_spin.setValue(hold)

    def sizeHint(self):
        return QSize(400, 32)


# ── main class ──────────────────────────────────────────────────────────

class SLMGui:
    def __init__(self, window):
        self.window = window
        self.locked = False
        self._pixmap: QPixmap | None = None
        self._threadpool = QThreadPool()

        # list of _ImageRowWidget references
        self._rows: list[_ImageRowWidget] = []

        # Control-tab signals
        self.window.slm_upload_btn.clicked.connect(self.upload)
        self.window.slm_next_btn.clicked.connect(self.next_image)
        self.window.slm_refresh_btn.clicked.connect(self.refresh)
        self.window.slm_lock_btn.clicked.connect(self.toggle_lock)
        self.window.slm_shift_right_btn.clicked.connect(self.shift_right)
        self.window.slm_shift_up_btn.clicked.connect(self.shift_up)
        self.window.slm_angle_rot_btn.clicked.connect(self.rotate)

        # Image-list-tab signals
        self.window.slm_image_up_btn.clicked.connect(self.move_up)
        self.window.slm_image_down_btn.clicked.connect(self.move_down)
        self.window.slm_image_delete_btn.clicked.connect(self.delete_image)
        self.window.slm_image_save_btn.clicked.connect(self.save_order)

        # Experiment settings
        self.window.slm_exp_enable.stateChanged.connect(self._on_exp_settings_changed)
        self.window.slm_exp_insertion.currentIndexChanged.connect(self._on_exp_settings_changed)

        # keep Control-tab hold spinbox in sync with selected list row
        self.window.slm_image_hold.valueChanged.connect(self._on_ctrl_hold_changed)
        self.window.slm_list_widget.currentRowChanged.connect(self._on_selection_changed)

        # responsive image scaling
        self._resize_filter = _ResizeFilter(self._scale_pixmap, window)
        self.window.slm_image_label.installEventFilter(self._resize_filter)

        # server init 
        try:
            requests.post(f"{SERVER_URL}/initialize", timeout=2)
        except Exception:
            pass

        app = QApplication.instance()
        if app:
            app.aboutToQuit.connect(self._on_quit)

        self._load_list()
        self.refresh()

    # inline row helpers

    def _add_row(self, filename: str, hold: float = 100.0):
        row_widget = _ImageRowWidget(filename)
        row_widget.hold_spin.setValue(hold)

        item = QListWidgetItem(self.window.slm_list_widget)
        item.setSizeHint(row_widget.sizeHint())
        self.window.slm_list_widget.setItemWidget(item, row_widget)
        self._rows.append(row_widget)
        return row_widget

    def _row_at(self, index: int) -> _ImageRowWidget | None:
        if 0 <= index < len(self._rows):
            return self._rows[index]
        return None

    # SLM experiment settings

    def _on_ctrl_hold_changed(self, value):
        """Mirror Control-tab hold spinbox → inline widget for selected row."""
        row = self.window.slm_list_widget.currentRow()
        rw = self._row_at(row)
        if rw:
            rw.hold_spin.blockSignals(True)
            rw.hold_spin.setValue(value)
            rw.hold_spin.blockSignals(False)

    def _on_selection_changed(self, row):
        """Sync Control-tab hold spinbox when list selection changes."""
        rw = self._row_at(row)
        if rw:
            self.window.slm_image_hold.blockSignals(True)
            self.window.slm_image_hold.setValue(rw.hold_spin.value())
            self.window.slm_image_hold.blockSignals(False)

    def _on_exp_settings_changed(self):
        if not self.window.ui_loaded:
            return
        self.send_slm_settings()

    def refresh_stages(self):
        combo = self.window.slm_exp_insertion
        prev_data = combo.currentData()
        combo.blockSignals(True)
        combo.clear()
        combo.addItem("After All Stages", None)

        if hasattr(self.window, 'stages_gui'):
            for stage in self.window.stages_gui.stages:
                combo.addItem(f"After: {stage.label()}", str(stage.id))

        # restore previous selection if still present
        for i in range(combo.count()):
            if combo.itemData(i) == prev_data:
                combo.setCurrentIndex(i)
                break
        combo.blockSignals(False)

    def send_slm_settings(self):
        """Build an SLMSettings object and send it down the pipe."""
        hold_times = [rw.hold_spin.value() for rw in self._rows]

        settings = SLMSettings(
            enabled=self.window.slm_exp_enable.isChecked(),
            insertion_stage_id=self.window.slm_exp_insertion.currentData(),
            hold_times=hold_times,
        )
        self.window.gui_pipe.send(settings)

    # threaded HTTP helper

    def _run_slm(self, task, on_done=None):
        worker = _SLMWorker(task)
        if on_done:
            worker.signals.finished.connect(on_done)
        worker.signals.error.connect(lambda msg: print(f"[SLM] Request failed: {msg}"))
        self._threadpool.start(worker)

    # image preview scaling

    def _scale_pixmap(self):
        if not self._pixmap:
            return
        label = self.window.slm_image_label
        label.setPixmap(self._pixmap.scaled(
            max(1, label.width()), max(1, label.height()),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        ))

    # lock

    def toggle_lock(self):
        endpoint = "unlock" if self.locked else "lock"
        new_state = not self.locked

        def task():
            requests.post(f"{SERVER_URL}/{endpoint}", timeout=2)

        def on_done(_):
            self.locked = new_state
            self.window.slm_lock_btn.setText("LOCK: ON" if self.locked else "LOCK: OFF")

        self._run_slm(task, on_done)

    # Control-tab actions

    def upload(self):
        if self.locked:
            return
        paths, _ = QFileDialog.getOpenFileNames(
            self.window, "Choose an image", "", "Images (*.png *.jpg *.jpeg)")
        if not paths:
            return

        def task():
            for path in paths:
                with open(path, "rb") as f:
                    requests.post(f"{SERVER_URL}/upload", files={"image": f}, timeout=15)
                requests.post(f"{SERVER_URL}/save_img", json={"params": [0, 0, 0]}, timeout=5)

        self._run_slm(task, on_done=lambda _: (self._load_list(), self.refresh()))

    def next_image(self):
        def task():
            requests.post(f"{SERVER_URL}/next", timeout=2)
        self._run_slm(task, on_done=lambda _: self.refresh())

    def _shift_cur(self, shift):
        if self.locked:
            return
        def task():
            requests.post(f"{SERVER_URL}/shift_cur", json={"shift": shift}, timeout=2)
        self._run_slm(task, on_done=lambda _: self.refresh())

    def shift_right(self):
        self._shift_cur([self.window.slm_pixel_right_spin.value(), 0, 0])

    def shift_up(self):
        self._shift_cur([0, -self.window.slm_pixel_up_spin.value(), 0])

    def rotate(self):
        self._shift_cur([0, 0, self.window.slm_angle_rot_spin.value()])

    # refresh

    def refresh(self):
        def task():
            result = {}

            # lock state
            try:
                resp = requests.get(f"{SERVER_URL}/islocked", timeout=2)
                result['locked'] = bool(resp.json().get("lock", 0))
            except Exception:
                result['locked'] = self.locked

            # current image
            try:
                resp = requests.get(f"{SERVER_URL}/current", timeout=10)
                if resp.status_code == 200 and resp.content != b"No Current Image Available":
                    result['image_data'] = resp.content
            except Exception:
                pass

            # image number + shift
            try:
                resp = requests.get(f"{SERVER_URL}/num_img", timeout=2)
                if resp.status_code == 200:
                    num = resp.json().get("num", [0, 0])
                    result['num'] = num
                    idx = num[0] - 1 if num[0] > 0 else 0
                    sresp = requests.get(f"{SERVER_URL}/shift_value",
                                         json={"index": idx}, timeout=2)
                    if sresp.status_code == 200:
                        result['shift'] = sresp.json().get("shift", [0, 0, 0])
            except Exception:
                pass

            return result

        def on_done(result):
            self.locked = result.get('locked', self.locked)
            self.window.slm_lock_btn.setText("LOCK: ON" if self.locked else "LOCK: OFF")

            if 'image_data' in result:
                img = QImage()
                if img.loadFromData(result['image_data']):
                    self._pixmap = QPixmap.fromImage(img)
                    self._scale_pixmap()

            if 'num' in result:
                num = result['num']
                self.window.slm_num_label.setText(f"Image n° {num[0]}/{num[1]}")
            if 'shift' in result:
                s = result['shift']
                self.window.slm_shift_label.setText(
                    f"Shift: →{s[0]}  ↑{-s[1]}  ⟳{s[2]}°")

        self._run_slm(task, on_done)

    # image list management

    def _load_list(self):
        old_holds = {rw.filename: rw.hold_spin.value() for rw in self._rows}

        def task():
            resp = requests.get(f"{SERVER_URL}/list", timeout=2)
            return resp.json()

        def on_done(data):
            self.window.slm_list_widget.clear()
            self._rows.clear()
            filenames = data[0] if isinstance(data, list) and len(data) == 2 and isinstance(data[0], list) else (data if isinstance(data, list) else [])
            for name in filenames:
                hold = old_holds.get(name, 100.0)
                self._add_row(name, hold=hold)

        self._run_slm(task, on_done)

    def _swap_rows(self, a: int, b: int):
        """Swap the content of two rows in-place."""
        rw_a, rw_b = self._rows[a], self._rows[b]
        snap_a, snap_b = rw_a.snapshot(), rw_b.snapshot()
        rw_a.apply(*snap_b)
        rw_b.apply(*snap_a)

    def _move(self, delta):
        if self.locked:
            return
        lw = self.window.slm_list_widget
        row = lw.currentRow()
        new_row = row + delta
        if 0 <= row < lw.count() and 0 <= new_row < lw.count():
            self._swap_rows(row, new_row)
            lw.setCurrentRow(new_row)

    def move_up(self):
        self._move(-1)

    def move_down(self):
        self._move(1)

    def delete_image(self):
        if self.locked:
            return
        lw = self.window.slm_list_widget
        row = lw.currentRow()
        if row < 0:
            return
        rw = self._rows[row]

        def task():
            return requests.post(f"{SERVER_URL}/remove",
                                 json={"filename": rw.filename}, timeout=2)

        def on_done(resp):
            if resp.status_code == 200:
                lw.takeItem(row)
                self._rows.pop(row)
                self.refresh()

        self._run_slm(task, on_done)

    def save_order(self):
        if self.locked:
            return

        order = [rw.filename for rw in self._rows]
        shifts = [[rw.shift_right_spin.value(), rw.shift_up_spin.value(), rw.rotate_spin.value()]
                  for rw in self._rows]

        def task():
            requests.post(f"{SERVER_URL}/reorder",
                          json={"list": order, "shifts": shifts}, timeout=5)

        def on_done(_):
            for rw in self._rows:
                rw.shift_right_spin.setValue(0)
                rw.shift_up_spin.setValue(0)
                rw.rotate_spin.setValue(0)
            self.refresh()

        self._run_slm(task, on_done)

    # lifecycle

    def _on_quit(self):
        try:
            requests.post(f"{SERVER_URL}/rem_folder", timeout=2)
        except Exception:
            pass