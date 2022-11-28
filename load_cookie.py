import json
import random
import time
from selenium.webdriver.common.by import By
from selenium import webdriver
import pyperclip

keyword = [
   "cần tìm", "cần mua", "muốn mua", "muốn tìm", "tìm nhà", "tìm đất", "tìm mua", "tìm mảnh", "cần mảnh", "minh quang", "thôn dy", "suối hai", "cẩm lĩnh"
]
driver = webdriver.Chrome(executable_path="./chromedriver")


driver.get("https://www.facebook.com/")
# sử dụng extensions "クッキーJSONファイル出力 for Puppeteer" https://chrome.google.com/webstore/detail/%E3%82%AF%E3%83%83%E3%82%AD%E3%83%BCjson%E3%83%95%E3%82%A1%E3%82%A4%E3%83%AB%E5%87%BA%E5%8A%9B-for-puppet/nmckokihipjgplolmcmjakknndddifde để xuất json cookies
cookies = open('fb.json')
cookies = json.load(cookies)
for cookie in cookies:
    driver.add_cookie(cookie)


while True:
    try:
        driver.get("https://www.facebook.com/notifications")

        time.sleep(1)
        unread_btn = driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[2]/div/div[1]/div/div/div/div[1]/div[3]/div[1]/div[2]/div/span/span')
        unread_btn.click()

        time.sleep(3)
        news_btn = driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[2]/div/div[1]/div/div/div/div[1]/div[3]/div[2]/div/div/div[2]/div[1]')
        news_btn.click()

        time.sleep(5)
        share_btn = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div/div/div[1]/div/div/div[4]/div/div/div[2]/div/div/div/div[2]/div[2]/div[2]/div/div/div/div/div/div/div/div[1]/div/div[8]/div/div[4]/div/div/div[1]/div/div/div/div[3]/div')
        share_btn.click()
        time.sleep(1)
        copylink_btn = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[2]/div/div/div[1]/div[1]/div/div/div/div/div/div[1]/div/div[9]/div/div[1]')
        copylink_btn.click()
        time.sleep(1)
        post_url = str(pyperclip.paste())
        driver.get(post_url)
        time.sleep(5)
        post_text = driver.find_element(By.XPATH, '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div/div[1]/div[1]/div[4]/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div/div[8]/div/div[3]/div/div')

        print(post_text.text)
        print("--------------------------")
        file1 = open("report.txt", "a")  # append mode
        file1.write(str(post_text.text) + "\n" + "-----------------")
        file1.close()

        print("saved")
    except:
        print("Try again")