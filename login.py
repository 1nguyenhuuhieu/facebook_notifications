# selenium 4
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))

driver.get("https://www.facebook.com/")

login_input = driver.find_element(By.XPATH, '//*[@id="email"]')
login_input.send_keys("tam@Durex.c0m3")

pwd_input = driver.find_element(By.XPATH, '//*[@id="pass"]')
pwd_input.send_keys("HUXE ICZN 2K3J 7HWI 5TUN EUAF WKIP UBEZ")