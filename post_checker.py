import configparser
import sqlite3


import json
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver

import smtplib
import func_timeout
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
    print("---------------------------------------")
    print("Gửi mail thông báo thành công")

    return None


def post_checker(driver):
    try:
        con = sqlite3.connect("fb.db")
        cur = con.cursor()
        res = cur.execute("SELECT post_id FROM post ORDER BY ROWID ASC LIMIT 1;")
        post_id = res.fetchone()[0]
        cur.execute("DELETE FROM post WHERE post_id=:post_id", {"post_id": post_id})
        con.commit()


        driver.get(f"{home_url}/{post_id}")
        time.sleep(5)

        group_id = driver.current_url.split("/")[4]

        now = str(datetime.now(vn_tz))
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
        print(post_text)
        print("---")

        for keyword in keywords:
            if keyword in post_text:
                status = "found"
                keywords_found.append(keyword)

        result = {
        "status": status,
        "keywords_found": keywords_found,
        "group": group_id,
        "post_id": post_id,
        "post_text": post_text,
        "checked_time": now
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



def main(driver):

    count_post = 0
    while True:
        time.sleep(5)
        today = datetime.now(vn_tz).date()
        count_post += 1
        print("***")
        print(f"Đang kiểm tra bài viết số: {count_post}")
        
        try:
            listener_post = post_checker(driver)
            log_file_path = f"logs/{listener_post['status']}-{today}.json"
            try:
                write_log(log_file_path, listener_post)
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
                try:
                    email_content = json.dumps(listener_post, indent=4, ensure_ascii=False)
                    func_timeout.func_timeout(20, send_notification_mail(sender_email, pwd_email, receiver_email, email_content))
                except func_timeout.FunctionTimedOut:
                    print("Gửi mail thất bại")  

            time.sleep(3)

        except:
            time.sleep(random.randint(60,100))


driver = mobile_driver()
main(driver)

