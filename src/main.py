from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time, re, os
from reserve import *
from telbot import TelegramBot

from tabulate import tabulate
tabulate.WIDE_CHARS_MODE = False

from dotenv import load_dotenv
load_dotenv()
korail_id = os.getenv("KORAIL_ID")
korail_pw = os.getenv("KORAIL_PW")

# initialize webdriver by using ChromeDriverManager
def initialize_webdriver(headless=True):
    service = Service(ChromeDriverManager().install())
    
    options = Options()
    if headless:
        options.add_argument("--headless")
    
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(1680, 1050)
    
    return driver

# login with given id and password, and move to the reservation page
def login(driver, id, pw):
    wait = WebDriverWait(driver, 30)
    driver.get("https://www.letskorail.com/korail/com/login.do")

    wait.until(EC.presence_of_element_located((By.ID, "txtMember"))).send_keys(id)
    wait.until(EC.presence_of_element_located((By.ID, "txtPwd"))).send_keys(pw)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn_login a"))).click()

    wait.until(EC.url_contains("https://www.letskorail.com/index.jsp"))

    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".first a"))).click()

# set ticket search criteria with given start station, end station, month, day, and hour
def set_criteria(driver, start_station, end_station, month, day, hour):
    wait = WebDriverWait(driver, 30)

    start_element = wait.until(EC.presence_of_element_located((By.ID, "start")))
    start_element.clear()
    start_element.send_keys(start_station)

    end_element = wait.until(EC.presence_of_element_located((By.ID, "get")))
    end_element.clear()
    end_element.send_keys(end_station)

    Select(driver.find_element(By.NAME, "selGoMonth")).select_by_value(month)
    Select(driver.find_element(By.NAME, "selGoDay")).select_by_value(day)
    Select(driver.find_element(By.NAME, "selGoHour")).select_by_value(hour)

# print schedules with given start station, end station, month, day, and hour
def print_schedules(driver, start_station, end_station, month, day, hour):
    set_criteria(driver, start_station, end_station, month, day, hour)
    wait = WebDriverWait(driver, 30)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn_inq a"))).click()
    wait.until(EC.visibility_of_element_located((By.ID, "tableResult")))

    schedules = driver.find_elements(By.CSS_SELECTOR, "#tableResult tbody tr")

    table = []
    for schedule in schedules:
        table.append(parse_schedule(schedule))

    headers = ["열차번호", "출발시간", "도착시간", "요금", "소요시간"]

    print(tabulate(table, headers, tablefmt='fancy_grid', showindex="always"))
    return table

# parse schedule information
def parse_schedule(schedule):
    arr = []

    train_no = re.split("\n| ", schedule.find_elements(By.TAG_NAME, "td")[1].text)
    if len(train_no) == 1:
        arr.append(train_no[0])
    else:
        arr.append(f'{train_no[1]}({train_no[0]})')

    start_time = re.split("\n| ", schedule.find_elements(By.TAG_NAME, "td")[2].text)
    arr.append(f"{start_time[1]}({start_time[0]})")

    end_time = re.split("\n| ", schedule.find_elements(By.TAG_NAME, "td")[3].text)
    arr.append(f"{end_time[1]}({end_time[0]})")

    price = re.split("\n| ", schedule.find_elements(By.TAG_NAME, "td")[8].text)
    arr.append(price[0])

    time = re.split("\n| ", schedule.find_elements(By.TAG_NAME, "td")[13].text)
    arr.append(time[0])

    return arr

if __name__ == "__main__":     
    driver = initialize_webdriver()
    login(driver, korail_id, korail_pw)

    print("출발역, 도착역, 월, 일, 시간을 입력하세요")
    print("ex) 서울 부산 11 05 07")
    start_station, end_station, month, day, hour = input().split()
    table = print_schedules(driver, start_station, end_station, month, day, hour)

    # table = print_schedules(driver, "서울", "부산", "11", "05", "10")

    print("예약을 원하는 열차의 번호를 입력하세요")
    print("ex) 5 / 4, 5, 6")
    table_idxs = [int(num.strip()) for num in input().split(',')]

    # table_idxs = [9]s

    print(table_idxs, "의 열차를 예약합니다.")
    if reserve_ticket(driver, table_idxs):
        print("예약 성공")
        time.sleep(10)

    

