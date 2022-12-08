import json
import time

import pytz
from datetime import date
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium import webdriver

import sqlite3
import random

# import hàm tự định nghĩa
from config import init


time_sleep = random.randint(5, 7)

vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')

file_path = "config.ini"
config = init(file_path)

driver_filepath = config["DRIVER"]["windows"]

home_url = config["FACEBOOK"]["home_url"]
notifications_url = config["FACEBOOK"]["notifications_url"]

cookies_filepath = config["FACEBOOK"]["file_path"]
user_facebook =  config["FACEBOOK"]["user"]
pwd_facebook = config["FACEBOOK"]["pwd"]

# Khởi tạo chrome driver với: maximize cửa sổ, disable thông báo đẩy, disable images hiển thị
def init_driver(driver_filepath):
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications" : 2,
            "profile.managed_default_content_settings.images": 2
    }
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_experimental_option("prefs",prefs)
    
    return webdriver.Chrome(executable_path=driver_filepath, chrome_options=chrome_options)


def login_facebook(driver, home_url, cookies_filepath, pwd_facebook):
    driver.get(home_url)
    # sử dụng extensions "クッキーJSONファイル出力 for Puppeteer" https://chrome.google.com/webstore/detail/%E3%82%AF%E3%83%83%E3%82%AD%E3%83%BCjson%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB%E5%87%BA%E5%8A%9B-for-puppet/nmckokihipjgplolmcmjakknndddifde để xuất json cookies
    with open(cookies_filepath, 'r') as file:
        file = open(cookies_filepath)
        cookies = json.load(file)

    for cookie in cookies:
        driver.add_cookie(cookie)

    driver.get(home_url)
    time.sleep(5)

    try:
        is_logged = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div/div[2]/div[3]/div/div[1]/div[1]/ul/li[1]/span/div/a')
        return True
    except:
        driver.get(home_url)
        time.sleep(3)
        account_link = driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[1]/div/div/div/div[1]/div[4]/div[1]/div/div[1]/a[1]')
        account_link.click()
        time.sleep(3)

        pwd_input = driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/div/div/div/div/form/div[2]/div/input')
        pwd_input.click()
        pwd_input.send_keys(pwd_facebook)
        time.sleep(5)

        login_btn = driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/div/div/div/div/form/div[4]/button')
        login_btn.click()
        time.sleep(5)
    
    driver.get(home_url) 
    time.sleep(3)
    
    return False

def notifications_collector(driver):
    
    try:
        now = str(datetime.now(vn_tz))
        now_date = str(datetime.now(vn_tz).date())
        file_path = f"logs/notifications-clicked-{now_date}.txt"

        print("TRY NOTIFICATIONS PAGE")
        print(now)
        time.sleep(time_sleep)
        unread_btn = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[2]/div/div[1]/div/div/div/div[1]/div[3]/div[1]/div[2]/div')
        unread_btn.click()
        print("unread clicked")

        time.sleep(time_sleep)
        news_btn = driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[2]/div/div[1]/div/div/div/div[1]/div[3]/div[2]/div/div/div[2]/div[1]')
        news_btn.click()
        print("notification clicked")
        time.sleep(time_sleep)

        post_url = driver.current_url

        # ghi notification đã xem vào logs
        

        with open(file_path, "a", encoding='utf-8') as text_file:
            text_file.write(f"Time clicked: {str(now)}, Notification URL: {post_url} \n")
            
        post_id = post_url.split("/")[5].split("=")[1].split("%")[0].split("&")[0]
        try:
            con = sqlite3.connect("fb.db")
            cur = con.cursor()
            cur.execute("INSERT INTO post_uncheck VALUES (:post_id)", {"post_id": post_id})
            con.commit()
            con.close()
        except:
            print("Lỗi khi thêm vào database")

        driver.back()
        print("back to notifications page")


    except:
        print("EXCEPT RELOAD PAGE")
        try:
            reload_btn = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div/div[3]/div/div')
            a_elements = driver.find_elements(By.TAG_NAME, 'a')
            for a in a_elements:
                if "/notifications/" in a.get_attribute("href"):
                    a.click()
                    print("notifications clicked")
                    time.sleep(time_sleep)
                    seeall_link = driver.find_element(By.PARTIAL_LINK_TEXT, "See all")
                    seeall_link.click()
                    print("see all clicked")
                    time.sleep(time_sleep)
                    return None
        except:
            print("EXCEPT NO NEW NOTIFICATION, wait 300s to recheck")
            time.sleep(300)
            driver.get(notifications_url)
    return None

def anti_fb_ai(driver):
    driver.get(home_url)
    time.sleep(time_sleep)
    print("go to home page")

    driver.execute_script("window.scrollTo(0, 1000)")
    time.sleep(time_sleep)
    driver.execute_script("window.scrollTo(0, 0)")

    driver.get(home_url)
    time.sleep(time_sleep)
    like_btn = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div[2]/div/div/div/div[3]/div/div[3]/div/div/div[1]/div/div/div/div/div/div/div/div/div/div/div/div[8]/div/div[4]/div/div/div[1]/div/div[2]/div/div[1]/div[1]/div[1]')
    like_btn.click()
    time.sleep(time_sleep)
    driver.get(home_url)
    time.sleep(time_sleep)


    return None



def create_monitor(start_time):
    con = sqlite3.connect("fb.db")
    cur = con.cursor()
    cur.execute("INSERT INTO monitor_collector VALUES ('yes', 'starting',:start_time, 0, 'last_time' )", {"start_time": start_time})
    con.commit()
    con.close()

    return None

def update_monitor(data):
    con = sqlite3.connect("fb.db")
    cur = con.cursor()
    cur.execute("""
    UPDATE monitor_collector
    SET status = :status, count_post = :count_post, last_time = :last_time
    WHERE start_time = :start_time
    """, data)
    con.commit()
    con.close()

    return None


start_time = datetime.now(vn_tz).strftime("%Y-%m-%d %H:%M:%S")
create_monitor(start_time)
driver = init_driver(driver_filepath)
login_facebook(driver, home_url, cookies_filepath, pwd_facebook)
driver.get(notifications_url)
count_post = 0
count = 0
start = "no"
status = "..."




while True:
    print("-----")
    print(f"Notification {count_post} seeing")
    count += 1
    count_post += 1
    time.sleep(time_sleep)
    if count < 100:
        try:
            notifications_collector(driver)
        except:
            print("EXCEPT TRUE")
            time.sleep(time_sleep)
            driver.get(notifications_url)
        
        time.sleep(time_sleep)
    else:
        count = 0
        try:
            print("ANTI FB AI MODE")
            anti_fb_ai(driver)
        except:
            time.sleep(300)

    last_time = datetime.now(vn_tz).strftime("%Y-%m-%d %H:%M")

    data= {
        "status":"tốt",
        "count_post": count_post,
        "last_time": last_time,
        "start_time": start_time
    }

    update_monitor(data)

