from __future__ import annotations

from PySide6.QtCore import QPoint, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QFont, QKeyEvent, QPainter, QPen
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from .config import AppConfig
from .unlock import UnlockState
from .windows_input import WindowsKeyBlocker


class CatButton(QPushButton):
    """Self-drawn character so the MVP has no external image dependency."""

    def __init__(self) -> None:
        super().__init__()
        self.setFixedSize(190, 190)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip("해제 준비를 하려면 캐릭터를 클릭하세요")
        self.setStyleSheet("QPushButton { border: none; background: transparent; }")

    def paintEvent(self, event) -> None:  # noqa: N802 - Qt method name
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor("#40354D"), 6)
        painter.setPen(pen)
        painter.setBrush(QColor("#FFD89C"))

        painter.drawPolygon([QPoint(48, 65), QPoint(62, 18), QPoint(93, 57)])
        painter.drawPolygon([QPoint(97, 57), QPoint(128, 18), QPoint(142, 65)])
        painter.drawEllipse(38, 48, 114, 108)

        painter.setBrush(QColor("#40354D"))
        painter.drawEllipse(70, 91, 10, 14)
        painter.drawEllipse(110, 91, 10, 14)
        painter.drawEllipse(91, 111, 8, 7)
        painter.drawLine(95, 118, 86, 126)
        painter.drawLine(95, 118, 104, 126)
        painter.end()


class CleaningOverlay(QWidget):
    finished = Signal(str)

    def __init__(self, config: AppConfig) -> None:
        super().__init__()
        self.config = config
        self.state = UnlockState(config.unlock_press_count)
        self.seconds_left = config.auto_unlock_seconds
        self.windows_key_blocker = WindowsKeyBlocker()

        self.setWindowTitle("잠깐닦냥 - 청소 모드")
        self.setWindowFlags(
            Qt.WindowType.Window
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setStyleSheet("background-color: #211A2B; color: #FFF8ED;")

        self.title = QLabel("마음 놓고 키보드를 닦아주세요")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setFont(QFont("Malgun Gothic", 25, QFont.Weight.Bold))

        self.character = CatButton()
        self.character.clicked.connect(self._arm_unlock)

        self.guide = QLabel("끝내려면 고양이를 클릭하세요")
        self.guide.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.guide.setFont(QFont("Malgun Gothic", 15))

        self.timer_label = QLabel()
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setStyleSheet("color: #C8BDD8;")

        center = QHBoxLayout()
        center.addStretch()
        center.addWidget(self.character)
        center.addStretch()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.addStretch(2)
        layout.addWidget(self.title)
        layout.addSpacing(20)
        layout.addLayout(center)
        layout.addSpacing(14)
        layout.addWidget(self.guide)
        layout.addSpacing(12)
        layout.addWidget(self.timer_label)
        layout.addStretch(2)

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._tick)
        self._update_timer_text()

    def start(self) -> None:
        self.windows_key_blocker.install()
        self.showFullScreen()
        self.raise_()
        self.activateWindow()
        self.setFocus(Qt.FocusReason.ActiveWindowFocusReason)
        self.timer.start()

    def keyPressEvent(self, event: QKeyEvent) -> None:  # noqa: N802
        # Ignore auto-repeat: holding space must not satisfy the gesture.
        if event.key() == Qt.Key.Key_Space and not event.isAutoRepeat():
            if self.state.register_space():
                self._finish("gesture")
            elif self.state.character_armed:
                self._update_guide()
        event.accept()

    def closeEvent(self, event) -> None:  # noqa: N802
        # Always release the OS hook, regardless of how this window is closed.
        self.timer.stop()
        self.windows_key_blocker.uninstall()
        event.accept()

    def _arm_unlock(self) -> None:
        self.state.arm()
        self.setFocus(Qt.FocusReason.MouseFocusReason)
        self._update_guide()

    def _update_guide(self) -> None:
        self.guide.setText(f"스페이스바를 {self.state.remaining}번 더 눌러주세요")

    def _tick(self) -> None:
        self.seconds_left -= 1
        self._update_timer_text()
        if self.seconds_left <= 0:
            self._finish("timeout")

    def _update_timer_text(self) -> None:
        self.timer_label.setText(f"안전을 위해 {self.seconds_left}초 후 자동으로 해제됩니다")

    def _finish(self, reason: str) -> None:
        self.timer.stop()
        self.finished.emit(reason)
        self.close()


class LauncherWindow(QMainWindow):
    def __init__(self, config: AppConfig) -> None:
        super().__init__()
        self.config = config
        self.overlay: CleaningOverlay | None = None
        self.setWindowTitle("잠깐닦냥")
        self.setFixedSize(460, 330)

        title = QLabel("잠깐닦냥")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Malgun Gothic", 24, QFont.Weight.Bold))

        description = QLabel(
            "키보드와 마우스를 닦는 동안\n다른 창이 눌리지 않도록 화면을 보호합니다."
        )
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setFont(QFont("Malgun Gothic", 12))

        self.status = QLabel("준비됨")
        self.status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status.setStyleSheet("color: #6A5C78;")

        start_button = QPushButton("청소 모드 시작")
        start_button.setMinimumHeight(52)
        start_button.setFont(QFont("Malgun Gothic", 12, QFont.Weight.Bold))
        start_button.clicked.connect(self._start_cleaning)
        start_button.setStyleSheet(
            "QPushButton { background: #7654A8; color: white; border: none; "
            "border-radius: 10px; padding: 12px; }"
            "QPushButton:hover { background: #8A68BC; }"
        )

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(48, 38, 48, 38)
        layout.addWidget(title)
        layout.addSpacing(15)
        layout.addWidget(description)
        layout.addStretch()
        layout.addWidget(start_button)
        layout.addSpacing(12)
        layout.addWidget(self.status)
        self.setCentralWidget(container)

    def _start_cleaning(self) -> None:
        self.overlay = CleaningOverlay(self.config)
        self.overlay.finished.connect(self._cleaning_finished)
        self.hide()
        self.overlay.start()

    def _cleaning_finished(self, reason: str) -> None:
        message = "청소 모드가 해제되었습니다."
        if reason == "timeout":
            message = "안전 타이머로 청소 모드가 자동 해제되었습니다."
        self.status.setText(message)
        self.show()
        self.raise_()
        self.activateWindow()


def run_app(config: AppConfig | None = None) -> int:
    app = QApplication.instance() or QApplication([])
    app.setApplicationName("잠깐닦냥")
    window = LauncherWindow(config or AppConfig())
    window.show()
    return app.exec()
