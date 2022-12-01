import configparser

import json
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium import webdriver

import smtplib
from email.message import EmailMessage


# khởi tạo thông tin từ file config
def init():
    config = configparser.ConfigParser()
    config.read('config.ini', encoding='utf-8')
    return config

def load_keywords(file_path):
    file = open(file_path, encoding='utf-8')
    keywords_json = json.load(file)
    file.close()

    return [keyword for keyword in keywords_json.values()]

config = init()

driver_filepath = config["DRIVER"]["file_path"]

home_url = config["FACEBOOK"]["home_url"]
notifications_url = config["FACEBOOK"]["notifications_url"]

cookies_filepath = config["FACEBOOK"]["file_path"]
user_facebook =  config["FACEBOOK"]["user"]
pwd_facebook = config["FACEBOOK"]["pwd"]


sender_email = config["EMAIL"]["sender"]
pwd_email = config["EMAIL"]["pwd"]
receiver_email = config["EMAIL"]["receiver"]

keyword_filepath = config["KEYWORDS"]["file_path"]

#load keywords từ file json
keywords = load_keywords(keyword_filepath)


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

def init_driver(driver_filepath):
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications" : 2}
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


def notifications_listener():
    time.sleep(3)
    found = False
    keywords_found = []
    try:
        time.sleep(5)
        unread_btn = driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[2]/div/div[1]/div/div/div/div[1]/div[3]/div[1]/div[2]/div/span/span')
        unread_btn.click()

        time.sleep(5)
        news_btn = driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[2]/div/div[1]/div/div/div/div[1]/div[3]/div[2]/div/div/div[2]/div[1]')
        news_btn.click()
        time.sleep(15)

        post = driver.find_element(By.CSS_SELECTOR, "span[class='x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x3x7a5m x6prxxf xvq8zen xo1l8bm xzsf02u x1yc453h']")
        post = post.text.lower()
        print(post)
        time.sleep(2)
        if "see more" in post:
            seemore_btn = driver.find_element(By.CSS_SELECTOR, "div[class='x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xt0b8zv xzsf02u x1s688f']")
            
            seemore_btn.click()

            time.sleep(3)

        time.sleep(5)

        post_text = driver.find_element(By.CSS_SELECTOR, "span[class='x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x3x7a5m x6prxxf xvq8zen xo1l8bm xzsf02u x1yc453h']").text
        post_text = post_text.lower()

        for keyword in keywords:
            if keyword in post_text:
                found = True
                keywords_found.append(keyword)

        if found:
            post_url = driver.current_url
            list_str = post_url.split("/")

            post = list_str[5]
            list_post = post.split("=")
            post_id = list_post[1].split("%")
            post_id = post_id[0].split("&")
            post_id = post_id[0]

            msg = f'Tìm thấy từ khóa "{keywords_found}" trong bài viết "{post_id}" tại group: {list_str[4]} \nNội dung bài viết:\n{post_text}'

            print(msg)

            return msg
        else:
            return None

    except:
        return None



def goto_notifications_page():
    try:
        see_all_link = driver.find_element(By.CSS_SELECTOR, "a[class='x1i10hfl x1qjc9v5 xjqpnuy xa49m3k xqeqjp1 x2hbi6w x13fuv20 xu3j5b3 x1q0q8m5 x26u7qi x972fbf xcfux6l x1qhh985 xm0m39n x9f619 xdl72j9 x2lah0s xe8uvvx x2lwn1j xeuugli x16tdsg8 xggy1nq x1ja2u2z x1t137rt x1q0g3np x87ps6o x1lku1pv x1a2a7pz x1fey0fg x1ypdohk x92akz8 x1k74hu9 x76ihet xwmqs3e x112ta8 xxxdfa6 x1lcm9me x1yr5g0i xrt01vj x10y3i5r x1rg5ohu xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x1n2onr6 x3ajldb actionChildElement']")

        see_all_link.click()
    except:
        driver.get(notifications_url)

driver = init_driver(driver_filepath)
login_facebook(driver, home_url, cookies_filepath, pwd_facebook)


driver.get(notifications_url)

while True:
    try:
        msg = notifications_listener()
        if msg:
            send_notification_mail(sender_email, pwd_email, receiver_email, msg)
        time.sleep(3)
        goto_notifications_page()
        time.sleep(5)

    except:
        pass



