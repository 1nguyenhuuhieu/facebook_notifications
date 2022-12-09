import json
import time
import pyscreenshot as ImageGrab
import pytz
from datetime import date
from datetime import datetime

from selenium.webdriver.common.by import By
from seleniumwire import webdriver

import sqlite3
import random

# import hàm tự định nghĩa
from config import init

proxy_server = "180.214.236.203:2021"


status = "..."
screenshot_path = "static/screenshot.png"
time_sleep = random.randint(7, 10)

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
    options = {
    'proxy': {
        'http': 'http://Proxyviet51340:CWrg2Swu@180.214.236.203:2021',
        'https': 'http://Proxyviet51340:CWrg2Swu@180.214.236.203:2021',
        'no_proxy': 'localhost,127.0.0.1'
    }
}
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications" : 2,
            "profile.managed_default_content_settings.images": 2
    }
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_experimental_option("prefs",prefs)
    chrome_options.add_argument('--proxy-server=%s' % proxy_server)
    
    return webdriver.Chrome(executable_path=driver_filepath, chrome_options=chrome_options, seleniumwire_options=options)


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
    global status
    
    try:
        status = "Mở trang thông báo"
        now = str(datetime.now(vn_tz))
        now_date = str(datetime.now(vn_tz).date())
        file_path = f"logs/notifications-clicked-{now_date}.txt"

        print("TRY NOTIFICATIONS PAGE")
        print(now)
        time.sleep(time_sleep)
        unread_btn = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[2]/div/div[1]/div/div/div/div[1]/div[3]/div[1]/div[2]/div')
        unread_btn.click()
        print("unread clicked")
        status = "Mở trang thông báo chưa đọc"

        time.sleep(time_sleep)
        news_btn = driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[2]/div/div[1]/div/div/div/div[1]/div[3]/div[2]/div/div/div[2]/div[1]')
        news_btn.click()
        print("notification clicked")
        status = "Xem thông báo chưa đọc mới nhất"
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
        status = "Lỗi khi mở trang thông báo"
        try:
            reload_btn = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div/div[3]/div/div')
            status = "Đã bị block tạm thời"
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
            status = "Không có thông báo mới hoặc bị block tạm thời, chờ 5 phút thử lại"
            print("EXCEPT NO NEW NOTIFICATION, wait 300s to recheck")
            time.sleep(300)
            driver.get(notifications_url)
    return None

def anti_fb_ai(driver):
    global status
    status = "Đang vào chế độ tự động tương tác"
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

def take_screenshot(screenshot_path):
    # fullscreen
    im=ImageGrab.grab()
    # to file
    im.save(screenshot_path)

    return None


start_time = datetime.now(vn_tz).strftime("%Y-%m-%d %H:%M:%S")
create_monitor(start_time)

count_post = 0
count = 0
start = "no"

try:
    driver = init_driver(driver_filepath)
    login_facebook(driver, home_url, cookies_filepath, pwd_facebook)
    driver.get(notifications_url)
except:
    pass




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
            status = "Lỗi không xác định"
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
        "status": status,
        "count_post": count_post,
        "last_time": last_time,
        "start_time": start_time
    }

    try:
        update_monitor(data)
    except:
        pass


    #Chụp ảnh màn hình mỗi 10 lần check noti
    if count % 10 == 0:
        try:
            take_screenshot(screenshot_path)
        except:
            pass


