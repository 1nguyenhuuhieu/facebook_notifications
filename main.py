import configparser


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


home_url = config["FACEBOOK"]["home_url"]
notifications_url = config["FACEBOOK"]["notifications_url"]

cookies_filepath = config["FACEBOOK"]["file_path"]
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
print(groups)


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
    is_logged = False
    driver.get(home_url)
    # sử dụng extensions "クッキーJSONファイル出力 for Puppeteer" https://chrome.google.com/webstore/detail/%E3%82%AF%E3%83%83%E3%82%AD%E3%83%BCjson%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB%E5%87%BA%E5%8A%9B-for-puppet/nmckokihipjgplolmcmjakknndddifde để xuất json cookies
    file = open(cookies_filepath)
    cookies = json.load(file)
    file.close()
    for cookie in cookies:
        driver.add_cookie(cookie)

    driver.refresh()

    time.sleep(5)

    # nếu chưa login thành công, đăng nhập lại 3 lần
    count = 0

    while not is_logged:
        driver.get(home_url)
        if count == 2:
            is_logged = True

        try:
            check_login_succeed = driver.find_elenment(By.XPATH, '/html/body/div[1]/div/div[1]/div/div[2]/div[3]/div/div[1]/div[1]/ul/li[1]/span/div/a')
            is_logged = True
            print("Đăng nhập thành công")
        
        except:
            count += 1
            try:
                account_link = driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[1]/div/div/div/div[1]/div[4]/div[1]/div/div[1]/a[1]')
                account_link.click()

                time.sleep(3)
                pwd_input = driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/div/div/div/div/form/div[2]/div/input')
                pwd_input.click()
                pwd_input.send_keys(pwd_facebook)
                time.sleep(10)
                login_btn = driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/div/div/div/div/form/div[4]/button')
                login_btn.click()

                time.sleep(5)
            except:
                pass

    return None


def notifications_listener(driver):

    now = str(datetime.now(vn_tz))
    
    time.sleep(3)
    status = "notfound"
    keywords_found = []
    unread_btn = driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[2]/div/div[1]/div/div/div/div[1]/div[3]/div[1]/div[2]/div/span/span')
    unread_btn.click()

    time.sleep(random.randint(3,5))
    news_btn = driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[2]/div/div[1]/div/div/div/div[1]/div[3]/div[2]/div/div/div[2]/div[1]')
    news_btn.click()

    # ghi notification đã xem vào logs
    now_date = str(datetime.now(vn_tz).date())
    file_path = f"logs/notifications-clicked-{now_date}.txt"
    with open(file_path, "a", encoding='utf-8') as text_file:
        text_file.write(f"Time clicked: {str(now)}, Notification URL: {str(driver.current_url)} \n")
        

    time.sleep(random.randint(7,10))

    post_url = driver.current_url
    list_str = post_url.split("/")

    post = list_str[5]
    list_post = post.split("=")
    post_id = list_post[1].split("%")
    post_id = post_id[0].split("&")
    post_id = post_id[0]
    group = list_str[4]

    driver.get(f"https://www.facebook.com/{post_id}")
    
    time.sleep(random.randint(15,20))
    try:
        post_text = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div/div[1]/div/div/div/div/div/div/div/div/div/div/div[8]').text.lower().replace('\n', '-')

    except:
        try:
            post_text = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div/div/div[1]/div/div/div/div/div/div/div/div/div/div/div[8]/div').text.lower().replace('\n', '-')
        except:
            status = "error"
            post_text = ""
            print(f"Không lấy được bài viết tại group: {list_str[4]}")

    for keyword in keywords:
        if keyword in post_text:
            status = "found"
            keywords_found.append(keyword)

    if status == "found":
        msg = f'Tìm thấy từ khóa "{keywords_found}" trong bài viết "{post_id}" tại group: {list_str[4]} \nNội dung bài viết:\n{post_text}'
        print(msg)
    else:
        print(post_text)

    

    result = {
        "status": status,
        "keywords_found": keywords_found,
        "group": group,
        "post_id": post_id,
        "post_text": post_text,
        "checked_time": now
    }

    return result

def goto_notifications_page(driver):
    try:
        noti_link = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[1]/div/div[2]/div[4]/div[1]/div[1]/span/span/div/a")

        noti_link.click()

        time.sleep(3)

        seeall_link = driver.find_element(By.XPATH, "/html/body/div[1]/div/div[1]/div/div[2]/div[4]/div[2]/div/div/div[1]/div[1]/div/div/div/div/div/div/div[1]/div[3]/div[2]/div/div/div[1]/div/div/div/div/div/div/span/div/div[2]/div/div[2]/div/a/span/span")
        seeall_link.click()
    except:
        driver.get(notifications_url)


def write_log(file_path, file_content):
    now = str(datetime.now(vn_tz))
    json_object = json.dumps(file_content, indent=4, ensure_ascii=False)
    json_now_object = f'"{now}": {json_object} , '
    with open(file_path, "a", encoding='utf-8') as text_file:
        text_file.write(json_now_object)

    return None




driver = init_driver(driver_filepath)
login_facebook(driver, home_url, cookies_filepath, pwd_facebook)
def main(driver):


    driver.get(notifications_url)

    count_post = 0
    while True:
        today = datetime.now(vn_tz).date()
        count_post += 1
        print("***")
        print(f"Đang kiểm tra bài viết số: {count_post}")
        time.sleep(random.randint(1,5))
        try:
            listener_post = notifications_listener(driver)


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

            goto_notifications_page(driver)
            time.sleep(5)

        except:
            driver.get(notifications_url)
            time.sleep(random.randint(180,300))


main(driver)