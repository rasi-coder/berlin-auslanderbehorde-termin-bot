import time
import os
import logging
from platform import system

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException


system = system()

logging.basicConfig(
    format='%(asctime)s\t%(levelname)s\t%(message)s',
    level=logging.INFO,
)


class WebDriver:
    def __init__(self):
        self._driver: webdriver.Chrome
        self._implicit_wait_time = 20

    def __enter__(self) -> webdriver.Chrome:
        logging.info("Open browser")
        # some stuff that prevents us from being locked out
        options = webdriver.ChromeOptions() 
        options.add_argument('--disable-blink-features=AutomationControlled')
        self._driver = webdriver.Chrome(options=options)
        self._driver.implicitly_wait(self._implicit_wait_time) # seconds
        self._driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self._driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
        return self._driver

    def __exit__(self, exc_type, exc_value, exc_tb):
        logging.info("Close browser")
        self._driver.quit()


class BerlinBot:
    def __init__(self):
        self.wait_time = 20
        self._sound_file = os.path.join(os.getcwd(), "alarm.wav")
        self._error_message = """Für die gewählte Dienstleistung sind aktuell keine Termine frei! Bitte"""

    @staticmethod
    def enter_start_page(driver: webdriver.Chrome):
        logging.info("Visit start page")
        driver.get("https://otv.verwalt-berlin.de/ams/TerminBuchen")
        driver.find_element(By.XPATH, '//*[@id="mainForm"]/div/div/div/div/div/div/div/div/div/div[1]/div[1]/div[2]/a').click()
        time.sleep(5)

    @staticmethod
    def tick_off_some_bullshit(driver: webdriver.Chrome):
        logging.info("Ticking off agreement")
        driver.find_element(By.XPATH, '//*[@id="xi-div-1"]/div[4]/label[2]/p').click()
        time.sleep(1)
        driver.find_element(By.ID, 'applicationForm:managedForm:proceed').click()
        time.sleep(5)

    @staticmethod
    def enter_form(driver: webdriver.Chrome):
        try:
            WebDriverWait(driver, 60).until(EC.invisibility_of_element((By.CLASS_NAME, 'loading')))

        except:
            return
        logging.info("Fill out form")

        # select Bosnien und Herzegowina
        s = Select(WebDriverWait(driver, 40).until(EC.element_to_be_clickable((By.ID, 'xi-sel-400'))))
        # s = Select(driver.find_element(By.ID, 'xi-sel-400'))
        try:
            s.select_by_visible_text("Bosnien und Herzegowina") #27
        except:
            return

        time.sleep(1)
        # eine person
        s = Select(driver.find_element(By.ID, 'xi-sel-422'))
        s.select_by_visible_text("eine Person")
        # no family
        s = Select(driver.find_element(By.ID, 'xi-sel-427' ))
        s.select_by_visible_text("nein")
        time.sleep(5)

        # extend stay
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="xi-div-30"]/div[2]/label/p'))).click()
        # driver.find_element(By.XPATH, '//*[@id="xi-div-30"]/div[2]/label/p').click()
        time.sleep(2)

        # # click on study group "studium und ausbildung"
        # WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="inner-122-0-2"]/div/div[@class="ozg-accordion accordion-122-0-2-3 level2"]/label/p'))).click()
        # # driver.find_element(By.XPATH,
        # #                     '//*[@id="inner-122-0-2"]/div/div[@class="ozg-accordion accordion-122-0-2-3 level2"]/label/p').click()
        # time.sleep(2)

        # OR click on Erwerbstaetigkeit
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH,
                                                                    '//*[@id="inner-122-0-2"]/div/div[@class="ozg-accordion accordion-122-0-2-1 level2"]/label'))).click()
        time.sleep(2)

        # # b/c of study "Aufenthaltserlaubnis für eine Berufsausbildung" 16a
        # WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="inner-122-0-2"]/div/div[@class="level2-content"][1]/div/div[@class="level3"][1]/label'))).click()

        # OR b/c of 18a
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH,
                                                                    '//*[@id="inner-122-0-2"]/div/div[@class="level2-content"][2]/div/div[@class="level3"][3]/label'))).click()

        # driver.find_element(By.XPATH, '//*[@id="inner-122-0-2"]/div/div[@class="level2-content"][1]/div/div[@class="level3"][1]/label').click()
        time.sleep(4)

        # submit form
        # WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, 'applicationForm:managedForm:proceed'))).click()
        try:
            weiter_link = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, 'applicationForm:managedForm:proceed')))
            weiter_link.click()

        except ElementClickInterceptedException:
            logging.info("Trying to click on the Weiter button again")
            driver.execute_script("arguments[0].click()", weiter_link)

        time.sleep(10)

        try:
            WebDriverWait(driver, 60).until(EC.invisibility_of_element((By.CLASS_NAME, 'loading')))
        except:
            return

    def _success(self):
        logging.info("!!!SUCCESS - do not close the window!!!!")
        while True:
            self._play_sound_osx(self._sound_file)
            time.sleep(15)
        
        # todo play something and block the browser

    def run_once(self):
        with WebDriver() as driver:
            try:
                self.enter_start_page(driver)
                self.tick_off_some_bullshit(driver)

                url_before = driver.current_url
                self.enter_form(driver)

                # retry submit
                for _ in range(10):
                    WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.ID, 'footer')))
                    url_after = driver.current_url
                    logging.info("Checking")
                    if not self._error_message in driver.page_source \
                            and not 'Familiäre Gründe' in driver.page_source \
                            and url_before != url_after:
                        current_window = driver.current_window_handle
                        driver.execute_script("alert(\"Focus window\")")
                        driver.switch_to.alert.accept()
                        driver.switch_to.window(current_window)
                        driver.fullscreen_window()
                        self._success()
                    time.sleep(10)
                    logging.info("Retry submitting form")
                    WebDriverWait(driver, 20).until(
                        EC.element_to_be_clickable((By.ID,
                                                    'applicationForm:managedForm:proceed'))).click()
                    try:
                        WebDriverWait(driver, 60).until(
                            EC.invisibility_of_element(
                                (By.CLASS_NAME, 'loading')))
                    except:
                        return
            except Exception as e:
                logging.error(e)
                driver.switch_to.window(driver.current_window_handle)

            # self.enter_start_page(driver)
            # self.tick_off_some_bullshit(driver)
            # self.enter_form(driver)
            #
            # # retry submit
            # for _ in range(10):
            #     if not self._error_message in driver.page_source:
            #         self._success()
            #     logging.info("Retry submitting form")
            #     driver.find_element(By.ID, 'applicationForm:managedForm:proceed').click()
            #     time.sleep(self.wait_time)

    def run_loop(self):
        # play sound to check if it works
        self._play_sound_osx(self._sound_file)
        while True:
            logging.info("One more round")
            self.run_once()
            time.sleep(self.wait_time)

    # stolen from https://github.com/JaDogg/pydoro/blob/develop/pydoro/pydoro_core/sound.py
    @staticmethod
    def _play_sound_osx(sound, block=True):
        """
        Utilizes AppKit.NSSound. Tested and known to work with MP3 and WAVE on
        OS X 10.11 with Python 2.7. Probably works with anything QuickTime supports.
        Probably works on OS X 10.5 and newer. Probably works with all versions of
        Python.
        Inspired by (but not copied from) Aaron's Stack Overflow answer here:
        http://stackoverflow.com/a/34568298/901641
        I never would have tried using AppKit.NSSound without seeing his code.
        """
        from AppKit import NSSound
        from Foundation import NSURL
        from time import sleep

        logging.info("Play sound")
        if "://" not in sound:
            if not sound.startswith("/"):
                from os import getcwd

                sound = getcwd() + "/" + sound
            sound = "file://" + sound
        url = NSURL.URLWithString_(sound)
        nssound = NSSound.alloc().initWithContentsOfURL_byReference_(url, True)
        if not nssound:
            raise IOError("Unable to load sound named: " + sound)
        nssound.play()

        if block:
            sleep(nssound.duration())


if __name__ == "__main__":
    BerlinBot().run_loop()
