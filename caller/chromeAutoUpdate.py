# -*- coding: utf-8 -*-

import requests
import zipfile
import os
import time
import getpass
from bs4 import BeautifulSoup
from win32com.client import Dispatch
import pythoncom

import json
import struct

def patchChromeDriver(originalPath, patchedPath):
    try:
        # 1. 파일 내용 읽기
        with open(originalPath, 'rb') as f:
            file_content = bytearray(f.read())
        
        # 2. 패치할 바이트 시퀀스 정의
        # 'c' (99), 'd' (100), 'c' (99), '_' (95) -> 'd' (100), 'o' (111), 'g' (103), '_' (95)
        search_sequence = b'\x63\x64\x63\x5f' 
        replace_sequence = b'\x64\x6f\x67\x5f'
        
        patch_applied = False
        start_index = 0
        
        # 3. 파일 내용에서 시퀀스 찾기 및 패치
        while True:
            index = file_content.find(search_sequence, start_index)
            
            if index == -1:
                break
            
            # 일치하는 시퀀스를 대체
            for i in range(len(replace_sequence)):
                file_content[index + i] = replace_sequence[i]
            
            print(f"Patch applied at offset: {index}")
            patch_applied = True
            
            start_index = index + len(replace_sequence) 
        
        if not patch_applied:
            print("Search sequence not found. No patch applied.")

        # 4. 패치된 내용 파일로 쓰기
        with open(patchedPath, 'wb') as f:
            f.write(file_content)
        
        print(f"Patched file successfully written to: {patchedPath}")
        
    except FileNotFoundError:
        print(f"Error: File not found at {originalPath}")
    except Exception as e:
        print(f"An error occurred during patching: {e}")
        
def get_version_via_com(filename):
    parser = Dispatch("Scripting.FileSystemObject",pythoncom.CoInitialize())
    try:
        version = parser.GetFileVersion(filename)
        return version
    except Exception:
        pass

def get_chrome_version():
    userName = getpass.getuser()
    paths = [
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Users\\" + userName + "\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe"
    ]
    for url in paths:
        chromeCheck = get_version_via_com(url)
        if chromeCheck == None:
            pass
        elif chromeCheck:
            print(chromeCheck)
            now_chrome_version = chromeCheck
            return now_chrome_version

def update() : 
    try:
        print("In update")
        try:
            os.remove(os.path.join(os.path.abspath('chromedriver.exe')))
        except FileNotFoundError:
            pass

        now_version = get_chrome_version()
        download_page = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_"+ now_version[:3]
        print("test")
        print(download_page)
        get_chromedownload = requests.get(download_page)
        print("asdf")
        print(get_chromedownload)
        print(get_chromedownload.status_code)
        print(get_chromedownload.text)



        def download(url, file_name):
            with open(file_name, "wb+") as file:
                response = requests.get(url)
                file.write(response.content)


        download_url = ""
        if get_chromedownload.status_code == 200 :
            download_url = 'https://chromedriver.storage.googleapis.com/' + str(get_chromedownload.text) + '/chromedriver_win32.zip'
        else :
            download_list = json.loads(requests.get("https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json").text).get('versions')
            last_info = None
            for download_info in download_list :
                if download_info.get('version') < now_version :
                    last_info = download_info
                else :
                    info_list = last_info.get("downloads").get("chromedriver")
                    for info in info_list :
                        if info.get("platform") == "win32" :
                            download_url = info.get("url")
                            break
                    break
            

            
        download_paths = os.path.join(os.path.abspath('chromedriver_win32.zip'))
        print(download_url)
        download(download_url, download_paths)
        try :
            chromedriver_path = zipfile.ZipFile(os.path.join(os.path.abspath('chromedriver_win32.zip'))).extract('chromedriver.exe')
        except Exception as e : 
            print(e)
            try :
                chromedriver_path = zipfile.ZipFile(os.path.join(os.path.abspath('chromedriver_win32.zip'))).extract('chromedriver-win32/chromedriver.exe')
                os.rename('./chromedriver-win32/chromedriver.exe','./chromedriver.exe')
                os.rmdir('./chromedriver-win32')
            except Exception as e : 
                print(e)
                chromedriver_path = zipfile.ZipFile(os.path.join(os.path.abspath('chromedriver_win32.zip'))).extract('chromedriver_win32/chromedriver.exe')
                os.rename('./chromedriver_win32/chromedriver.exe','./chromedriver.exe')
                os.rmdir('./chromedriver_win32')
        os.remove(os.path.join(os.path.abspath('chromedriver_win32.zip')))
        
        original_path = os.path.join(os.path.abspath('chromedriver.exe'))
        patched_path = os.path.join(os.path.abspath('chromedriver_t.exe'))
        patchChromeDriver(original_path, patched_path)
    except Exception as e:
        print (e)
        pass
    