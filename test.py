# -*- coding: utf-8 -*-
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

# ==========================================
# 모던 스타일 시트 (QSS) - 첨부 이미지 디자인 반영
# ==========================================
MODERN_STYLE = """
/* 메인 윈도우 기본 폰트 설정 */
QWidget {
    font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
}

/* ==================================
   좌측 사이드바 스타일
================================== */
QFrame#SideBar {
    background-color: #0E0E0E; /* 블랙 배경 */
}

QLabel#LogoTitle {
    color: #FFFFFF;
    font-size: 18pt;
    font-weight: 900;
}
QLabel#LogoSub {
    color: #888888;
    font-size: 10pt;
}

/* 사이드바 메뉴 버튼 */
QPushButton.MenuButton {
    text-align: left;
    padding-left: 20px;
    font-size: 12pt;
    font-weight: bold;
    color: #888888;
    background-color: transparent;
    border-radius: 8px; /* 둥근 모서리 */
    height: 50px;
    margin-bottom: 5px;
}
QPushButton.MenuButton:hover {
    background-color: #222222;
    color: #FFFFFF;
}
/* 선택된 메뉴 버튼 상태 (화이트 배경, 블랙 텍스트) */
QPushButton.MenuButton:checked {
    background-color: #FFFFFF;
    color: #0E0E0E;
}

/* 하단 상태 박스 */
QFrame#StatusBox {
    background-color: #171A21;
    border-radius: 8px;
}
QLabel#StatusTitle { color: #888888; font-size: 9pt; }
QLabel#StatusText { color: #FF4D4D; font-weight: bold; font-size: 11pt; } /* 미연동시 레드, 연동시 그린(#00D26A) 등으로 변경 가능 */

/* ==================================
   우측 메인 영역 스타일
================================== */
QStackedWidget#MainArea {
    background-color: #FFFFFF;
}

/* 메인 영역 내 타이틀 */
QLabel.PageTitle {
    color: #000000;
    font-size: 18pt;
    font-weight: 900;
}
QLabel.SectionTitle {
    color: #000000;
    font-size: 13pt;
    font-weight: bold;
    margin-top: 10px;
    margin-bottom: 5px;
}

/* 리스트, 테이블 기본 스타일 */
QListWidget, QTableWidget {
    background-color: #FFFFFF;
    border: 1px solid #E5E5E5;
    border-radius: 8px;
    outline: none;
    font-size: 11pt;
    color: #333333;
    padding: 5px;
}
QHeaderView::section {
    background-color: #F8F9FA;
    border: none;
    border-bottom: 1px solid #E5E5E5;
    padding: 10px;
    font-weight: bold;
    color: #555555;
}
QListWidget::item, QTableWidget::item {
    padding: 10px;
    border-bottom: 1px solid #F0F0F0;
}
QListWidget::item:selected, QTableWidget::item:selected {
    background-color: #F4F4F4;
    color: #000000;
}

/* 메인 영역 공통 액션 버튼 (저장하기 등) */
QPushButton.ActionBtn {
    background-color: #0E0E0E;
    color: #FFFFFF;
    font-weight: bold;
    font-size: 11pt;
    border-radius: 8px;
    padding: 10px 20px;
}
QPushButton.ActionBtn:hover { background-color: #333333; }
"""

class ModernDashboardApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # 해상도 1600x900 설정
        self.setWindowTitle("블로그 자동화 프로그램")
        self.resize(1600, 900)
        self.setStyleSheet(MODERN_STYLE)
        
        # 버튼 그룹 (메뉴 단일 선택 토글용)
        self.menu_btn_group = QButtonGroup(self)
        self.menu_btn_group.setExclusive(True)

        self.setup_ui()

    def setup_ui(self):
        # 전체를 감싸는 센트럴 위젯과 HBox 레이아웃 (여백 0)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ---------------------------------------------------------
        # 1. 좌측 사이드바 (SideBar) 구성
        # ---------------------------------------------------------
        self.sidebar = QFrame()
        self.sidebar.setObjectName("SideBar")
        self.sidebar.setFixedWidth(260)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(20, 30, 20, 20)

        # 1-1. 로고 영역
        lbl_logo = QLabel("유나우랩 블로그")
        lbl_logo.setObjectName("LogoTitle")
        lbl_sub = QLabel("자동화 솔루션 v1.0")
        lbl_sub.setObjectName("LogoSub")
        
        sidebar_layout.addWidget(lbl_logo)
        sidebar_layout.addWidget(lbl_sub)
        sidebar_layout.addSpacing(40)

        # 1-2. 메뉴 버튼 생성
        self.btn_home = self.create_menu_button("🏠  홈", 0)
        self.btn_campaign = self.create_menu_button("📋  캠페인 관리", 1)
        self.btn_account = self.create_menu_button("👤  계정 관리", 2)
        self.btn_settings = self.create_menu_button("⚙️  프로그램 설정", 3)
        
        sidebar_layout.addWidget(self.btn_home)
        sidebar_layout.addWidget(self.btn_campaign)
        sidebar_layout.addWidget(self.btn_account)
        sidebar_layout.addWidget(self.btn_settings)
        sidebar_layout.addStretch() # 빈 공간 채우기

        # 1-3. 하단 계정 상태 박스
        status_box = QFrame()
        status_box.setObjectName("StatusBox")
        status_layout = QVBoxLayout(status_box)
        status_layout.setContentsMargins(15, 15, 15, 15)
        
        lbl_stat_title = QLabel("계정 연동 상태")
        lbl_stat_title.setObjectName("StatusTitle")
        lbl_stat_text = QLabel("ⓧ 연동 안됨")
        lbl_stat_text.setObjectName("StatusText")
        
        status_layout.addWidget(lbl_stat_title)
        status_layout.addWidget(lbl_stat_text)
        sidebar_layout.addWidget(status_box)

        main_layout.addWidget(self.sidebar)

        # ---------------------------------------------------------
        # 2. 우측 메인 영역 (MainArea) 구성
        # ---------------------------------------------------------
        self.main_stack = QStackedWidget()
        self.main_stack.setObjectName("MainArea")
        main_layout.addWidget(self.main_stack)

        # 페이지 초기화 및 추가
        self.page_home = self.create_home_page()
        self.page_campaign = self.create_placeholder_page("캠페인 관리", "이곳에 이전 단계의 '캠페인 위저드'를 결합합니다.")
        self.page_account = self.create_placeholder_page("계정 관리", "계정 등록 및 삭제를 관리하는 화면입니다.")
        self.page_settings = self.create_placeholder_page("프로그램 설정", "LLM API 키 및 기타 설정을 관리합니다.")

        self.main_stack.addWidget(self.page_home)
        self.main_stack.addWidget(self.page_campaign)
        self.main_stack.addWidget(self.page_account)
        self.main_stack.addWidget(self.page_settings)

        # 기본 화면을 홈으로 설정
        self.btn_home.setChecked(True)

    # ==========================================
    # 사이드바 메뉴 버튼 생성 헬퍼 함수
    # ==========================================
    def create_menu_button(self, text, index):
        btn = QPushButton(text)
        btn.setProperty("class", "MenuButton")
        btn.setCheckable(True)
        self.menu_btn_group.addButton(btn, index)
        # 버튼 클릭 시 해당 인덱스의 스택 위젯 페이지로 이동
        btn.clicked.connect(lambda _, idx=index: self.main_stack.setCurrentIndex(idx))
        return btn

    # ==========================================
    # [화면 1] 홈 페이지 구성 (예정 목록 + 구동 기록)
    # ==========================================
    def create_home_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(50, 40, 50, 40)
        layout.setSpacing(20)

        # 페이지 최상단 타이틀
        top_layout = QHBoxLayout()
        lbl_title = QLabel("대시보드 (홈)")
        lbl_title.setProperty("class", "PageTitle")
        top_layout.addWidget(lbl_title)
        top_layout.addStretch()
        layout.addLayout(top_layout)

        # 1. 작업 예정 목록 (상단)
        lbl_sched = QLabel("작업 예정 목록")
        lbl_sched.setProperty("class", "SectionTitle")
        layout.addWidget(lbl_sched)

        self.list_schedule = QListWidget()
        self.list_schedule.addItem(" [대기중] '유나우랩 철거' 캠페인 - 티스토리 계정 1")
        self.list_schedule.addItem(" [대기중] '유나우랩 철거' 캠페인 - 티스토리 계정 2")
        layout.addWidget(self.list_schedule, 1) # 비율 1

        # 2. 구동 기록 (하단)
        lbl_log = QLabel("구동 기록 (로그)")
        lbl_log.setProperty("class", "SectionTitle")
        layout.addWidget(lbl_log)

        self.table_log = QTableWidget()
        self.table_log.setColumnCount(3)
        self.table_log.setHorizontalHeaderLabels(["시간", "작업명", "상태"])
        self.table_log.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_log.verticalHeader().setVisible(False)
        self.table_log.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # 샘플 데이터
        self.table_log.setRowCount(2)
        self.table_log.setItem(0, 0, QTableWidgetItem("15:30:21"))
        self.table_log.setItem(0, 1, QTableWidgetItem("'맛집 추천' 캠페인 이미지 생성 완료"))
        self.table_log.setItem(0, 2, QTableWidgetItem("성공"))
        
        self.table_log.setItem(1, 0, QTableWidgetItem("15:35:00"))
        self.table_log.setItem(1, 1, QTableWidgetItem("티스토리 포스팅 업로드"))
        self.table_log.setItem(1, 2, QTableWidgetItem("진행중"))
        
        layout.addWidget(self.table_log, 1) # 비율 1

        return page

    # ==========================================
    # 빈 페이지 생성 헬퍼 함수 (캠페인, 계정, 설정용)
    # ==========================================
    def create_placeholder_page(self, title_text, desc_text):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(50, 40, 50, 40)
        
        # 헤더
        top_layout = QHBoxLayout()
        lbl_title = QLabel(title_text)
        lbl_title.setProperty("class", "PageTitle")
        top_layout.addWidget(lbl_title)
        top_layout.addStretch()
        
        # 액션 버튼 (오른쪽 위)
        btn_action = QPushButton(f"{title_text} 저장하기")
        btn_action.setProperty("class", "ActionBtn")
        top_layout.addWidget(btn_action)
        
        layout.addLayout(top_layout)
        
        # 설명
        lbl_desc = QLabel(desc_text)
        lbl_desc.setStyleSheet("color: #666666; font-size: 12pt; margin-top: 10px;")
        layout.addWidget(lbl_desc)
        
        # 가운데 빈 영역
        empty_frame = QFrame()
        empty_frame.setStyleSheet("background-color: #F8F9FA; border: 1px dashed #DDDDDD; border-radius: 8px;")
        layout.addWidget(empty_frame, 1)
        
        return page

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # OS 기본 스타일에 구애받지 않도록 퓨전 스타일 적용
    app.setStyle('Fusion') 
    
    window = ModernDashboardApp()
    window.show()
    sys.exit(app.exec_())