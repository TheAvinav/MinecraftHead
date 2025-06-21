import sys, os, math
from PyQt5.QtWidgets import QApplication, QLabel, QFileDialog
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QPixmap, QCursor, QTransform

class HeadOverlay(QLabel):
    def __init__(self, img_path):
        super().__init__()

        # Window flags: frameless, always‑on‑top, tool (no taskbar icon)
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)  # accept drag clicks

        # Load base pixmap and display it
        self.base_pix = QPixmap(img_path)
        self.setPixmap(self.base_pix)
        self.resize(self.base_pix.size())

        # Allow dragging the window by left‑click + move
        self.drag_position = None

        # For F10 edge‑detection
        self._last_f10 = False

        # Timer for rotation + toggle check
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update)
        self.timer.start(16)  # ~60 FPS

    def _update(self):
        # 1) Toggle on F10 press (edge‑detect)
        f10 = QCursor().pos()  # we’ll check via keyboard.is_pressed
        # (keyboard.is_pressed needs import; see note below)

        # Instead, poll F10 via PyQt native:
        # Qt doesn’t give global key state, so we fall back to keyboard lib:
        try:
            import keyboard
            curr = keyboard.is_pressed("F10")
        except ImportError:
            curr = False

        if curr and not self._last_f10:
            self.setVisible(not self.isVisible())
        self._last_f10 = curr

        if not self.isVisible():
            return

        # 2) Compute angle to cursor
        center = self.frameGeometry().center()
        cursor = QCursor.pos()
        dx = cursor.x() - center.x()
        dy = cursor.y() - center.y()
        angle = math.degrees(math.atan2(dy, dx)) + 90  # +90 to align “head up”

        # 3) Rotate pixmap
        transform = QTransform().rotate(angle)
        rotated = self.base_pix.transformed(transform, Qt.SmoothTransformation)
        self.setPixmap(rotated)
        # adjust size so masking/transparent areas update
        self.resize(rotated.size())

    # — Dragging support —
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.drag_position = e.globalPos() - self.frameGeometry().topLeft()
            e.accept()

    def mouseMoveEvent(self, e):
        if self.drag_position is not None:
            self.move(e.globalPos() - self.drag_position)
            e.accept()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.drag_position = None
            e.accept()

    # — (Optional) a method to pick new skin —
    def choose_new_skin(self):
        fn, _ = QFileDialog.getOpenFileName(
            self, "Select Skin PNG", os.getcwd(), "Image Files (*.png)"
        )
        if fn:
            self.base_pix = QPixmap(fn)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # ensure keyboard lib is installed
    try:
        import keyboard
    except ImportError:
        print("Install the keyboard module: pip install keyboard")
        sys.exit(1)

    overlay = HeadOverlay("steve_head.png")  # drop this PNG next to your script
    overlay.show()

    sys.exit(app.exec_())
