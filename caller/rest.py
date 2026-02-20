# -*- coding: utf-8 -*-

import requests
import json
import os
import configparser
import traceback

main_server = 'http://43.201.119.167:23113/'
# main_server = 'http://127.0.0.1:23113/'

def isAdmin():
    # return True
    return False

def login(**data):
    body = {
            'id': data['userId'], 
            'pw': data['userPw'],
            'key': data['key'],
            'ip': data['ip'],
            'force' : data['force']
    }
    try :
        print("31231231231221312")
        print(body)
        response = requests.post(main_server + 'user/login/god', data = body, timeout= 300)
        print("0000")
        print(response)
        loginObject = json.loads(response.text)
        print("1111")
        print(loginObject)
        
        return loginObject
    except Exception as e :            
        raise e.Except["None"]
    
def logOut(**data):
    body = {
            'id': data['userId'], 
            'key': data['key']
    }
    try :
        response = requests.post(main_server + 'user/logout/god', data = body, timeout= 300)
        loginObject = json.loads(response.text)
        return loginObject["status"]
    except Exception as e :            
        raise e.Except["None"]

def loginCheck(**data):
    body = {
            'id': data['userId'], 
            'key': data['key'],
            'ip': data['ip'],
    }
    try :
        response = requests.post(main_server + 'user/login/god/check', data = body, timeout= 300)
        loginObject = json.loads(response.text)
        
        return loginObject
    except Exception as e :            
        raise e.Except["None"]
    
def getVersion():
    response = requests.get(main_server + 'free/lately/?item=23')
    bodyObject = json.loads(response.text)
    return bodyObject.get("version")

def setPort():
    
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        info_file_path = os.path.join(current_dir, '..', 'info.on')
        info_file_path = os.path.normpath(info_file_path)
        
        config = configparser.ConfigParser()
        config.read(info_file_path)
        
        if 'Config' in config and 'version' in config['Config']:
            version = config['Config']['version']
            return True
        
    except Exception as e: 
        # print("2222")
        traceback.print_exc()
        return False
    
def postErrorLog(code, soId, message):
    body = {
            'program': "tiktokmate", 
            'code': code,
            'soId': soId,
            'message' : message
    }
    try :
        response = requests.post(main_server + 'process/dev/err', data = body, timeout= 300)
        loginObject = json.loads(response.text)
        
        return loginObject
    except Exception as e :            
        raise e.Except["None"]
    
    
    
def postWarningLog(message, soId):
    body = {
            'message': message, 
            'soId': soId,
            'program' : 'tiktokmate'
    }
    print(body)
    try :
        response = requests.post(main_server + 'process/dev/warning', data = body, timeout= 300)
        loginObject = json.loads(response.text)
        
        return loginObject
    except Exception as e :            
        # raise e.Except["None"]
        print(e)
    
    
def sendErrorMessage(message, file_path) :

    TOKEN = '8134776243:AAE2AKzzjUpuRpceG2oTWPNfKbLDkRc-VqQ'
    CHAT_ID = '5026820079'
    IMAGE_PATH = file_path

    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"

    with open(IMAGE_PATH, 'rb') as photo:
        files = {'photo': photo}
        data = {'chat_id': CHAT_ID, 'caption': message}
        response = requests.post(url, files=files, data=data)

    print(response.status_code)
    print(response.json())
    