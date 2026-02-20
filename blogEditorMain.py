# -*- coding: utf-8 -*-
import sys
import os
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QWidget, QHBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets

# 위에서 작성한 UI 모듈과 커스텀 위젯들을 임포트
from view.main_Ui import Ui_MainWindow, CampaignCard, ImageDropZone

# ==========================================
# JSON 데이터 관리
# ==========================================
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
# 메인 윈도우 로직 컨트롤러
# ==========================================
class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # UI 세팅 실행 (main_Ui.py)
        
        # 데이터 관리 초기화
        self.camp_mgr = DataManager('campaign.json')
        self.acc_mgr = DataManager('account.json')
        self.current_camp = {}
        self.dropzones = [] # 이미지 업로더 객체 추적용

        # 이벤트 및 초기 데이터 연동
        self.connect_events()
        self.refresh_campaign_list()

    def connect_events(self):
        """UI 컴포넌트의 클릭, 텍스트 변경 이벤트들을 로직에 연결합니다."""
        
        # 1. 사이드바 메뉴 탭 전환
        self.btn_home.clicked.connect(lambda: self.main_stack.setCurrentIndex(0))
        self.btn_campaign.clicked.connect(lambda: self.main_stack.setCurrentIndex(1))
        self.btn_account.clicked.connect(lambda: self.main_stack.setCurrentIndex(2))
        self.btn_settings.clicked.connect(lambda: self.main_stack.setCurrentIndex(3))

        # 2. 메인/기타 버튼들
        self.btn_add_schedule.clicked.connect(lambda: QMessageBox.information(self, "안내", "예정 목록 추가 창"))
        self.btn_add_camp.clicked.connect(self.start_wizard_new)
        self.btn_back.clicked.connect(lambda: self.camp_stack.setCurrentIndex(0))

        # 3. 위저드 네비게이션
        self.btn_next1.clicked.connect(self.go_next)
        self.btn_prev2.clicked.connect(self.go_prev)
        self.btn_next2.clicked.connect(self.go_next)
        self.btn_prev3.clicked.connect(self.go_prev)
        self.btn_next3.clicked.connect(self.go_next)
        self.btn_prev4.clicked.connect(self.go_prev)
        self.btn_save_camp.clicked.connect(self.save_campaign)

        # 4. 위저드 블록 제어
        self.btn_add_blk.clicked.connect(self.add_block_to_list)
        self.btn_add_dummy.clicked.connect(lambda: self.add_block_to_list(is_dummy=True))

        # 5. 위저드 우측 트래커 (실시간 텍스트 반영)
        self.e_name.textChanged.connect(lambda t: self.lbl_trk_name.setText(t if t else "입력 대기중"))
        self.e_base.textChanged.connect(lambda t: self.lbl_trk_base.setText(t if t else "입력 대기중"))
        self.btn_wel.toggled.connect(self.update_tracker_options)
        self.btn_end.toggled.connect(self.update_tracker_options)

    # --------------------------------------------------------
    # 위저드 화면 제어 로직 (스킵/분기 처리)
    # --------------------------------------------------------
    def update_tracker_options(self):
        res = []
        if self.btn_wel.isChecked(): res.append("서론O")
        if self.btn_end.isChecked(): res.append("결론O")
        self.lbl_trk_welcome.setText(", ".join(res) if res else "미사용 (3단계 직행)")

    def go_next(self):
        curr = self.step_stack.currentIndex()
        if curr == 0:
            if self.btn_wel.isChecked() or self.btn_end.isChecked():
                self.step_stack.setCurrentIndex(1)
                self.lbl_step.setText("STEP 2 OF 4"); self.lbl_wiz_title.setText("서론 / 결론 설정")
            else:
                self.step_stack.setCurrentIndex(2) # Step 2 스킵
                self.lbl_step.setText("STEP 3 OF 4"); self.lbl_wiz_title.setText("콘텐츠 블록 설정")
        elif curr == 1:
            self.step_stack.setCurrentIndex(2)
            self.lbl_step.setText("STEP 3 OF 4"); self.lbl_wiz_title.setText("콘텐츠 블록 설정")
        elif curr == 2:
            self.prepare_step4() # 이미지 업로드 뷰 동적 생성
            self.step_stack.setCurrentIndex(3)
            self.lbl_step.setText("STEP 4 OF 4"); self.lbl_wiz_title.setText("이미지 리소스 업로드")

    def go_prev(self):
        curr = self.step_stack.currentIndex()
        if curr == 3:
            self.step_stack.setCurrentIndex(2)
            self.lbl_step.setText("STEP 3 OF 4"); self.lbl_wiz_title.setText("콘텐츠 블록 설정")
        elif curr == 2:
            if self.btn_wel.isChecked() or self.btn_end.isChecked():
                self.step_stack.setCurrentIndex(1)
                self.lbl_step.setText("STEP 2 OF 4"); self.lbl_wiz_title.setText("서론 / 결론 설정")
            else:
                self.step_stack.setCurrentIndex(0)
                self.lbl_step.setText("STEP 1 OF 4"); self.lbl_wiz_title.setText("캠페인 기본 설정")
        elif curr == 1:
            self.step_stack.setCurrentIndex(0)
            self.lbl_step.setText("STEP 1 OF 4"); self.lbl_wiz_title.setText("캠페인 기본 설정")

    # --------------------------------------------------------
    # 캠페인 관리 핵심 로직
    # --------------------------------------------------------
    def start_wizard_new(self):
        """새 캠페인 작성 모드 진입"""
        self.current_camp = {}
        self.e_name.clear(); self.e_base.clear(); self.e_tags.clear()
        self.btn_wel.setChecked(False); self.btn_end.setChecked(False)
        self.list_blocks.clear()
        
        self.step_stack.setCurrentIndex(0)
        self.lbl_step.setText("STEP 1 OF 4"); self.lbl_wiz_title.setText("캠페인 기본 설정")
        self.camp_stack.setCurrentIndex(1)

    def start_wizard_edit(self, camp_data):
        """기존 캠페인 수정 모드 진입"""
        self.current_camp = camp_data
        self.e_name.setText(camp_data.get('name', ''))
        self.e_base.setText(camp_data.get('baseTitle', ''))
        self.e_tags.setText(",".join(camp_data.get('hashTags', [])))
        self.btn_wel.setChecked(camp_data.get('usingWelcomeContent', False))
        self.btn_end.setChecked(camp_data.get('usingEndingContent', False))
        
        self.list_blocks.clear()
        for b in camp_data.get('content', []):
            self.cb_btype.setCurrentText(b['type'])
            self.add_block_to_list()

        self.step_stack.setCurrentIndex(0)
        self.camp_stack.setCurrentIndex(1)

    def delete_campaign(self, name):
        """캠페인 삭제 로직"""
        reply = QMessageBox.question(self, '삭제 확인', f"'{name}' 캠페인을 삭제하시겠습니까?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.camp_mgr.data = [c for c in self.camp_mgr.data if c.get('name') != name]
            self.camp_mgr.save()
            self.refresh_campaign_list()

    def refresh_campaign_list(self):
        """카드 뷰 리스트 갱신"""
        self.list_camp_cards.clear()
        for c in self.camp_mgr.data:
            item = QListWidgetItem()
            item.setSizeHint(QtCore.QSize(300, 180))
            
            card = CampaignCard(c)
            # 커스텀 시그널을 이벤트 함수로 연결
            card.edit_clicked.connect(self.start_wizard_edit)
            card.delete_clicked.connect(self.delete_campaign)
            
            self.list_camp_cards.addItem(item)
            self.list_camp_cards.setItemWidget(item, card)

    # --------------------------------------------------------
    # 데이터 (블록/이미지/저장) 연산 로직
    # --------------------------------------------------------
    def add_block_to_list(self, is_dummy=False):
        btype = "image" if is_dummy else self.cb_btype.currentText()
        item = QListWidgetItem()
        item.setSizeHint(QtCore.QSize(0, 60))
        
        # 기획안 JSON 규격 세팅
        data = {"type": btype, "resources": [], "links": {"isUsing": False, "url": ""}}
        if btype == "subjectContent":
            data.update({"subject": "제목 입력", "subjectGenerate": True, "size": 900, "contentGenerate": True, "usingSubject": True})
        else:
            data.update({
                "subject": {"isUsing": (btype != "hiddenImage"), "text": "업체소개", "isGenerate": False, "size": 500 if btype != "hiddenImage" else 0},
                "content": {"isUsing": (btype != "hiddenImage"), "text": "", "isGenerate": (btype != "hiddenImage"), "size": 800 if btype != "hiddenImage" else 0}
            })

        item.setData(Qt.UserRole, data)
        
        # 블록 표시용 UI 
        w = QWidget(); l = QHBoxLayout(w); l.setContentsMargins(10,5,10,5)
        l.addWidget(QLabel(f"🗂️ [{btype}] 블록"))
        btn_del = QPushButton("❌"); btn_del.setStyleSheet("border:none;")
        btn_del.clicked.connect(lambda: self.list_blocks.takeItem(self.list_blocks.row(item)))
        l.addStretch(); l.addWidget(btn_del)
        
        self.list_blocks.addItem(item)
        self.list_blocks.setItemWidget(item, w)

    def prepare_step4(self):
        """블록 리스트를 읽어 이미지 첨부용 뷰 생성"""
        for i in reversed(range(self.img_layout.count())): 
            self.img_layout.itemAt(i).widget().setParent(None)

        row, col = 0, 0
        self.dropzones = [] 
        
        for i in range(self.list_blocks.count()):
            data = self.list_blocks.item(i).data(Qt.UserRole)
            if data['type'] in ['image', 'hiddenImage']:
                v_box = QVBoxLayout()
                v_box.addWidget(QLabel(f"Block #{i+1} [{data['type']}]"))
                dropzone = ImageDropZone(block_idx=i)
                self.dropzones.append(dropzone)
                v_box.addWidget(dropzone)
                
                self.img_layout.addLayout(v_box, row, col)
                col += 1
                if col > 3: # 4열 그리드 유지
                    col = 0; row += 1

    def save_campaign(self):
        """최종 JSON 데이터 조합 후 저장"""
        content_arr = []
        for i in range(self.list_blocks.count()):
            content_arr.append(self.list_blocks.item(i).data(Qt.UserRole))
            
        # Step 4의 이미지 매핑
        for dz in self.dropzones:
            if dz.file_path:
                content_arr[dz.block_idx]["resources"] = [dz.file_path]

        new_data = {
            "name": self.e_name.text(),
            "baseTitle": self.e_base.text(),
            "usingTitleGenerate": self.chk_tgen.isChecked(),
            "usingWelcomeContent": self.btn_wel.isChecked(),
            "usingEndingContent": self.btn_end.isChecked(),
            "hashTags": [t.strip() for t in self.e_tags.text().split(",")],
            "welcome": {"size": self.sp_wel.value(), "generate": self.chk_wgen.isChecked()},
            "ending": {"size": self.sp_end.value(), "generate": self.chk_egen.isChecked()},
            "content": content_arr
        }

        old_name = self.current_camp.get('name')
        if old_name: # 기존 데이터 덮어쓰기
            for idx, c in enumerate(self.camp_mgr.data):
                if c.get('name') == old_name:
                    self.camp_mgr.data[idx] = new_data
                    break
        else: # 신규 추가
            self.camp_mgr.data.append(new_data)
            
        self.camp_mgr.save()
        self.refresh_campaign_list()
        self.camp_stack.setCurrentIndex(0) 
        QMessageBox.information(self, "저장 완료", "캠페인이 성공적으로 저장되었습니다.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())