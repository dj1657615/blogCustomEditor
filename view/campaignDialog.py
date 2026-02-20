from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

class CampaignDialog(QDialog):
    def __init__(self, campaign_manager, parent=None):
        super().__init__(parent)
        self.manager = campaign_manager
        self.setWindowTitle("캠페인 설정 관리")
        self.resize(600, 700)
        self.setup_ui()
        self.refresh_campaign_list()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # 1. 상단: 캠페인 선택 및 로드
        top_layout = QHBoxLayout()
        self.combo_campaigns = QComboBox()
        self.btn_load = QPushButton("불러오기")
        self.btn_delete = QPushButton("삭제")
        
        top_layout.addWidget(QLabel("캠페인 선택:"))
        top_layout.addWidget(self.combo_campaigns)
        top_layout.addWidget(self.btn_load)
        top_layout.addWidget(self.btn_delete)
        layout.addLayout(top_layout)

        layout.addWidget(self.create_line())

        # 2. 폼 영역: 기본 설정
        form_layout = QFormLayout()
        
        self.edit_name = QLineEdit()
        self.edit_base_title = QLineEdit()
        self.edit_hashtags = QLineEdit()
        self.edit_hashtags.setPlaceholderText("콤마(,)로 구분 (예: 맛집,철거,추천)")
        
        self.chk_title_gen = QCheckBox("타이틀 자동 생성 (usingTitleGenerate)")
        self.chk_welcome = QCheckBox("인사말 사용 (usingWelcomeContent)")
        self.chk_ending = QCheckBox("맺음말 사용 (usingEndingContent)")

        form_layout.addRow("캠페인 이름(name):", self.edit_name)
        form_layout.addRow("기본 타이틀(baseTitle):", self.edit_base_title)
        form_layout.addRow("해시태그(hashTags):", self.edit_hashtags)
        
        chk_layout = QVBoxLayout()
        chk_layout.addWidget(self.chk_title_gen)
        chk_layout.addWidget(self.chk_welcome)
        chk_layout.addWidget(self.chk_ending)
        form_layout.addRow("옵션 설정:", chk_layout)
        
        layout.addLayout(form_layout)

        # 3. 추가 콘텐츠 배열 영역 (Content List)
        # 이 부분은 JSON의 "content" 배열을 관리하는 리스트 위젯입니다.
        layout.addWidget(QLabel("콘텐츠 블록 관리 (content):"))
        self.list_contents = QListWidget()
        layout.addWidget(self.list_contents)

        # 4. 하단 버튼
        bottom_layout = QHBoxLayout()
        self.btn_save = QPushButton("현재 설정 저장")
        self.btn_save.setStyleSheet("background-color: #020202; color: white; height: 40px; font-weight: bold;")
        self.btn_close = QPushButton("닫기")
        
        bottom_layout.addWidget(self.btn_save)
        bottom_layout.addWidget(self.btn_close)
        layout.addLayout(bottom_layout)

        # 이벤트 연결
        self.btn_save.clicked.connect(self.save_current_campaign)
        self.btn_load.clicked.connect(self.load_selected_campaign)
        self.btn_delete.clicked.connect(self.delete_selected_campaign)
        self.btn_close.clicked.connect(self.close)

    def create_line(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        return line

    def refresh_campaign_list(self):
        self.combo_campaigns.clear()
        for camp in self.manager.campaigns:
            self.combo_campaigns.addItem(camp.get("name", "Unknown"))

    def load_selected_campaign(self):
        name = self.combo_campaigns.currentText()
        if not name: return
        
        camp = self.manager.get_campaign_by_name(name)
        if camp:
            self.edit_name.setText(camp.get("name", ""))
            self.edit_base_title.setText(camp.get("baseTitle", ""))
            self.edit_hashtags.setText(",".join(camp.get("hashTags", [])))
            
            self.chk_title_gen.setChecked(camp.get("usingTitleGenerate", False))
            self.chk_welcome.setChecked(camp.get("usingWelcomeContent", False))
            self.chk_ending.setChecked(camp.get("usingEndingContent", False))

            # Content 리스트 갱신
            self.list_contents.clear()
            for content in camp.get("content", []):
                self.list_contents.addItem(f"[{content.get('type')}] - {content.get('subject', {}).get('text', '제목없음')}")

    def save_current_campaign(self):
        name = self.edit_name.text().strip()
        if not name:
            QMessageBox.warning(self, "경고", "캠페인 이름을 입력해주세요.")
            return

        # UI 데이터를 JSON 규격에 맞게 딕셔너리로 변환
        hashtags = [tag.strip() for tag in self.edit_hashtags.text().split(",") if tag.strip()]
        
        # 기존 캠페인 데이터를 가져오거나 새로 생성
        existing_camp = self.manager.get_campaign_by_name(name) or {}
        
        campaign_data = {
            "name": name,
            "baseTitle": self.edit_base_title.text(),
            "usingTitleGenerate": self.chk_title_gen.isChecked(),
            "usingWelcomeContent": self.chk_welcome.isChecked(),
            "usingEndingContent": self.chk_ending.isChecked(),
            "hashTags": hashtags,
            
            # 아래 딕셔너리와 컨텐츠 리스트는 기존 데이터를 유지하거나 디폴트값 셋팅
            "welcome": existing_camp.get("welcome", {"size": 400, "generate": True}),
            "ending": existing_camp.get("ending", {"size": 350, "generate": True}),
            "content": existing_camp.get("content", []) 
        }

        # 매니저를 통해 저장
        self.manager.update_campaign(campaign_data)
        QMessageBox.information(self, "완료", f"'{name}' 캠페인이 저장되었습니다.")
        self.refresh_campaign_list()
        
    def delete_selected_campaign(self):
        name = self.combo_campaigns.currentText()
        if name:
            self.manager.delete_campaign(name)
            self.refresh_campaign_list()
            QMessageBox.information(self, "완료", "삭제되었습니다.")