# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import webbrowser
from datetime import datetime
import time
from view import login_Ui
from blogEditorMain import MainWindow
import sys
from caller import rest
from controller import ui_controller
from caller import chromeAutoUpdate
import socket
import traceback
import pyautogui
import os
from view import process_ui
from caller import rest

class Initializer(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    progressChanged = QtCore.pyqtSignal(int)

    def run(self):
        try:
            for i in range(1, 75):
                time.sleep(0.01)
                self.progressChanged.emit(i)
                
            chromeAutoUpdate.update()
            for i in range(75, 101):
                time.sleep(0.01)
                self.progressChanged.emit(i)
            time.sleep(0.1)
            
        except Exception as e:
            print("초기화 중 오류 발생:", e)
            self.showCustomMessageBox('프로그램 실행 오류', '프로그램 실행을 실패하였습니다') 
            sys.exit()
        finally:
            self.finished.emit()
            
    def showCustomMessageBox(self, title, message):
        icon_path = 'resource/trayIcon.png'
        msgBox = QtWidgets.QMessageBox()
        msgBox.setWindowTitle(title)
        msgBox.setWindowIcon(QtGui.QIcon(icon_path))
        msgBox.setText(f" \nㅤㅤ{message}ㅤㅤㅤ\n ")
        msgBox.exec_()
            
            
class ProcessWindow(QMainWindow, process_ui.Process_Ui):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('resource/icons/trayIcon.png'))
        self.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        
class Login(QMainWindow, login_Ui.Ui_LoginWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        
        login_Ui.Ui_LoginWindow.__init__(self)
        self.setWindowIcon(QIcon('resource/trayIcon.png'))
        
        print(pyautogui.size())
        
        if rest.isAdmin() :
            self.setupUi(self)
            
            ui_controller.userLoadInfo(self)
            self.checkVersion()
            self.setWindowFlags(Qt.FramelessWindowHint)
            self.loginButton.clicked.connect(self._loginCheck)
            self.minimumButton.clicked.connect(self._minimumWindow)
            self.exitButton.clicked.connect(self._closeWindow)
            self.remoteButton.clicked.connect(self.openRemote)
        else :
            
            if self.setPort() :
                chromeAutoUpdate.update()
                
                self.setupUi(self)
                
                ui_controller.userLoadInfo(self)
                self.checkVersion()
                self.setWindowFlags(Qt.FramelessWindowHint)
                self.loginButton.clicked.connect(self._loginCheck)
                self.minimumButton.clicked.connect(self._minimumWindow)
                self.exitButton.clicked.connect(self._closeWindow)
                self.remoteButton.clicked.connect(self.openRemote)
            
            else :
                self.showCustomMessageBox('프로그램 실행 오류', '이미 실행중인 프로그램이 있습니다') 
                sys.exit()

    def setPort(self) :
        self.PROCESS_PORT = 20025
        
        try :
            serverSocket  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0) 
            
            serverSocket.bind(('localhost', self.PROCESS_PORT))
            
            serverSocket.listen(3)
            
            self.serverSocket = serverSocket
            
            return True
        except:
            return False
        
    def closeSocket(self):
        if hasattr(self, 'serverSocket'):
            self.serverSocket.close()
            
    def checkVersion(self):
        _translate = QCoreApplication.translate
        # self.setWindowTitle(_translate("LoginWindow", "Login-v"+self.version))


    def _loginCheck(self):
        
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        userIp = s.getsockname()[0]
        s.close()
        
        userId = self.idEdit.text()
        userPw = self.pwEdit.text()
        cbSaveInfo = self.idpw_checkbox.isChecked()
        version = rest.getVersion()
        force= False
        ui_controller.userSaveInfo(self, cbSaveInfo, userId, userPw, version)
        
        data = {'userId':userId,'userPw':userPw, "key":"tiktokmate" ,"ip":userIp, "force":force}
        print("1111")
        loginCheckInfo = rest.login(**data)
        loginStatus = loginCheckInfo['status']
        loginMessage = ""
        if loginStatus == False :
            loginMessage = loginCheckInfo['message']
        
        try :
            if loginStatus != True :
                if loginStatus ==  "EU001" or loginMessage ==  "EU001":
                    self.showCustomMessageBox('로그인 에러', '올바른 계정정보를 입력해주세요') 
                    
                elif loginStatus == "EU002" or loginMessage ==  "EU002":
                    self.showCustomMessageBox('로그인 에러', '이용기간이 만료되었습니다')  
                    
                elif loginStatus  == "EU003" or loginMessage ==  "EU003":
                    self.showOtherPlaceMessageBox('중복 로그인', '다른 장소에서 로그인 중입니다 \nㅤㅤ접속을 끊고 로그인하시겠습니까???ㅤㅤ')   
                
            else :
                self.close()
                loginCheckInfo['data']['ip'] = userIp
                # print(loginCheckInfo )
                self.main = MainWindow(login_data=loginCheckInfo)
                self.main.setWindowIcon(QIcon('resource/trayIcon.png'))
                self.main.show()
                
        except Exception as e : 
            # print(e)
            traceback.print_exc
            
    def showOtherPlaceMessageBox(self, title, message):
        icon_path = 'resource/trayIcon.png'
        msgBox = QtWidgets.QMessageBox()
        msgBox.setWindowTitle(title)
        msgBox.setWindowIcon(QtGui.QIcon(icon_path))
        msgBox.setText(f" \nㅤㅤㅤ{message}ㅤㅤ\n ")
            
        yes_button = msgBox.addButton("확인", QtWidgets.QMessageBox.YesRole)
        no_button = msgBox.addButton("취소", QtWidgets.QMessageBox.NoRole)
        
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch(1) 
        button_layout.addWidget(yes_button)
        button_layout.addWidget(no_button)
        button_layout.addStretch(1)
        
        layout = msgBox.layout()
        item_count = layout.count()
        # for i in range(item_count - 1, -1, -1):
        #     item = layout.itemAt(i)
        #     if isinstance(item.widget(), QtWidgets.QPushButton):
        #         layout.removeItem(item)
        layout.addLayout(button_layout, layout.rowCount(), 0, 1, layout.columnCount())
        reply = msgBox.exec_()

        if msgBox.clickedButton() == yes_button:
            
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            userIp = s.getsockname()[0]
            s.close()
        
            userId = self.idEdit.text()
            userPw = self.pwEdit.text()
            force= True
            
            data = {'userId':userId,'userPw':userPw, "key":"tiktokmate" ,"ip":userIp, "force": True}
            loginCheckInfo = rest.login(**data)
            
            
            self.close()
            self.main = MainWindow( login_data=loginCheckInfo)
            self.main.setWindowIcon(QIcon('resource/trayIcon.png'))
            self.main.show()
        
    def showCustomMessageBox(self, title, message):
        icon_path = 'resource/trayIcon.png'
        msgBox = QtWidgets.QMessageBox()
        msgBox.setWindowTitle(title)
        msgBox.setWindowIcon(QtGui.QIcon(icon_path))
        msgBox.setText(f" \nㅤㅤ{message}ㅤㅤㅤ\n ")
        msgBox.exec_()
    
    def openRemote(self) :
        webbrowser.open("https://www.helpu.kr/agcglobal")
        
    def _minimumWindow(self):
        self.showMinimized()

    def _closeWindow(self):
        self.closeSocket()
        QCoreApplication.instance().quit()
                
    def keyPressEvent(self, e): 
        if e.key() in [Qt.Key_Return, Qt.Key_Enter] :
            self._loginCheck()
    
    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.oldPos != None :
                
            delta = QPoint (event.globalPos() - self.oldPos)
            self.move(self.x() + delta.x(), self.y()+ delta.y())
            self.oldPos = event.globalPos()
            
    def mouseReleaseEvent(self, event) :
        self.oldPos =None

    


if __name__ == "__main__":
    try:
        os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
        QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
        app = QApplication(sys.argv)
        
        loading_window = ProcessWindow()
        loading_window.show()

        initializer = Initializer()
        thread = QtCore.QThread()
        initializer.moveToThread(thread)
        
        def show_login():
            global login_window 
            login_window = Login()
            login_window.show()
            
        initializer.progressChanged.connect(loading_window.progressBar.setValue)
        initializer.finished.connect(thread.quit)
        initializer.finished.connect(loading_window.close)
        initializer.finished.connect(show_login)

        thread.started.connect(initializer.run)
        thread.start()

        sys.exit(app.exec_())
        
        # window = Login()
        # window.show()
        # sys.exit(app.exec_())
    except Exception as e:
        print(e)
        traceback.print_exc()
        with open("error_log.txt", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        raise
    