"""
Biobank Specimen Transfer UI (PySide6)
- 작업 유형: 랙 / 튜브 선택
- 랙: A저장고 -> B저장고
- 튜브: A저장고(좌표) -> B저장고(좌표)
- 상태 패널 + 로그 테이블 + 버튼(시작/일시정지/정지/Reset/Home/로그 내보내기)

설치:
  pip install pyside6

실행:
  python biobank_ui.py
"""

import sys
import csv
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto

from PySide6.QtCore import Qt, QTimer, QObject, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QGroupBox, QRadioButton, QButtonGroup, QComboBox, QSpinBox, QLineEdit,
    QPushButton, QProgressBar, QTableWidget, QTableWidgetItem, QFileDialog,
    QMessageBox, QGridLayout, QFrame
)


# ----------------------------
# Domain model / fake backend
# ----------------------------
class JobType(Enum):
    RACK = "랙"
    TUBE = "튜브"


class Step(Enum):
    IDLE = "대기"
    PICK_A = "A 픽업"
    MOVE = "이동"
    PLACE_B = "B 배치"
    LOG = "로그 기록"
    DONE = "완료"
    ERROR = "오류"


@dataclass
class Job:
    job_type: JobType
    source: str
    dest: str
    rack_id: str = ""
    tube_id: str = ""
    a_row: int = 1
    a_col: int = 1
    b_row: int = 1
    b_col: int = 1


class FakeRobotController(QObject):
    """
    실제 로봇/서버(DART/DRL, TCP, ROS2 등) 연동 전,
    UI 동작 확인용 모의 컨트롤러.
    """
    state_changed = Signal(str, str, int)   # robot_state, step, progress(0-100)
    event = Signal(dict)                    # log event dict
    error = Signal(str)

    def __init__(self):
        super().__init__()
        self._timer = QTimer()
        self._timer.setInterval(600)  # ms
        self._timer.timeout.connect(self._tick)

        self._running = False
        self._paused = False
        self._job: Job | None = None

        self._steps = [Step.PICK_A, Step.MOVE, Step.PLACE_B, Step.LOG, Step.DONE]
        self._idx = 0

    def start(self, job: Job):
        if self._running and not self._paused:
            return
        self._job = job
        if not self._running:
            self._idx = 0
        self._running = True
        self._paused = False
        self.state_changed.emit("Busy", self._steps[self._idx].value, self._progress())
        self._timer.start()

    def pause(self):
        if not self._running:
            return
        self._paused = True
        self._timer.stop()
        self.state_changed.emit("Paused", self._steps[self._idx].value, self._progress())

    def stop(self):
        if not self._running:
            return
        self._timer.stop()
        self._running = False
        self._paused = False
        self._idx = 0
        self.state_changed.emit("Ready", Step.IDLE.value, 0)

    def reset(self):
        # 실제 시스템이면 에러 리셋/알람 클리어 같은 동작
        self.stop()

    def home(self):
        # 실제 시스템이면 홈 포지션 이동 명령
        self.event.emit(self._make_event(step="Home", result="SUCCESS"))
        self.state_changed.emit("Ready", Step.IDLE.value, 0)

    def _progress(self) -> int:
        # DONE 포함 5스텝 -> 0..100
        if not self._steps:
            return 0
        return int(min(100, (self._idx / (len(self._steps) - 1)) * 100))

    def _tick(self):
        if not self._running or self._paused:
            return
        if self._job is None:
            self.error.emit("Job is None")
            self.stop()
            return

        current_step = self._steps[self._idx]

        # 각 스텝에서 로그 1건 찍기(샘플)
        if current_step == Step.PICK_A:
            self.event.emit(self._make_event(step="픽업", result="SUCCESS"))
        elif current_step == Step.MOVE:
            self.event.emit(self._make_event(step="이동", result="SUCCESS"))
        elif current_step == Step.PLACE_B:
            self.event.emit(self._make_event(step="배치", result="SUCCESS"))
        elif current_step == Step.LOG:
            self.event.emit(self._make_event(step="로그 기록", result="SUCCESS"))

        # 다음 스텝
        self._idx += 1

        if self._idx >= len(self._steps):
            # 완료 처리 후 대기 복귀
            self.event.emit(self._make_event(step="완료", result="SUCCESS"))
            self.stop()
            return

        self.state_changed.emit("Busy", self._steps[self._idx].value, self._progress())

    def _make_event(self, step: str, result: str) -> dict:
        assert self._job is not None
        target = self._job.rack_id if self._job.job_type == JobType.RACK else self._job.tube_id
        if self._job.job_type == JobType.TUBE:
            target = f"{target} (A:{self._job.a_row}-{self._job.a_col} -> B:{self._job.b_row}-{self._job.b_col})".strip()

        return {
            "time": datetime.now().strftime("%H:%M:%S"),
            "type": self._job.job_type.value,
            "source": self._job.source,
            "dest": self._job.dest,
            "target": target if target else "-",
            "step": step,
            "result": result
        }


# ----------------------------
# UI
# ----------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("바이오뱅크 검체 이송 시스템 - Operation UI")
        self.resize(1180, 720)

        self.robot = FakeRobotController()
        self.robot.state_changed.connect(self.on_state_changed)
        self.robot.event.connect(self.append_log)
        self.robot.error.connect(self.on_error)

        self.logs: list[dict] = []

        root = QWidget()
        self.setCentralWidget(root)
        main = QVBoxLayout(root)
        main.setContentsMargins(14, 14, 14, 14)
        main.setSpacing(10)

        title = QLabel("바이오뱅크 검체 이송 시스템 - Operation UI")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        main.addWidget(title)

        # Top area: Setup + Status
        top = QHBoxLayout()
        top.setSpacing(10)
        main.addLayout(top, stretch=2)

        self.setup_box = self.build_setup_panel()
        self.status_box = self.build_status_panel()
        top.addWidget(self.setup_box, stretch=1)
        top.addWidget(self.status_box, stretch=1)

        # Bottom: logs
        logs_box = self.build_logs_panel()
        main.addWidget(logs_box, stretch=3)

        # Initialize UI state
        self.update_jobtype_ui()

    # ---------- Panels ----------
    def build_setup_panel(self) -> QGroupBox:
        box = QGroupBox("A. 작업 설정 (Job Setup)")
        lay = QVBoxLayout(box)
        lay.setSpacing(10)

        # Job type
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("작업 유형"))
        self.rb_rack = QRadioButton("랙 이송")
        self.rb_tube = QRadioButton("튜브 이송")
        self.rb_rack.setChecked(True)

        self.bg = QButtonGroup()
        self.bg.addButton(self.rb_rack)
        self.bg.addButton(self.rb_tube)

        self.rb_rack.toggled.connect(self.update_jobtype_ui)
        self.rb_tube.toggled.connect(self.update_jobtype_ui)

        row1.addStretch(1)
        row1.addWidget(self.rb_rack)
        row1.addWidget(self.rb_tube)
        lay.addLayout(row1)

        # Source/Dest
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)

        grid.addWidget(QLabel("출발지"), 0, 0)
        self.cb_source = QComboBox()
        self.cb_source.addItems(["A저장고", "A저장고(채혈/접수)", "A저장고(전처리)"])
        grid.addWidget(self.cb_source, 0, 1)

        grid.addWidget(QLabel("도착지"), 1, 0)
        self.cb_dest = QComboBox()
        self.cb_dest.addItems(["B저장고", "B저장고(전처리)", "B저장고(보관)"])
        grid.addWidget(self.cb_dest, 1, 1)

        # IDs
        grid.addWidget(QLabel("Rack ID (옵션)"), 2, 0)
        self.ed_rack_id = QLineEdit()
        self.ed_rack_id.setPlaceholderText("예: RACK-001")
        grid.addWidget(self.ed_rack_id, 2, 1)

        grid.addWidget(QLabel("Tube ID (옵션)"), 3, 0)
        self.ed_tube_id = QLineEdit()
        self.ed_tube_id.setPlaceholderText("예: T-003")
        grid.addWidget(self.ed_tube_id, 3, 1)

        # Tube coords (only when tube)
        self.tube_coords_frame = QFrame()
        tube_grid = QGridLayout(self.tube_coords_frame)
        tube_grid.setHorizontalSpacing(10)
        tube_grid.setVerticalSpacing(8)

        tube_grid.addWidget(QLabel("튜브 위치 (A저장고)"), 0, 0)
        self.sb_a_row = QSpinBox(); self.sb_a_row.setRange(1, 50); self.sb_a_row.setValue(1)
        self.sb_a_col = QSpinBox(); self.sb_a_col.setRange(1, 50); self.sb_a_col.setValue(1)
        tube_grid.addWidget(QLabel("Row"), 0, 1); tube_grid.addWidget(self.sb_a_row, 0, 2)
        tube_grid.addWidget(QLabel("Col"), 0, 3); tube_grid.addWidget(self.sb_a_col, 0, 4)

        tube_grid.addWidget(QLabel("튜브 위치 (B저장고)"), 1, 0)
        self.sb_b_row = QSpinBox(); self.sb_b_row.setRange(1, 50); self.sb_b_row.setValue(1)
        self.sb_b_col = QSpinBox(); self.sb_b_col.setRange(1, 50); self.sb_b_col.setValue(1)
        tube_grid.addWidget(QLabel("Row"), 1, 1); tube_grid.addWidget(self.sb_b_row, 1, 2)
        tube_grid.addWidget(QLabel("Col"), 1, 3); tube_grid.addWidget(self.sb_b_col, 1, 4)

        lay.addLayout(grid)
        lay.addWidget(self.tube_coords_frame)

        # Buttons (start/pause/stop)
        btn_row = QHBoxLayout()
        self.btn_start = QPushButton("시작")
        self.btn_pause = QPushButton("일시정지")
        self.btn_stop = QPushButton("정지")
        self.btn_start.clicked.connect(self.on_start)
        self.btn_pause.clicked.connect(self.on_pause)
        self.btn_stop.clicked.connect(self.on_stop)

        btn_row.addWidget(self.btn_start)
        btn_row.addWidget(self.btn_pause)
        btn_row.addWidget(self.btn_stop)
        lay.addLayout(btn_row)

        return box

    def build_status_panel(self) -> QGroupBox:
        box = QGroupBox("B. 현재 상태 (Live Status)")
        lay = QVBoxLayout(box)
        lay.setSpacing(10)

        # Connection / Robot state
        self.lb_conn = QLabel("연결 상태: Online")
        self.lb_robot = QLabel("로봇: Ready")
        self.lb_step = QLabel("현재 단계: 대기")
        self.pb = QProgressBar()
        self.pb.setRange(0, 100)
        self.pb.setValue(0)

        # Target / route
        self.lb_target = QLabel("대상: -")
        self.lb_route = QLabel("출발지: -   도착지: -")
        self.lb_last = QLabel("마지막 이벤트: -")

        # Alert
        alert = QGroupBox("상태 알림")
        alert_lay = QVBoxLayout(alert)
        self.lb_alert = QLabel("정상 동작 준비")
        self.lb_alert.setWordWrap(True)
        alert_lay.addWidget(self.lb_alert)

        # Utility buttons
        util = QHBoxLayout()
        self.btn_reset = QPushButton("Reset")
        self.btn_home = QPushButton("Home")
        self.btn_export = QPushButton("로그 내보내기")
        self.btn_reset.clicked.connect(self.on_reset)
        self.btn_home.clicked.connect(self.on_home)
        self.btn_export.clicked.connect(self.export_logs)
        util.addWidget(self.btn_reset)
        util.addWidget(self.btn_home)
        util.addWidget(self.btn_export)

        lay.addWidget(self.lb_conn)
        lay.addWidget(self.lb_robot)
        lay.addWidget(self.lb_step)
        lay.addWidget(self.pb)
        lay.addWidget(self.lb_target)
        lay.addWidget(self.lb_route)
        lay.addWidget(self.lb_last)
        lay.addWidget(alert)
        lay.addLayout(util)
        lay.addStretch(1)
        return box

    def build_logs_panel(self) -> QGroupBox:
        box = QGroupBox("C. 작업 큐 / 로그 (Queue & Log)")
        lay = QVBoxLayout(box)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(
            ["Time", "Type", "Source", "Dest", "Target", "Step", "Result"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        lay.addWidget(self.table)
        return box

    # ---------- UI helpers ----------
    def current_job_type(self) -> JobType:
        return JobType.RACK if self.rb_rack.isChecked() else JobType.TUBE

    def update_jobtype_ui(self):
        jt = self.current_job_type()
        is_tube = jt == JobType.TUBE
        self.tube_coords_frame.setVisible(is_tube)
        self.ed_tube_id.setEnabled(is_tube)
        self.ed_rack_id.setEnabled(not is_tube)

        # defaults / hints
        if is_tube:
            self.ed_tube_id.setFocus()
        else:
            self.ed_rack_id.setFocus()

    def make_job_from_ui(self) -> Job:
        jt = self.current_job_type()
        source = self.cb_source.currentText()
        dest = self.cb_dest.currentText()

        job = Job(job_type=jt, source=source, dest=dest)

        if jt == JobType.RACK:
            job.rack_id = self.ed_rack_id.text().strip()
        else:
            job.tube_id = self.ed_tube_id.text().strip()
            job.a_row = int(self.sb_a_row.value())
            job.a_col = int(self.sb_a_col.value())
            job.b_row = int(self.sb_b_row.value())
            job.b_col = int(self.sb_b_col.value())

        return job

    # ---------- Button handlers ----------
    def on_start(self):
        job = self.make_job_from_ui()
        # 최소 유효성: ID 없으면 그냥 "-"로 기록되게 놔두되, 튜브는 좌표는 필수(기본값이라 OK)
        self.lb_route.setText(f"출발지: {job.source}   도착지: {job.dest}")
        target_text = job.rack_id if job.job_type == JobType.RACK else job.tube_id
        if job.job_type == JobType.TUBE:
            target_text = f"{target_text or '-'} (A:{job.a_row}-{job.a_col} -> B:{job.b_row}-{job.b_col})"
        self.lb_target.setText(f"대상: {target_text or '-'}")

        self.lb_alert.setText("작업 시작")
        self.robot.start(job)

    def on_pause(self):
        self.lb_alert.setText("일시정지")
        self.robot.pause()

    def on_stop(self):
        self.lb_alert.setText("정지")
        self.robot.stop()

    def on_reset(self):
        self.lb_alert.setText("Reset 수행")
        self.robot.reset()

    def on_home(self):
        self.lb_alert.setText("Home 이동")
        self.robot.home()

    # ---------- Robot callbacks ----------
    def on_state_changed(self, robot_state: str, step: str, progress: int):
        self.lb_robot.setText(f"로봇: {robot_state}")
        self.lb_step.setText(f"현재 단계: {step}")
        self.pb.setValue(progress)

    def append_log(self, ev: dict):
        self.logs.append(ev)

        row = self.table.rowCount()
        self.table.insertRow(row)
        for c, k in enumerate(["time", "type", "source", "dest", "target", "step", "result"]):
            item = QTableWidgetItem(str(ev.get(k, "")))
            if k == "result":
                item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, c, item)

        self.table.scrollToBottom()
        self.lb_last.setText("마지막 이벤트: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def on_error(self, msg: str):
        self.lb_alert.setText(f"오류: {msg}")
        QMessageBox.critical(self, "오류", msg)

    # ---------- Export ----------
    def export_logs(self):
        if not self.logs:
            QMessageBox.information(self, "안내", "내보낼 로그가 없습니다.")
            return

        path, _ = QFileDialog.getSaveFileName(self, "로그 저장", "biobank_logs.csv", "CSV Files (*.csv)")
        if not path:
            return

        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                w = csv.DictWriter(f, fieldnames=["time", "type", "source", "dest", "target", "step", "result"])
                w.writeheader()
                for ev in self.logs:
                    w.writerow(ev)
            QMessageBox.information(self, "완료", f"저장 완료:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "오류", f"저장 실패:\n{e}")


def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
