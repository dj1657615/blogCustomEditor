# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *

# ==========================================
# 모던 스타일 시트 (QSS)
# ==========================================
MODERN_STYLE = """
QWidget { font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif; }

/* 사이드바 */
QFrame#SideBar { background-color: #0E0E0E; }
QLabel#LogoTitle { color: #FFFFFF; font-size: 18pt; font-weight: 900; }
QLabel#LogoSub { color: #888888; font-size: 10pt; }

QPushButton.MenuButton {
    text-align: left; padding-left: 20px; font-size: 12pt; font-weight: bold;
    color: #888888; background-color: transparent; border-radius: 8px; height: 50px;
}
QPushButton.MenuButton:hover { background-color: #222222; color: #FFFFFF; }
QPushButton.MenuButton:checked { background-color: #FFFFFF; color: #0E0E0E; }

QFrame#StatusBox { background-color: #171A21; border-radius: 8px; }
QLabel#StatusTitle { color: #888888; font-size: 9pt; }
QLabel#StatusText { color: #FF4D4D; font-weight: bold; font-size: 11pt; }

/* 메인 영역 */
QStackedWidget#MainArea { background-color: #FAFAFB; }
QLabel.PageTitle { color: #111111; font-size: 20pt; font-weight: 900; }
QLabel.SectionTitle { color: #111111; font-size: 13pt; font-weight: bold; margin-top: 10px; margin-bottom: 5px; }

/* 테이블 & 리스트 */
QListWidget, QTableWidget {
    background-color: transparent; border: none; outline: none; font-size: 11pt; color: #333333;
}
QHeaderView::section { background-color: #F0F2F5; border: none; border-bottom: 1px solid #E5E5E5; padding: 10px; font-weight: bold; }
QTableWidget::item { padding: 10px; border-bottom: 1px solid #F0F0F0; }

/* 기본 입력 폼 */
QLineEdit, QSpinBox, QComboBox {
    background-color: #FFFFFF; border: 1px solid #E0E2E7; border-radius: 8px; padding: 10px 15px; font-size: 11pt;
}
QLineEdit:focus, QSpinBox:focus { border: 1px solid #111111; }

/* 액션 버튼 */
QPushButton.ActionBtn { background-color: #111111; color: #FFFFFF; font-weight: bold; font-size: 11pt; border-radius: 8px; padding: 12px 20px; }
QPushButton.ActionBtn:hover { background-color: #333333; }
QPushButton.SecondaryBtn { background-color: #F0F2F5; color: #555555; font-weight: bold; font-size: 11pt; border-radius: 8px; padding: 12px 20px; border: none;}
QPushButton.SecondaryBtn:hover { background-color: #E4E6EB; }

/* 위저드 토글 버튼 (첨부 사진의 40대, 50대 버튼 스타일) */
QPushButton.ToggleBtn {
    background-color: #F5F6F8; color: #555555; font-weight: bold; font-size: 11pt; border-radius: 20px; padding: 10px; border: none;
}
QPushButton.ToggleBtn:checked {
    background-color: #4B4EFC; color: #FFFFFF; /* 선택 시 블루/퍼플 계열 강조 */
}

/* 플랜 트래커 패널 */
QFrame#TrackerPanel { background-color: #FFFFFF; border: 1px solid #E0E2E7; border-radius: 12px; }
QLabel.TrackerHeader { color: #111111; font-weight: 900; font-size: 12pt; }
QLabel.TrackerLabel { color: #888888; font-size: 9pt; margin-top: 8px; }
QLabel.TrackerValue { color: #333333; font-size: 11pt; font-weight: bold; background-color: #F8F9FA; border-radius: 6px; padding: 8px; border: 1px solid #F0F0F0;}
"""

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1600, 900)
        MainWindow.setStyleSheet(MODERN_STYLE)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        MainWindow.setCentralWidget(self.centralwidget)

        self.main_layout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # ---------------------------------------------------------
        # 1. 사이드바
        # ---------------------------------------------------------
        self.sidebar = QtWidgets.QFrame(self.centralwidget)
        self.sidebar.setObjectName("SideBar")
        self.sidebar.setFixedWidth(260)
        self.sidebar_layout = QtWidgets.QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(20, 30, 20, 20)

        self.lbl_logo = QtWidgets.QLabel("블로그 자동화", self.sidebar)
        self.lbl_logo.setObjectName("LogoTitle")
        self.lbl_sub = QtWidgets.QLabel("포스팅 자동화", self.sidebar)
        self.lbl_sub.setObjectName("LogoSub")
        self.sidebar_layout.addWidget(self.lbl_logo)
        self.sidebar_layout.addWidget(self.lbl_sub)
        self.sidebar_layout.addSpacing(40)

        self.menu_btn_group = QtWidgets.QButtonGroup(MainWindow)
        self.menu_btn_group.setExclusive(True)

        self.btn_home = self.create_menu_btn("🏠  홈", 0)
        self.btn_campaign = self.create_menu_btn("📋  캠페인 관리", 1)
        self.btn_account = self.create_menu_btn("👤  계정 관리", 2)
        self.btn_settings = self.create_menu_btn("⚙️  프로그램 설정", 3)
        self.btn_home.setChecked(True)

        self.sidebar_layout.addWidget(self.btn_home)
        self.sidebar_layout.addWidget(self.btn_campaign)
        self.sidebar_layout.addWidget(self.btn_account)
        self.sidebar_layout.addWidget(self.btn_settings)
        self.sidebar_layout.addStretch()

        self.status_box = QtWidgets.QFrame(self.sidebar)
        self.status_box.setObjectName("StatusBox")
        self.status_layout = QtWidgets.QVBoxLayout(self.status_box)
        self.lbl_stat_title = QtWidgets.QLabel("계정 연동 상태", self.status_box)
        self.lbl_stat_title.setObjectName("StatusTitle")
        self.lbl_stat_text = QtWidgets.QLabel("ⓧ 연동 안됨", self.status_box)
        self.lbl_stat_text.setObjectName("StatusText")
        self.status_layout.addWidget(self.lbl_stat_title)
        self.status_layout.addWidget(self.lbl_stat_text)
        self.sidebar_layout.addWidget(self.status_box)

        self.main_layout.addWidget(self.sidebar)

        # ---------------------------------------------------------
        # 2. 메인 영역 스택
        # ---------------------------------------------------------
        self.main_stack = QtWidgets.QStackedWidget(self.centralwidget)
        self.main_stack.setObjectName("MainArea")
        self.main_layout.addWidget(self.main_stack)

        # 2-1. 홈 화면 (유지)
        self.page_home = QtWidgets.QWidget()
        self.layout_home = QtWidgets.QVBoxLayout(self.page_home)
        self.layout_home.setContentsMargins(50, 40, 50, 40)
        self.layout_home.setSpacing(20)
        lbl_home_title = QtWidgets.QLabel("대시보드")
        lbl_home_title.setProperty("class", "PageTitle")
        self.layout_home.addWidget(lbl_home_title)
        
        lbl_sched = QtWidgets.QLabel("작업 예정 목록")
        lbl_sched.setProperty("class", "SectionTitle")
        self.list_schedule = QtWidgets.QListWidget()
        self.list_schedule.setStyleSheet("background-color: white; border: 1px solid #E5E5E5; border-radius: 8px;")
        self.layout_home.addWidget(lbl_sched)
        self.layout_home.addWidget(self.list_schedule, 1)

        lbl_log = QtWidgets.QLabel("구동 기록 (로그)")
        lbl_log.setProperty("class", "SectionTitle")
        self.log_table = QtWidgets.QTableWidget()
        self.log_table.setStyleSheet("background-color: white; border: 1px solid #E5E5E5; border-radius: 8px;")
        self.log_table.setColumnCount(3)
        self.log_table.setHorizontalHeaderLabels(["시간", "작업내역", "상태"])
        self.log_table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.log_table.verticalHeader().setVisible(False)
        self.log_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.layout_home.addWidget(lbl_log)
        self.layout_home.addWidget(self.log_table, 1)
        self.main_stack.addWidget(self.page_home)

        # 2-2. 캠페인 관리 화면 (비워두고 main.py에서 구성)
        self.page_campaign = QtWidgets.QWidget()
        self.layout_campaign = QtWidgets.QVBoxLayout(self.page_campaign)
        self.layout_campaign.setContentsMargins(0, 0, 0, 0)
        self.main_stack.addWidget(self.page_campaign)

        # 2-3. 계정 및 설정
        self.page_account = QtWidgets.QWidget()
        self.layout_account = QtWidgets.QVBoxLayout(self.page_account)
        self.main_stack.addWidget(self.page_account)

        self.page_settings = QtWidgets.QWidget()
        self.layout_settings = QtWidgets.QVBoxLayout(self.page_settings)
        self.main_stack.addWidget(self.page_settings)

    def create_menu_btn(self, text, index):
        btn = QtWidgets.QPushButton(text)
        btn.setProperty("class", "MenuButton")
        btn.setCheckable(True)
        self.menu_btn_group.addButton(btn, index)
        return btn