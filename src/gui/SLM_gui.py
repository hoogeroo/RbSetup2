'''
SLM_gui.py: handles the SLM control dock

All widgets are defined in QtCreator in `gui.ui` under the `SLM_Control` dock.
This class only connects signals
'''

from PyQt6.QtCore import Qt, QObject
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QApplication, QFileDialog
import requests

SERVER_URL = "http://130.216.51.133:5000"


class SLMGui(QObject):
    def __init__(self, window):
        super().__init__(window)
        self.window = window
        self.locked = False
        self._pixmap: QPixmap | None = None

        # connect signals
        self.window.slm_upload_btn.clicked.connect(self.upload)
        self.window.slm_next_btn.clicked.connect(self.next_image)
        self.window.slm_refresh_btn.clicked.connect(self.refresh)
        self.window.slm_lock_btn.clicked.connect(self.toggle_lock)
        self.window.slm_shift_right_btn.clicked.connect(self.shift_right)
        self.window.slm_shift_up_btn.clicked.connect(self.shift_up)
        self.window.slm_angle_rot_btn.clicked.connect(self.rotate)
        self.window.slm_image_up_btn.clicked.connect(self.move_up)
        self.window.slm_image_down_btn.clicked.connect(self.move_down)
        self.window.slm_image_delete_btn.clicked.connect(self.delete_image)
        self.window.slm_image_save_btn.clicked.connect(self.save_order)

        # responsive image scaling
        self.window.slm_image_label.installEventFilter(self)

        # server init + load initial state
        try:
            requests.post(f"{SERVER_URL}/initialize", timeout=2)
        except Exception:
            pass

        app = QApplication.instance()
        if app:
            app.aboutToQuit.connect(self._on_quit)

        self._load_list()
        self.refresh()

    # event filter for responsive, rescalable image preview

    def eventFilter(self, obj, event):
        if obj is self.window.slm_image_label and event.type() == event.Type.Resize:
            self._scale_pixmap()
        return super().eventFilter(obj, event)

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
        if not self.locked:
            requests.post(f"{SERVER_URL}/lock", timeout=2)
            self.locked = True
            self.window.slm_lock_btn.setText("LOCK: ON")
        else:
            requests.post(f"{SERVER_URL}/unlock", timeout=2)
            self.locked = False
            self.window.slm_lock_btn.setText("LOCK: OFF")

    # actions

    def upload(self):
        if self.locked:
            return
        paths, _ = QFileDialog.getOpenFileNames(
            self.window, "Choose an image", "", "Images (*.png *.jpg *.jpeg)")
        if not paths:
            return
        for path in paths:
            with open(path, "rb") as f:
                requests.post(f"{SERVER_URL}/upload", files={"image": f}, timeout=15)
            requests.post(f"{SERVER_URL}/save_img", json={"params": [0, 0, 0]}, timeout=5)
        self._load_list()
        self.refresh()

    def next_image(self):
        requests.post(f"{SERVER_URL}/next", timeout=2)
        self.refresh()

    def shift_right(self):
        if self.locked:
            return
        pixels = self.window.slm_pixel_right_spin.value()
        requests.post(f"{SERVER_URL}/shift_right", data={"pixels_right": pixels}, timeout=2)
        self.refresh()

    def shift_up(self):
        if self.locked:
            return
        pixels = self.window.slm_pixel_up_spin.value()
        requests.post(f"{SERVER_URL}/shift_up", data={"pixels_up": pixels}, timeout=2)
        self.refresh()

    def rotate(self):
        if self.locked:
            return
        angle = self.window.slm_angle_rot_spin.value()
        requests.post(f"{SERVER_URL}/rotate", data={"angle": angle}, timeout=2)
        self.refresh()

    def _sync_lock(self):
        try:
            resp = requests.get(f"{SERVER_URL}/islocked", timeout=2)
            self.locked = bool(resp.json().get("lock", 0))
        except Exception:
            pass
        self.window.slm_lock_btn.setText("LOCK: ON" if self.locked else "LOCK: OFF")

    def refresh(self):
        self._sync_lock()

        # current image
        try:
            resp = requests.get(f"{SERVER_URL}/current", timeout=10)
            if resp.status_code == 200 and resp.content != b"No Current Image Available":
                print(f"[SLM] Got image data: {len(resp.content)} bytes")
                img = QImage()
                if img.loadFromData(resp.content):
                    self._pixmap = QPixmap.fromImage(img)
                    print(f"[SLM] Pixmap size: {self._pixmap.width()}x{self._pixmap.height()}")
                    self._scale_pixmap()
                else:
                    print("[SLM] QImage.loadFromData() failed — server sent unrecognised format")
            else:
                print(f"[SLM] /current: status={resp.status_code}, body={resp.content[:80]}")
        except Exception as e:
            print(f"[SLM] /current request failed: {e}")

        # image number
        try:
            resp = requests.get(f"{SERVER_URL}/num_img", timeout=2)
            if resp.status_code == 200:
                num = resp.json().get("num", [0, 0])
                self.window.slm_num_label.setText(f"Image n° {num[0]}/{num[1]}")
        except Exception:
            pass

        # shift value
        try:
            resp = requests.get(f"{SERVER_URL}/shift_value", timeout=2)
            if resp.status_code == 200:
                s = resp.json().get("shift", [0, 0, 0])
                self.window.slm_shift_label.setText(
                    f"Shift: right={s[0]}; up={-s[1]}; Rotation: {s[2]} deg")
        except Exception:
            pass

    # image list management

    def _load_list(self):
        try:
            resp = requests.get(f"{SERVER_URL}/list", timeout=2)
            data = resp.json()
            # server returns [filenames, shifts]
            items = data[0] if isinstance(data, list) and data and isinstance(data[0], list) else data
            self.window.slm_list_widget.clear()
            for name in items:
                self.window.slm_list_widget.addItem(name)
        except Exception:
            pass

    def move_up(self):
        if self.locked:
            return
        lw = self.window.slm_list_widget
        row = lw.currentRow()
        if row > 0:
            item = lw.takeItem(row)
            lw.insertItem(row - 1, item)
            lw.setCurrentRow(row - 1)

    def move_down(self):
        if self.locked:
            return
        lw = self.window.slm_list_widget
        row = lw.currentRow()
        if 0 <= row < lw.count() - 1:
            item = lw.takeItem(row)
            lw.insertItem(row + 1, item)
            lw.setCurrentRow(row + 1)

    def delete_image(self):
        if self.locked:
            return
        lw = self.window.slm_list_widget
        row = lw.currentRow()
        if row < 0:
            return
        filename = lw.item(row).text()
        resp = requests.post(f"{SERVER_URL}/remove", json={"filename": filename}, timeout=2)
        if resp.status_code == 200:
            lw.takeItem(row)
            self.refresh()

    def save_order(self):
        if self.locked:
            return
        lw = self.window.slm_list_widget
        order = [lw.item(i).text() for i in range(lw.count())]
        requests.post(f"{SERVER_URL}/reorder", json={"order": order}, timeout=2)

    # lifecycle

    def _on_quit(self):
        try:
            requests.post(f"{SERVER_URL}/rem_folder", timeout=2)
        except Exception:
            pass
