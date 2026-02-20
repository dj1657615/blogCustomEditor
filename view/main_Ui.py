# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPixmap

# ==========================================
# 모던 스타일 시트 (QSS)
# 사이드바 배경을 살짝 파란빛이 도는 다크 네이비(#0F172A)로 변경
# ==========================================
MODERN_STYLE = """
QWidget { font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif; }

/* 사이드바 (파란빛이 섞인 검정/네이비 톤) */
QFrame#SideBar { background-color: #0F172A; }
QLabel#LogoTitle { color: #FFFFFF; font-size: 18pt; font-weight: 900; }
QLabel#LogoSub { color: #94A3B8; font-size: 10pt; }

QPushButton.MenuButton {
    text-align: left; padding-left: 20px; font-size: 12pt; font-weight: bold;
    color: #94A3B8; background-color: transparent; border-radius: 8px; height: 50px;
}
QPushButton.MenuButton:hover { background-color: #1E293B; color: #FFFFFF; }
QPushButton.MenuButton:checked { background-color: #FFFFFF; color: #0F172A; }

QFrame#StatusBox { background-color: #1E293B; border-radius: 8px; }
QLabel#StatusTitle { color: #94A3B8; font-size: 9pt; }
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

/* 위저드 토글 버튼 */
QPushButton.ToggleBtn {
    background-color: #F5F6F8; color: #555555; font-weight: bold; font-size: 11pt; border-radius: 20px; padding: 10px; border: none;
}
QPushButton.ToggleBtn:checked {
    background-color: #111111; color: #FFFFFF; 
}

/* 플랜 트래커 패널 */
QFrame#TrackerPanel { background-color: #FFFFFF; border: 1px solid #E0E2E7; border-radius: 12px; }
QLabel.TrackerHeader { color: #111111; font-weight: 900; font-size: 12pt; }
QLabel.TrackerLabel { color: #888888; font-size: 9pt; margin-top: 8px; }
QLabel.TrackerValue { color: #333333; font-size: 11pt; font-weight: bold; background-color: #F8F9FA; border-radius: 6px; padding: 8px; border: 1px solid #F0F0F0;}
"""

# ==========================================
# 커스텀 위젯 1: 드래그 앤 드롭 이미지 업로더
# ==========================================
class ImageDropZone(QFrame):
    def __init__(self, block_idx, parent=None):
        super().__init__(parent)
        self.block_idx = block_idx
        self.file_path = ""
        self.setAcceptDrops(True)
        self.setFixedSize(150, 150)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QFrame { border: 2px dashed #CCCCCC; border-radius: 10px; background-color: #FAFAFA; }
            QFrame:hover { background-color: #F0F0F0; border-color: #888888; }
            QLabel { border: none; background: transparent; color: #888888; }
        """)
        self.layout = QVBoxLayout(self)
        self.lbl_icon = QLabel("📁\n이미지 첨부")
        self.lbl_icon.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.lbl_icon)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
            self.setStyleSheet("QFrame { border: 2px dashed #4B4EFC; background-color: #E8E8FF; border-radius: 10px; }")
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.setStyleSheet("QFrame { border: 2px dashed #CCCCCC; border-radius: 10px; background-color: #FAFAFA; } QFrame:hover { background-color: #F0F0F0; border-color: #888888; }")

    def dropEvent(self, event):
        self.dragLeaveEvent(event)
        urls = event.mimeData().urls()
        if urls:
            self.set_image(urls[0].toLocalFile())

    def mousePressEvent(self, event):
        file_path, _ = QFileDialog.getOpenFileName(self, "이미지 선택", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.set_image(file_path)

    def set_image(self, path):
        self.file_path = path
        pixmap = QPixmap(path).scaled(140, 140, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.lbl_icon.setPixmap(pixmap)

# ==========================================
# 커스텀 위젯 2: 캠페인 카드 (Hover 오버레이 포함)
# ==========================================
class CampaignCard(QFrame):
    edit_clicked = pyqtSignal(dict)
    delete_clicked = pyqtSignal(str)

    def __init__(self, camp_data, parent=None):
        super().__init__(parent)
        self.camp_data = camp_data
        self.name = camp_data.get("name", "제목 없음")
        
        self.setFixedSize(300, 180)
        self.setStyleSheet("""
            QFrame#BaseCard { background-color: #FFFFFF; border: 1px solid #E0E2E7; border-radius: 12px; }
            QFrame#BaseCard:hover { border: 1px solid #4B4EFC; }
        """)
        self.setObjectName("BaseCard")

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        lbl_name = QLabel(self.name)
        lbl_name.setStyleSheet("font-size: 14pt; font-weight: bold; border: none;")
        layout.addWidget(lbl_name)

        lbl_base = QLabel(f"{camp_data.get('baseTitle', '')}")
        lbl_base.setStyleSheet("font-size: 10pt; color: #888888; border: none;")
        layout.addWidget(lbl_base)
        layout.addStretch()

        tags = camp_data.get("hashTags", [])
        lbl_tags = QLabel(" ".join([f"#{t}" for t in tags[:3]]))
        lbl_tags.setStyleSheet("font-size: 10pt; color: #4B4EFC; border: none;")
        layout.addWidget(lbl_tags)

        # Hover 오버레이 영역
        self.overlay = QFrame(self)
        self.overlay.setFixedSize(300, 180)
        self.overlay.setStyleSheet("background-color: rgba(255, 255, 255, 0.85); border-radius: 12px;")
        
        ov_layout = QHBoxLayout(self.overlay)
        btn_edit = QPushButton("✏️ 수정")
        btn_edit.setCursor(Qt.PointingHandCursor)
        btn_edit.setStyleSheet("background-color: #111; color: white; border-radius: 6px; padding: 8px;")
        btn_edit.clicked.connect(lambda: self.edit_clicked.emit(self.camp_data))

        btn_del = QPushButton("🗑️ 삭제")
        btn_del.setCursor(Qt.PointingHandCursor)
        btn_del.setStyleSheet("background-color: #FF4D4D; color: white; border-radius: 6px; padding: 8px;")
        btn_del.clicked.connect(lambda: self.delete_clicked.emit(self.name))

        ov_layout.addWidget(btn_edit)
        ov_layout.addWidget(btn_del)
        self.overlay.hide()

    def enterEvent(self, event):
        self.overlay.show()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.overlay.hide()
        super().leaveEvent(event)

# ==========================================
# UI Main 구조 정의 클래스
# ==========================================
class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1600, 900)
        MainWindow.setStyleSheet(MODERN_STYLE)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        MainWindow.setCentralWidget(self.centralwidget)

        self.main_layout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # ---------------------------------------------------------
        # 1. 사이드바 구성
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


        self.main_layout.addWidget(self.sidebar)

        # ---------------------------------------------------------
        # 2. 메인 영역 스택 위젯
        # ---------------------------------------------------------
        self.main_stack = QtWidgets.QStackedWidget(self.centralwidget)
        self.main_stack.setObjectName("MainArea")
        self.main_layout.addWidget(self.main_stack)

        self.setupHomeUI()
        self.setupCampaignUI()
        self.setupAccountUI()
        self.setupSettingsUI()

    def create_menu_btn(self, text, index):
        btn = QtWidgets.QPushButton(text)
        btn.setProperty("class", "MenuButton")
        btn.setCheckable(True)
        self.menu_btn_group.addButton(btn, index)
        return btn

    def setupHomeUI(self):
        self.page_home = QtWidgets.QWidget()
        self.layout_home = QtWidgets.QVBoxLayout(self.page_home)
        self.layout_home.setContentsMargins(50, 40, 50, 40)
        self.layout_home.setSpacing(20)
        
        lbl_home_title = QtWidgets.QLabel("대시보드")
        lbl_home_title.setProperty("class", "PageTitle")
        self.layout_home.addWidget(lbl_home_title)

        # 예정 목록 상단 (버튼 추가용 HBox)
        sched_top = QHBoxLayout()
        lbl_sched = QtWidgets.QLabel("작업 예정 목록")
        lbl_sched.setProperty("class", "SectionTitle")
        self.btn_add_schedule = QPushButton("+ 예정 목록에 추가")
        self.btn_add_schedule.setProperty("class", "ActionBtn")
        sched_top.addWidget(lbl_sched)
        sched_top.addStretch()
        sched_top.addWidget(self.btn_add_schedule)
        self.layout_home.addLayout(sched_top)

        self.list_schedule = QtWidgets.QListWidget()
        self.list_schedule.setStyleSheet("background-color: white; border: 1px solid #E5E5E5; border-radius: 8px;")
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

    def setupCampaignUI(self):
        self.page_campaign = QtWidgets.QWidget()
        self.layout_campaign = QtWidgets.QVBoxLayout(self.page_campaign)
        self.layout_campaign.setContentsMargins(0, 0, 0, 0)
        
        self.camp_stack = QStackedWidget()
        self.layout_campaign.addWidget(self.camp_stack)

        # [뷰 1] 리스트 뷰
        self.view_list = QWidget()
        list_layout = QVBoxLayout(self.view_list)
        list_layout.setContentsMargins(50, 40, 50, 40)
        
        top_layout = QHBoxLayout()
        lbl_camp_title = QLabel("캠페인 관리")
        lbl_camp_title.setProperty("class", "PageTitle")
        self.btn_add_camp = QPushButton("+ 새 캠페인 생성")
        self.btn_add_camp.setProperty("class", "ActionBtn")
        
        top_layout.addWidget(lbl_camp_title)
        top_layout.addStretch()
        top_layout.addWidget(self.btn_add_camp)
        list_layout.addLayout(top_layout)

        self.list_camp_cards = QListWidget()
        self.list_camp_cards.setViewMode(QListWidget.IconMode)
        self.list_camp_cards.setResizeMode(QListWidget.Adjust)
        self.list_camp_cards.setSpacing(20)
        self.list_camp_cards.setMovement(QListWidget.Static)
        list_layout.addWidget(self.list_camp_cards)
        self.camp_stack.addWidget(self.view_list)

        # [뷰 2] 위저드 뷰
        self.view_wizard = QWidget()
        wizard_main_layout = QHBoxLayout(self.view_wizard)
        wizard_main_layout.setContentsMargins(30, 30, 30, 30)
        wizard_main_layout.setSpacing(20)

        back_layout = QVBoxLayout()
        self.btn_back = QPushButton("← 목록으로")
        self.btn_back.setStyleSheet("border: none; font-weight: bold; font-size: 12pt; color: #555;")
        self.btn_back.setCursor(Qt.PointingHandCursor)
        back_layout.addWidget(self.btn_back)
        back_layout.addStretch()

        self.wizard_card = QFrame()
        self.wizard_card.setMinimumWidth(800)
        self.wizard_card.setStyleSheet("background-color: #FFFFFF; border-radius: 12px; border: 1px solid #EAEAEA;")
        self.wizard_layout = QVBoxLayout(self.wizard_card)
        self.wizard_layout.setContentsMargins(40, 40, 40, 40)
        
        self.lbl_step = QLabel("STEP 1 OF 4")
        self.lbl_step.setAlignment(Qt.AlignCenter)
        self.lbl_step.setStyleSheet("color: #888; font-weight: bold; border:none;")
        self.lbl_wiz_title = QLabel("캠페인 기본 설정")
        self.lbl_wiz_title.setAlignment(Qt.AlignCenter)
        self.lbl_wiz_title.setStyleSheet("font-size: 18pt; font-weight: 900; margin-bottom: 20px; border:none;")
        
        self.wizard_layout.addWidget(self.lbl_step)
        self.wizard_layout.addWidget(self.lbl_wiz_title)

        self.step_stack = QStackedWidget()
        self.build_wizard_steps()
        self.wizard_layout.addWidget(self.step_stack)

        # 트래커 패널
        self.tracker_panel = QFrame()
        self.tracker_panel.setObjectName("TrackerPanel")
        self.tracker_panel.setFixedWidth(280)
        tracker_layout = QVBoxLayout(self.tracker_panel)
        tracker_layout.setContentsMargins(25, 25, 25, 25)

        lbl_trk_head = QLabel("나의 플랜")
        lbl_trk_head.setProperty("class", "TrackerHeader")
        tracker_layout.addWidget(lbl_trk_head)
        tracker_layout.addSpacing(15)

        self.lbl_trk_name = self.create_tracker_item(tracker_layout, "캠페인명", "입력 대기중")
        self.lbl_trk_base = self.create_tracker_item(tracker_layout, "기본 제목", "입력 대기중")
        self.lbl_trk_welcome = self.create_tracker_item(tracker_layout, "서론/결론 사용", "선택 대기중")
        tracker_layout.addStretch()

        wizard_main_layout.addLayout(back_layout)
        wizard_main_layout.addWidget(self.wizard_card, stretch=1)
        wizard_main_layout.addWidget(self.tracker_panel)

        self.camp_stack.addWidget(self.view_wizard)
        self.main_stack.addWidget(self.page_campaign)

    def create_tracker_item(self, parent_layout, label_text, default_val):
        lbl = QLabel(label_text); lbl.setProperty("class", "TrackerLabel")
        val = QLabel(default_val); val.setProperty("class", "TrackerValue")
        parent_layout.addWidget(lbl); parent_layout.addWidget(val)
        return val

    def build_wizard_steps(self):
        # Step 1
        page1 = QWidget(); l1 = QVBoxLayout(page1); l1.setSpacing(15)
        self.e_name = QLineEdit(); self.e_name.setPlaceholderText("예: 유나우랩")
        self.e_base = QLineEdit(); self.e_base.setPlaceholderText("예: [지역명] 철거")
        self.e_tags = QLineEdit(); self.e_tags.setPlaceholderText("콤마 구분 (예: 맛집, 철거)")
        self.chk_tgen = QCheckBox("타이틀 자동 생성 사용"); self.chk_tgen.setChecked(True)

        l1.addWidget(QLabel("캠페인 이름")); l1.addWidget(self.e_name)
        l1.addWidget(QLabel("기본 타이틀")); l1.addWidget(self.e_base)
        l1.addWidget(QLabel("해시태그")); l1.addWidget(self.e_tags)
        l1.addWidget(self.chk_tgen)

        h_opt = QHBoxLayout()
        self.btn_wel = QPushButton("서론(Welcome) 사용"); self.btn_wel.setProperty("class", "ToggleBtn"); self.btn_wel.setCheckable(True)
        self.btn_end = QPushButton("결론(Ending) 사용"); self.btn_end.setProperty("class", "ToggleBtn"); self.btn_end.setCheckable(True)
        h_opt.addWidget(self.btn_wel); h_opt.addWidget(self.btn_end)
        l1.addWidget(QLabel("본문 구성 옵션")); l1.addLayout(h_opt)

        nav1 = QHBoxLayout(); nav1.addStretch()
        self.btn_next1 = QPushButton("다음 ➔"); self.btn_next1.setProperty("class", "ActionBtn")
        nav1.addWidget(self.btn_next1)
        l1.addStretch(); l1.addLayout(nav1)
        self.step_stack.addWidget(page1)

        # Step 2
        page2 = QWidget(); l2 = QFormLayout(page2); l2.setVerticalSpacing(20)
        self.sp_wel = QSpinBox(); self.sp_wel.setMaximum(5000); self.sp_wel.setValue(400)
        self.chk_wgen = QCheckBox("자동생성"); self.chk_wgen.setChecked(True)
        self.sp_end = QSpinBox(); self.sp_end.setMaximum(5000); self.sp_end.setValue(350)
        self.chk_egen = QCheckBox("자동생성"); self.chk_egen.setChecked(True)
        
        l2.addRow("Welcome Size:", self.sp_wel); l2.addRow("", self.chk_wgen)
        l2.addRow("Ending Size:", self.sp_end); l2.addRow("", self.chk_egen)

        nav2 = QHBoxLayout()
        self.btn_prev2 = QPushButton("← 이전"); self.btn_prev2.setProperty("class", "SecondaryBtn")
        self.btn_next2 = QPushButton("다음 ➔"); self.btn_next2.setProperty("class", "ActionBtn")
        nav2.addWidget(self.btn_prev2); nav2.addStretch(); nav2.addWidget(self.btn_next2)
        l2.addRow(nav2)
        self.step_stack.addWidget(page2)

        # Step 3
        page3 = QWidget(); l3 = QVBoxLayout(page3)
        l3.addWidget(QLabel("<b>콘텐츠 블록 추가</b>"))
        
        self.list_blocks = QListWidget()
        self.list_blocks.setDragDropMode(QAbstractItemView.InternalMove) 
        self.list_blocks.setStyleSheet("border: 1px solid #E0E2E7; border-radius: 8px;")
        l3.addWidget(self.list_blocks)

        add_layout = QHBoxLayout()
        self.cb_btype = QComboBox()
        self.cb_btype.addItems(["image", "hiddenImage", "subjectContent", "summary"])
        self.btn_add_blk = QPushButton("블록 추가"); self.btn_add_blk.setProperty("class", "SecondaryBtn")
        self.btn_add_dummy = QPushButton("+ 더미 테스트"); self.btn_add_dummy.setProperty("class", "SecondaryBtn")
        add_layout.addWidget(self.cb_btype); add_layout.addWidget(self.btn_add_blk); add_layout.addWidget(self.btn_add_dummy)
        l3.addLayout(add_layout)

        nav3 = QHBoxLayout()
        self.btn_prev3 = QPushButton("← 이전"); self.btn_prev3.setProperty("class", "SecondaryBtn")
        self.btn_next3 = QPushButton("이미지 업로드 단계로 ➔"); self.btn_next3.setProperty("class", "ActionBtn")
        nav3.addWidget(self.btn_prev3); nav3.addStretch(); nav3.addWidget(self.btn_next3)
        l3.addLayout(nav3)
        self.step_stack.addWidget(page3)

        # Step 4
        self.page4 = QWidget(); self.l4 = QVBoxLayout(self.page4)
        self.l4.addWidget(QLabel("<b>블록별 이미지 업로드</b> (클릭 또는 드래그)"))
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: transparent;")
        self.img_container = QWidget()
        self.img_layout = QGridLayout(self.img_container)
        scroll.setWidget(self.img_container)
        self.l4.addWidget(scroll)

        nav4 = QHBoxLayout()
        self.btn_prev4 = QPushButton("← 이전"); self.btn_prev4.setProperty("class", "SecondaryBtn")
        self.btn_save_camp = QPushButton("캠페인 저장 완료 ✔"); self.btn_save_camp.setProperty("class", "ActionBtn")
        nav4.addWidget(self.btn_prev4); nav4.addStretch(); nav4.addWidget(self.btn_save_camp)
        self.l4.addLayout(nav4)
        self.step_stack.addWidget(self.page4)

    def setupAccountUI(self):
        self.page_account = QtWidgets.QWidget()
        self.layout_account = QtWidgets.QVBoxLayout(self.page_account)
        self.layout_account.setContentsMargins(50, 40, 50, 40)
        lbl = QLabel("계정 관리"); lbl.setProperty("class", "PageTitle")
        self.layout_account.addWidget(lbl)
        self.layout_account.addStretch()
        self.main_stack.addWidget(self.page_account)

    def setupSettingsUI(self):
        self.page_settings = QtWidgets.QWidget()
        self.layout_settings = QtWidgets.QVBoxLayout(self.page_settings)
        self.layout_settings.setContentsMargins(50, 40, 50, 40)
        lbl = QLabel("프로그램 설정"); lbl.setProperty("class", "PageTitle")
        self.layout_settings.addWidget(lbl)
        self.layout_settings.addStretch()
        self.main_stack.addWidget(self.page_settings)