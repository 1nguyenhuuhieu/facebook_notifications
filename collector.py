import configparser
import sqlite3


import json
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver

import pytz
from datetime import date
from datetime import datetime

vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')

# khởi tạo thông tin từ file config
def init(file_path):
    config = configparser.ConfigParser()
    config.read(file_path, encoding='utf-8')
    return config

file_path = "config.ini"
config = init(file_path)

driver_filepath = config["DRIVER"]["windows"]


home_url = config["FACEBOOK"]["m_home_url"]
notifications_url = config["FACEBOOK"]["m_notifications_url"]

cookies_filepath = config["FACEBOOK"]["m_file_path"]
user_facebook =  config["FACEBOOK"]["user"]
pwd_facebook = config["FACEBOOK"]["pwd"]


# giả lập driver mobile
def mobile_driver():
    
    mobile_emulation = {
    "deviceMetrics": {"width": 360, "height": 640, "pixelRatio": 3.0},
    "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19"}
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)

    # tắt thông báo và tắt hiển thị hình ảnh
    prefs = {"profile.default_content_setting_values.notifications" : 2,
            "profile.managed_default_content_settings.images": 2
    }
    chrome_options.add_experimental_option("prefs",prefs)


    driver = webdriver.Chrome(executable_path=driver_filepath, options=chrome_options)
    driver.get(home_url)


    # sử dụng extensions "クッキーJSONファイル出力 for Puppeteer" https://chrome.google.com/webstore/detail/%E3%82%AF%E3%83%83%E3%82%AD%E3%83%BCjson%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB%E5%87%BA%E5%8A%9B-for-puppet/nmckokihipjgplolmcmjakknndddifde để xuất json cookies
    file = open(cookies_filepath)
    cookies = json.load(file)
    file.close()
    for cookie in cookies:
        driver.add_cookie(cookie)

    driver.get(home_url)
    time.sleep(3)
    
    try:
        account_link = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div[2]/div/div/div[1]/div/div')
        account_link.click()
        
        time.sleep(3)

        input_pwd = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[3]/div[1]/div/form/div[1]/div/div/div/div/div[1]/div/input')
        input_pwd.send_keys(pwd_facebook)

        time.sleep(5)

        login_btn = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[3]/div[1]/div/form/div[2]/button')
        login_btn.click()
        time.sleep(3)

    except:
        pass

    return driver


driver = mobile_driver()
