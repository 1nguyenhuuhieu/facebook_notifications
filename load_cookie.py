import json
import random
import time
from selenium.webdriver.common.by import By
from selenium import webdriver

import smtplib
from email.message import EmailMessage

sender_mail = "1nguyenhuuhieu@gmail.com"

password = "ycydocwufdfejphw"

reciever_mail = "legolinking@gmail.com"
 



chrome_options = webdriver.ChromeOptions()
prefs = {"profile.default_content_setting_values.notifications" : 2}
chrome_options.add_experimental_option("prefs",prefs)

keywords = [
   "cần tìm", "cần mua", "muốn mua", "muốn tìm", "tìm nhà", "tìm đất", "tìm mua", "tìm mảnh", "cần mảnh", "minh quang", "thôn dy", "suối hai", "cẩm lĩnh"
]
driver = webdriver.Chrome(executable_path="./chromedriver", chrome_options=chrome_options)


driver.get("https://www.facebook.com/")
# sử dụng extensions "クッキーJSONファイル出力 for Puppeteer" https://chrome.google.com/webstore/detail/%E3%82%AF%E3%83%83%E3%82%AD%E3%83%BCjson%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB%E5%87%BA%E5%8A%9B-for-puppet/nmckokihipjgplolmcmjakknndddifde để xuất json cookies
file = open('fb.json')
cookies = json.load(file)
file.close()
for cookie in cookies:
    driver.add_cookie(cookie)

count = 0
while True:
    try:
        driver.get("https://www.facebook.com/notifications")

        time.sleep(5)
        unread_btn = driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[2]/div/div[1]/div/div/div/div[1]/div[3]/div[1]/div[2]/div/span/span')
        unread_btn.click()

        time.sleep(3)
        news_btn = driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[2]/div/div[1]/div/div/div/div[1]/div[3]/div[2]/div/div/div[2]/div[1]')
        news_btn.click()
        count += 1

        time.sleep(5)

        post = driver.find_element(By.CSS_SELECTOR, "span[class='x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x3x7a5m x6prxxf xvq8zen xo1l8bm xzsf02u x1yc453h']")
        

        if "See more" in post.text:
            seemore_btn = driver.find_element(By.CSS_SELECTOR, "div[class='x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xt0b8zv xzsf02u x1s688f']")
            seemore_btn.click()

        post_text = driver.find_element(By.CSS_SELECTOR, "span[class='x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x3x7a5m x6prxxf xvq8zen xo1l8bm xzsf02u x1yc453h']").text
        post_text = post_text.lower()

        for keyword in keywords:
            if keyword in post_text:
                post_url = driver.current_url
                list_str = post_url.split("/")

                print(f"Keyword: {keyword} in post {count}")
                print(f"Post URL: {post_url} tại group {list_str[4]}")
                print("*******")
                print(post_text)
                print("--------------------------")
                # creates SMTP session
                s = smtplib.SMTP('smtp.gmail.com', 587)
                
                # start TLS for security
                s.starttls()
                
                # Authentication
                s.login(sender_mail, password)
                
                # message to be sent
                msg = EmailMessage()
                msg.set_content(f'Tìm thấy từ khóa "{keyword}" trong bài viết {count} tại group: {list_str[4]} \nLink bài viết: {post_url} \n Nội dung bài viết:\n{post_text}')

                msg['Subject'] = 'Thông báo về từ khóa trên group facebook'
                msg['From'] = "1nguyenhuuhieu@gmail.com"
                msg['To'] = "huuhieung90@gmail.com"
                
                # sending the mail
                s.send_message(msg)
                
                # terminating the session
                s.quit()


            else:
                print(f"Not found '{keyword}' in post {count}")


    except:
        print("Try again")

