from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time

def reserve_ticket(driver, target_idxs):
    wait = WebDriverWait(driver, 30)
    is_ticket_found = False

    while not is_ticket_found:
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn_inq a"))).click()
        wait.until(EC.visibility_of_element_located((By.ID, "tableResult")))

        is_ticket_found = reverve_ticket_once(driver, target_idxs)
        time.sleep(1)

    return is_ticket_found

def reverve_ticket_once(driver, target_idxs):
    tbody = driver.find_element(By.XPATH, "//*[@id='tableResult']/tbody")
    rows = tbody.find_elements(By.TAG_NAME, "tr")

    for i in range(1, len(rows)+1):
        if (i-1) in target_idxs:
            reservation_button = get_button(driver, i)
            if reservation_button is not None:
                reservation_button.click()
                try:
                    modal_handler(driver)
                except:
                    return True

                return True
    return False

def get_button(driver, index):
    try:
        regular_seat_element = driver.find_element(By.XPATH, f"//*[@id='tableResult']/tbody/tr[{index}]/td[6]")
        regular_seat_img = regular_seat_element.find_element(By.TAG_NAME, "img")
        alt_regular = regular_seat_img.get_attribute("alt")

        if alt_regular == "예약하기":
            return regular_seat_element.find_element(By.TAG_NAME, "a")
        else:
            return None
    except NoSuchElementException:
        return None

def modal_handler(driver):
    wait = WebDriverWait(driver, 30)
    try:
        wait.until(EC.visibility_of_element_located((By.ID, "korail-modal-traininfo")))
        modal = driver.find_element(By.ID, "korail-modal-traininfo")
        
        if modal.is_displayed():
            iframe = modal.find_element(By.TAG_NAME, "iframe")
            driver.switch_to.frame(iframe)
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".cont p.btn_c a"))).click()
            driver.switch_to.default_content()
    except:
        pass