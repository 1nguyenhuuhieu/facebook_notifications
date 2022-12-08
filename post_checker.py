import configparser
import sqlite3


import json
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver

import smtplib
from email.message import EmailMessage

import pytz
from datetime import date
from datetime import datetime

vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')

# khởi tạo thông tin từ file config
def init(file_path):
    config = configparser.ConfigParser()
    config.read(file_path, encoding='utf-8')
    return config

def load_json_file(file_path):
    file = open(file_path, encoding='utf-8')
    items_json = json.load(file)
    file.close()

    return [item for item in items_json.values()]

file_path = "config.ini"
config = init(file_path)

driver_filepath = config["DRIVER"]["windows"]


home_url = config["FACEBOOK"]["m_home_url"]
notifications_url = config["FACEBOOK"]["m_notifications_url"]

cookies_filepath = config["FACEBOOK"]["m_file_path"]
user_facebook =  config["FACEBOOK"]["user"]
pwd_facebook = config["FACEBOOK"]["pwd"]


sender_email = config["EMAIL"]["sender"]
pwd_email = config["EMAIL"]["pwd"]
receiver_email = config["EMAIL"]["receiver"]

keyword_filepath = config["KEYWORDS"]["file_path"]

groups_filepath = config["GROUPS"]["file_path"]

#load keywords từ file json
keywords = load_json_file(keyword_filepath)

#load group từ file json
groups = load_json_file(groups_filepath)

print(keywords)

# Gửi mail sử dụng application pwd của gmail
def send_notification_mail(sender, pwd, receiver, email_content):
    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)
    # start TLS for security
    s.starttls()
    # Authentication
    s.login(sender, pwd)
    # message to be sent
    msg = EmailMessage()
    msg.set_content(email_content)
    msg['Subject'] = 'Thông báo về từ khóa trên group facebook'
    msg['From'] = sender
    msg['To'] = receiver
    # sending the mail
    s.send_message(msg)
    # terminating the session
    s.quit()
    print("Gửi mail thông báo thành công")

    return None


def post_checker(driver):
    global count_post
    try:
        con = sqlite3.connect("fb.db")
        cur = con.cursor()
        res = cur.execute("SELECT post_id FROM post_uncheck ORDER BY ROWID ASC LIMIT 1;")
        post_id = res.fetchone()[0]
        cur.execute("DELETE FROM post_uncheck WHERE post_id=:post_id", {"post_id": post_id})
        con.commit()
        

        driver.get(f"{home_url}/{post_id}")
        print(f"go to post id: {post_id}")
        count_post += 1
        time.sleep(5)

        group_id = driver.current_url.split("/")[4]

        now = datetime.now(vn_tz)
        now = now.strftime("%Y-%m-%d %H:%M")
        now_date = str(datetime.now(vn_tz).date())

        status = "notfound"
        keywords_found = []

        try:
            post_text = driver.find_element(By.XPATH, ' /html/body/div[1]/div/div[4]/div/div[1]/div[1]/div/div/div[1]').text.lower().replace('\n', '-')
            

        except:
            cur.execute("INSERT INTO post_broken VALUES (:post_id)", {"post_id": post_id})
            con.commit()
            status = "error"
            post_text = ""
    
        
        con.close()
        print(f"post text: {post_text}")

        for keyword in keywords:
            if keyword in post_text:
                status = "found"
                keywords_found.append(keyword)
            
        print(f"status: {status} ")

        result = {
        "status": status,
        "keywords_found": str(keywords_found),
        "checked_time": str(now),
        "post_id": int(post_id),
        "group_id": group_id,
        "post_text": post_text,
        
        }

        return result

    except:
        return None


def write_log(file_path, file_content):
    now = str(datetime.now(vn_tz))
    json_object = json.dumps(file_content, indent=4, ensure_ascii=False)
    json_now_object = f'"{now}": {json_object} , '
    with open(file_path, "a", encoding='utf-8') as text_file:
        text_file.write(json_now_object)

    return None

def save_database(data):
    con = sqlite3.connect("fb.db")
    cur = con.cursor()
    cur.execute("INSERT INTO post_checked VALUES (:status, :keywords_found,:checked_time, :post_id, :group_id, :post_text )", data)
    con.commit()
    con.close()

    return None


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



def create_monitor(start_time):
    con = sqlite3.connect("fb.db")
    cur = con.cursor()
    cur.execute("INSERT INTO monitor_post_checker VALUES ('yes', 'starting',:start_time, 0, 'last_time', 0 )", {"start_time": start_time})
    con.commit()
    con.close()

    return None


def update_monitor(data):
    con = sqlite3.connect("fb.db")
    cur = con.cursor()
    cur.execute("""
    UPDATE monitor_post_checker
    SET status = :status, count_post = :count_post, last_time = :last_time, count_found_post = :count_found_post
    WHERE start_time = :start_time
    """, data)
    con.commit()
    con.close()

    return None



def main(driver):


    while True:
        time.sleep(5)
        now = str(datetime.now(vn_tz))
        today = datetime.now(vn_tz).date()
        print("---")
        print(f"Checking: {count_post}")
        print(now)
        
        try:
            listener_post = post_checker(driver)
            log_file_path = f"logs/{listener_post['status']}-{today}.json"
            try:
                write_log(log_file_path, listener_post)
                print("written to file log")
            except:
                pass
            try:
                save_database(listener_post)
                print("saved to database")
            except:
                pass

           
            try:
                total_logs_file_path = f"logs/logs-{today}.txt"
                with open(total_logs_file_path, "a", encoding='utf-8') as text_file:
                    now = datetime.now(vn_tz)
                    text_file.write(f"Status: {listener_post['status']}, Checked: {count_post}, Time: {now} ,  Post ID: {listener_post['post_id']}, Group: {listener_post['group']} \n")
            except:
                pass

            if listener_post["status"] == "found":
                global count_found_post
                count_found_post += 1
                try:
                    email_content = json.dumps(listener_post, indent=4, ensure_ascii=False)
                    send_notification_mail(sender_email, pwd_email, receiver_email, email_content)
                except:
                    print("Gửi mail thất bại")  

            time.sleep(3)

        except:
            time.sleep(random.randint(60,100))
        
        last_time = datetime.now(vn_tz).strftime("%Y-%m-%d %H:%M")

        data= {
            "status":"tốt",
            "count_post": count_post,
            "last_time": last_time,
            "start_time": start_time,
            "count_found_post": count_found_post
        }

        update_monitor(data)


count_post = 0
count_found_post = 0

driver = mobile_driver()
start_time = datetime.now(vn_tz).strftime("%Y-%m-%d %H:%M:%S")
create_monitor(start_time)

main(driver)

