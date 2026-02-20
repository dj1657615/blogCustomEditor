# -*- coding: utf-8 -*-
import sys
import os
import json
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QColor

from view import main_Ui

# JSON 매니저
class DataManager:
    def __init__(self, filepath, default_data=[]):
        self.filepath = filepath
        self.data = default_data
        self.load()

    def load(self):
        if not os.path.exists(self.filepath):
            self.data = []
        else:
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except:
                self.data = []

    def save(self):
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

# ==========================================
# 커스텀 위젯: 캠페인 카드 (리스트 뷰용)
# ==========================================
class CampaignCard(QFrame):
    def __init__(self, camp_data, parent=None):
        super().__init__(parent)
        self.camp_data = camp_data
        self.setFixedSize(300, 180) # 카드 사이즈
        self.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #E0E2E7;
                border-radius: 12px;
            }
            QFrame:hover {
                border: 1px solid #4B4EFC;
            }
        """)
        
        # 그림자 효과
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 15))
        shadow.setOffset(0, 5)
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # 타이틀
        name = camp_data.get("name", "제목 없음")
        lbl_name = QLabel(name)
        lbl_name.setStyleSheet("font-size: 14pt; font-weight: bold; border: none;")
        layout.addWidget(lbl_name)

        # 서브 타이틀 (Base Title)
        base_title = camp_data.get("baseTitle", "")
        lbl_base = QLabel(f"기본제목: {base_title}")
        lbl_base.setStyleSheet("font-size: 10pt; color: #888888; border: none;")
        layout.addWidget(lbl_base)
        
        layout.addStretch()

        # 해시태그
        tags = camp_data.get("hashTags", [])
        tag_text = " ".join([f"#{t}" for t in tags[:3]]) # 3개만 표시
        if len(tags) > 3: tag_text += " ..."
        lbl_tags = QLabel(tag_text)
        lbl_tags.setStyleSheet("font-size: 10pt; color: #4B4EFC; border: none;")
        layout.addWidget(lbl_tags)


# ==========================================
# 메인 윈도우
# ==========================================
class MainWindow(QMainWindow, main_Ui.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        self.camp_mgr = DataManager('campaign.json')
        self.acc_mgr = DataManager('account.json')
        
        self.connect_menu_events()
        self.setup_campaign_page()
        self.setup_account_page()
        
        self.refresh_campaign_list()

    def connect_menu_events(self):
        self.btn_home.clicked.connect(lambda: self.main_stack.setCurrentIndex(0))
        self.btn_campaign.clicked.connect(lambda: self.main_stack.setCurrentIndex(1))
        self.btn_account.clicked.connect(lambda: self.main_stack.setCurrentIndex(2))
        self.btn_settings.clicked.connect(lambda: self.main_stack.setCurrentIndex(3))

    def setup_account_page(self):
        # 간단한 계정 관리 틀
        lbl_acc = QLabel("계정 관리")
        lbl_acc.setProperty("class", "PageTitle")
        self.layout_account.addWidget(lbl_acc)
        self.layout_account.addStretch()

    # ==========================================
    # 캠페인 관리 페이지 (리스트 뷰 vs 위저드 뷰)
    # ==========================================
    def setup_campaign_page(self):
        # 캠페인 내부 뷰 전환용 스택 위젯
        self.camp_stack = QStackedWidget()
        self.layout_campaign.addWidget(self.camp_stack)

        # ---- [뷰 1] 캠페인 리스트 모드 ----
        self.view_list = QWidget()
        list_layout = QVBoxLayout(self.view_list)
        list_layout.setContentsMargins(50, 40, 50, 40)
        
        top_layout = QHBoxLayout()
        lbl_camp_title = QLabel("캠페인 관리")
        lbl_camp_title.setProperty("class", "PageTitle")
        btn_add_camp = QPushButton("+ 새 캠페인 생성")
        btn_add_camp.setProperty("class", "ActionBtn")
        btn_add_camp.clicked.connect(self.show_campaign_wizard)
        
        top_layout.addWidget(lbl_camp_title)
        top_layout.addStretch()
        top_layout.addWidget(btn_add_camp)
        list_layout.addLayout(top_layout)
        list_layout.addSpacing(20)

        # 격자 형태(Grid/Flow) 리스트 위젯
        self.list_camp_cards = QListWidget()
        self.list_camp_cards.setViewMode(QListWidget.IconMode)
        self.list_camp_cards.setResizeMode(QListWidget.Adjust)
        self.list_camp_cards.setSpacing(20)
        self.list_camp_cards.setMovement(QListWidget.Static) # 드래그 금지
        list_layout.addWidget(self.list_camp_cards)
        self.camp_stack.addWidget(self.view_list)

        # ---- [뷰 2] 캠페인 위저드 모드 ----
        self.view_wizard = QWidget()
        wizard_main_layout = QHBoxLayout(self.view_wizard)
        wizard_main_layout.setContentsMargins(50, 40, 50, 40)
        wizard_main_layout.setSpacing(40)

        # 좌측 상단 뒤로가기 버튼
        back_layout = QVBoxLayout()
        btn_back = QPushButton("← 목록으로 돌아가기")
        btn_back.setStyleSheet("border: none; font-weight: bold; font-size: 12pt; color: #555;")
        btn_back.setCursor(Qt.PointingHandCursor)
        btn_back.clicked.connect(self.hide_campaign_wizard)
        back_layout.addWidget(btn_back)
        back_layout.addStretch()

        # 중앙 위저드 폼 카드 (첨부사진 느낌)
        self.wizard_card = QFrame()
        self.wizard_card.setFixedWidth(550)
        self.wizard_card.setStyleSheet("background-color: #FFFFFF; border-radius: 20px; border: 1px solid #EAEAEA;")
        card_shadow = QGraphicsDropShadowEffect()
        card_shadow.setBlurRadius(30)
        card_shadow.setColor(QColor(0, 0, 0, 15))
        card_shadow.setOffset(0, 10)
        self.wizard_card.setGraphicsEffect(card_shadow)
        
        self.wizard_layout = QVBoxLayout(self.wizard_card)
        self.wizard_layout.setContentsMargins(40, 40, 40, 40)
        
        self.lbl_step = QLabel("STEP 1 OF 3")
        self.lbl_step.setAlignment(Qt.AlignCenter)
        self.lbl_step.setStyleSheet("color: #888888; font-weight: bold; font-size: 10pt; letter-spacing: 1px; border: none;")
        self.lbl_wiz_title = QLabel("캠페인 기본 정보 설정")
        self.lbl_wiz_title.setAlignment(Qt.AlignCenter)
        self.lbl_wiz_title.setStyleSheet("font-size: 16pt; font-weight: 900; margin-top: 10px; margin-bottom: 30px; border: none;")
        
        self.wizard_layout.addWidget(self.lbl_step)
        self.wizard_layout.addWidget(self.lbl_wiz_title)

        # 위저드 내부 스텝 스택
        self.step_stack = QStackedWidget()
        self.setup_wizard_steps()
        self.wizard_layout.addWidget(self.step_stack)

        # 우측 트래커 (나의 플랜 요약) 패널
        self.tracker_panel = QFrame()
        self.tracker_panel.setObjectName("TrackerPanel")
        self.tracker_panel.setFixedWidth(280)
        tracker_layout = QVBoxLayout(self.tracker_panel)
        tracker_layout.setContentsMargins(25, 25, 25, 25)

        self.lbl_trk_name = self.add_tracker_item(tracker_layout, "캠페인명", "입력 대기중")
        self.lbl_trk_base = self.add_tracker_item(tracker_layout, "기본 제목", "입력 대기중")
        self.lbl_trk_welcome = self.add_tracker_item(tracker_layout, "서론/결론 사용", "선택 대기중")
        
        tracker_layout.addStretch()

        # 위저드 메인 레이아웃 조합
        wizard_main_layout.addLayout(back_layout)
        wizard_main_layout.addStretch()
        wizard_main_layout.addWidget(self.wizard_card)
        wizard_main_layout.addStretch()
        wizard_main_layout.addWidget(self.tracker_panel)

        self.camp_stack.addWidget(self.view_wizard)

    def add_tracker_item(self, parent_layout, label_text, default_val):
        """트래커 패널 내부에 라벨/값 추가"""
        lbl = QLabel(label_text)
        lbl.setProperty("class", "TrackerLabel")
        val = QLabel(default_val)
        val.setProperty("class", "TrackerValue")
        parent_layout.addWidget(lbl)
        parent_layout.addWidget(val)
        return val

    # ==========================================
    # 위저드 스텝 UI 구성
    # ==========================================
    def setup_wizard_steps(self):
        # --- [Step 1] 기본 정보 ---
        page1 = QWidget()
        layout1 = QVBoxLayout(page1)
        layout1.setSpacing(15)
        
        self.edit_camp_name = QLineEdit()
        self.edit_camp_name.setPlaceholderText("예: 유나우랩")
        self.edit_camp_name.textChanged.connect(lambda t: self.lbl_trk_name.setText(t if t else "입력 대기중"))
        
        self.edit_base_title = QLineEdit()
        self.edit_base_title.setPlaceholderText("예: [지역명] 철거")
        self.edit_base_title.textChanged.connect(lambda t: self.lbl_trk_base.setText(t if t else "입력 대기중"))
        
        self.edit_hashtags = QLineEdit()
        self.edit_hashtags.setPlaceholderText("콤마로 구분 (예: 맛집, 추천)")

        layout1.addWidget(QLabel("<b>캠페인 이름</b>"))
        layout1.addWidget(self.edit_camp_name)
        layout1.addWidget(QLabel("<b>기본 타이틀</b>"))
        layout1.addWidget(self.edit_base_title)
        layout1.addWidget(QLabel("<b>해시태그</b>"))
        layout1.addWidget(self.edit_hashtags)

        # 옵션 토글 버튼 (첨부이미지 스타일)
        opt_layout = QHBoxLayout()
        self.btn_opt_welcome = QPushButton("서론 사용")
        self.btn_opt_welcome.setProperty("class", "ToggleBtn"); self.btn_opt_welcome.setCheckable(True)
        self.btn_opt_ending = QPushButton("결론 사용")
        self.btn_opt_ending.setProperty("class", "ToggleBtn"); self.btn_opt_ending.setCheckable(True)
        
        # 트래커 연동용 함수
        def update_wel_end_tracker():
            res = []
            if self.btn_opt_welcome.isChecked(): res.append("서론O")
            if self.btn_opt_ending.isChecked(): res.append("결론O")
            self.lbl_trk_welcome.setText(", ".join(res) if res else "미사용 (3단계 직행)")
            
        self.btn_opt_welcome.toggled.connect(update_wel_end_tracker)
        self.btn_opt_ending.toggled.connect(update_wel_end_tracker)

        opt_layout.addWidget(self.btn_opt_welcome)
        opt_layout.addWidget(self.btn_opt_ending)
        layout1.addWidget(QLabel("<b>본문 구성 옵션</b>"))
        layout1.addLayout(opt_layout)

        # 네비게이션
        nav1 = QHBoxLayout()
        nav1.addStretch()
        btn_next1 = QPushButton("다음 ➔")
        btn_next1.setProperty("class", "ActionBtn")
        btn_next1.clicked.connect(self.go_next_step)
        nav1.addWidget(btn_next1)
        layout1.addStretch()
        layout1.addLayout(nav1)
        self.step_stack.addWidget(page1)

        # --- [Step 2] 서론/결론 상세 ---
        page2 = QWidget()
        layout2 = QVBoxLayout(page2)
        
        layout2.addWidget(QLabel("<b>서론 (Welcome) 글자수</b>"))
        self.spin_wel_size = QSpinBox(); self.spin_wel_size.setMaximum(5000); self.spin_wel_size.setValue(400)
        layout2.addWidget(self.spin_wel_size)
        
        layout2.addWidget(QLabel("<b>결론 (Ending) 글자수</b>"))
        self.spin_end_size = QSpinBox(); self.spin_end_size.setMaximum(5000); self.spin_end_size.setValue(350)
        layout2.addWidget(self.spin_end_size)

        nav2 = QHBoxLayout()
        btn_prev2 = QPushButton("이전")
        btn_prev2.setProperty("class", "SecondaryBtn")
        btn_prev2.clicked.connect(self.go_prev_step)
        btn_next2 = QPushButton("다음 ➔")
        btn_next2.setProperty("class", "ActionBtn")
        btn_next2.clicked.connect(self.go_next_step)
        nav2.addWidget(btn_prev2)
        nav2.addStretch()
        nav2.addWidget(btn_next2)
        
        layout2.addStretch()
        layout2.addLayout(nav2)
        self.step_stack.addWidget(page2)

        # --- [Step 3] 블록 설정 (간략화) ---
        page3 = QWidget()
        layout3 = QVBoxLayout(page3)
        layout3.addWidget(QLabel("<b>콘텐츠 블록 구성</b>"))
        layout3.addWidget(QLabel("여기서 블록을 추가하고 순서를 변경합니다.", styleSheet="color:#888; font-size:10pt;"))
        
        # 리스트 위젯 (드래그앤드롭)
        self.wiz_block_list = QListWidget()
        self.wiz_block_list.setDragDropMode(QAbstractItemView.InternalMove)
        self.wiz_block_list.setStyleSheet("border: 1px solid #E0E2E7; border-radius: 8px;")
        layout3.addWidget(self.wiz_block_list)

        btn_add_blk = QPushButton("+ 더미 블록 추가 (테스트)")
        btn_add_blk.setProperty("class", "SecondaryBtn")
        btn_add_blk.clicked.connect(lambda: self.wiz_block_list.addItem("블록: image (업체소개)"))
        layout3.addWidget(btn_add_blk)

        nav3 = QHBoxLayout()
        btn_prev3 = QPushButton("이전")
        btn_prev3.setProperty("class", "SecondaryBtn")
        btn_prev3.clicked.connect(self.go_prev_step)
        btn_finish = QPushButton("저장 및 완료 ✔")
        btn_finish.setProperty("class", "ActionBtn")
        btn_finish.clicked.connect(self.save_new_campaign)
        nav3.addWidget(btn_prev3)
        nav3.addStretch()
        nav3.addWidget(btn_finish)

        layout3.addStretch()
        layout3.addLayout(nav3)
        self.step_stack.addWidget(page3)

    # ==========================================
    # 위저드 동작 함수들
    # ==========================================
    def go_next_step(self):
        curr = self.step_stack.currentIndex()
        if curr == 0:
            if self.btn_opt_welcome.isChecked() or self.btn_opt_ending.isChecked():
                self.step_stack.setCurrentIndex(1)
                self.lbl_step.setText("STEP 2 OF 3")
                self.lbl_wiz_title.setText("서론 / 결론 글자수 설정")
            else:
                self.step_stack.setCurrentIndex(2)
                self.lbl_step.setText("STEP 3 OF 3")
                self.lbl_wiz_title.setText("콘텐츠 블록 셋팅")
        elif curr == 1:
            self.step_stack.setCurrentIndex(2)
            self.lbl_step.setText("STEP 3 OF 3")
            self.lbl_wiz_title.setText("콘텐츠 블록 셋팅")

    def go_prev_step(self):
        curr = self.step_stack.currentIndex()
        if curr == 2:
            if self.btn_opt_welcome.isChecked() or self.btn_opt_ending.isChecked():
                self.step_stack.setCurrentIndex(1)
                self.lbl_step.setText("STEP 2 OF 3")
                self.lbl_wiz_title.setText("서론 / 결론 글자수 설정")
            else:
                self.step_stack.setCurrentIndex(0)
                self.lbl_step.setText("STEP 1 OF 3")
                self.lbl_wiz_title.setText("캠페인 기본 정보 설정")
        elif curr == 1:
            self.step_stack.setCurrentIndex(0)
            self.lbl_step.setText("STEP 1 OF 3")
            self.lbl_wiz_title.setText("캠페인 기본 정보 설정")

    def show_campaign_wizard(self):
        # 폼 초기화
        self.edit_camp_name.clear(); self.edit_base_title.clear(); self.edit_hashtags.clear()
        self.btn_opt_welcome.setChecked(False); self.btn_opt_ending.setChecked(False)
        self.wiz_block_list.clear()
        self.step_stack.setCurrentIndex(0)
        self.lbl_step.setText("STEP 1 OF 3")
        self.lbl_wiz_title.setText("캠페인 기본 정보 설정")
        # 뷰 전환
        self.camp_stack.setCurrentIndex(1)

    def hide_campaign_wizard(self):
        self.camp_stack.setCurrentIndex(0)

    def save_new_campaign(self):
        camp_data = {
            "name": self.edit_camp_name.text(),
            "baseTitle": self.edit_base_title.text(),
            "usingWelcomeContent": self.btn_opt_welcome.isChecked(),
            "usingEndingContent": self.btn_opt_ending.isChecked(),
            "hashTags": [t.strip() for t in self.edit_hashtags.text().split(",")],
            "welcome": {"size": self.spin_wel_size.value()},
            "ending": {"size": self.spin_end_size.value()},
            "content": [] # 블록 리스트 데이터 변환 생략
        }
        self.camp_mgr.data.append(camp_data)
        self.camp_mgr.save()
        self.refresh_campaign_list()
        self.hide_campaign_wizard()

    def refresh_campaign_list(self):
        self.list_camp_cards.clear()
        for c in self.camp_mgr.data:
            item = QListWidgetItem()
            item.setSizeHint(QtCore.QSize(300, 180)) # CustomCard 사이즈와 동일하게 맞춤
            
            card_widget = CampaignCard(c)
            
            self.list_camp_cards.addItem(item)
            self.list_camp_cards.setItemWidget(item, card_widget)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())