from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options as options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep, time
import selenium.common.exceptions as SEX
import pyautogui
import tkinter as tk
from tkinter import filedialog
import os

class FirefoxDriver:
    def __init__(self):
        ops = options()
        ops.headless = False
        self.drv = webdriver.Firefox(options=ops)
        self.drv.implicitly_wait(10)
        self.html = ""

    def _check_xpath(self, xpath):
        def condition(locator):
            p = EC.presence_of_element_located(locator)
            c = EC.element_to_be_clickable(locator)
            v = EC.visibility_of_element_located(locator)
            return p and c and v
        element = WebDriverWait(self.drv, 10).until(
            condition((By.XPATH, xpath)))
        return element

    def _action_click(self, element):
        self.drv.execute_script(
            "arguments[0].scrollIntoView();", element)
        ActionChains(self.drv)\
            .click(element)\
            .perform()

    def _action_post(self, element, word):
        self.drv.execute_script(
            "arguments[0].scrollIntoView();", element)
        ActionChains(self.drv)\
            .click(element)\
            .send_keys(word)\
            .perform()
    
    def get(self, url):
        self.drv.get(url)
        self.html = self.drv.page_source
    
    def quit(self):
        self.drv.quit()

    def click(self, xpath):
        bt = self._check_xpath(xpath)
        try:
            self._action_click(bt)
        except SEX.StaleElementReferenceException:
            bt = self._check_xpath(xpath)
            self._action_click(bt)
        self.html = self.drv.page_source

    def post(self, xpath, word):
        field = self._check_xpath(xpath)
        try:
            self._action_post(field, word)
        except SEX.StaleElementReferenceException:
            field = self._check_xpath(xpath)
            self._action_post(field, word)
        self.html = self.drv.page_source

    def upload(self, xpath, file):
        field = self._check_xpath(xpath)
        try:
            self._action_click(field)
        except SEX.StaleElementReferenceException:
            field = self._check_xpath(xpath)
            self._action_click(field)
        pyautogui.sleep(3)
        pyautogui.typewrite(file + '\n')
        pyautogui.sleep(3)
        pyautogui.press('enter')
        self.html = self.drv.page_source

    def clear(self, xpath):
        field = self._check_xpath(xpath)
        self.drv.execute_script("arguments[0].scrollIntoView();",
                field)
        ActionChains(self.drv)\
            .move_to_element(field)\
            .click(field)\
            .key_down(Keys.COMMAND)\
            .send_keys(Keys.UP)\
            .key_up(Keys.COMMAND)\
            .perform()
        self.html = self.drv.page_source


def send_email(file):
    driver = FirefoxDriver()
    driver.get("https://account.proton.me/login")
    driver.post("//*[@id=\"username\"]", "dummy8V")
    driver.post("//*[@id=\"password\"]", "rRhkE6HLJr9hypW")
    driver.click("/html/body/div[1]/div[4]/div[1]/div/main/div[2]/form/button")
    #  Composing a message
    driver.click("/html/body/div[1]/div[3]/div/div[2]/div/div[1]/div[2]/button")
    driver.post("//*[@data-testid=\"composer:to\"]", "dummy8V@proton.me")
    driver.click("/html/body/div[1]/div[4]/div/div/div/div/div/div[3]")
    driver.post("//*[@data-testid=\"composer:subject\"]", "lol")
    driver.clear("/html/body/div[1]/div[4]/div/div/div/div/section/div/div[1]/div[1]/div/iframe")
    driver.post("/html/body/div[1]/div[4]/div/div/div/div/section/div/div[1]/div[1]/div/iframe", 
            "This is a automated message.")
    driver.upload("//*[@data-testid=\"composer:attachment-button\"]",
            file)
    sleep(5)
    driver.click("/html/body/div[1]/div[4]/div/div/div/footer/div/div[1]/button[1]")
    # Looking at the message
    sleep(35)
    driver.click("/html/body/div[1]/div[3]/div/div[2]/div/div[1]/div[4]/nav/div/ul/div[3]/li")
    driver.click("/html/body/div[1]/div[3]/div/div[2]/div/div[2]/div/div/div/main/div/div[1]/div/div[1]/div/button[3]")
    driver.click("/html/body/div[1]/div[3]/div/div[2]/div/div[2]/div/div/div/main/div/div[1]/div/div[2]/div")
    driver.click("//*[@data-testid=\"attachment-list:download-all\"]")
    # Deleting a message
    driver.click("/html/body/div[1]/div[3]/div/div[2]/div/div[2]/div/div/div/main/section/div/div[3]/div/div/div/article/div[1]/div[4]/div[1]/div/button[2]")
    sleep(5)
    # Quiting
    driver.quit()


def main():
    def send_file(event=None):
        filename = entry.get()
        if filename.strip() == "":
            error_label.config(text="Пожалуйста введите имя файла", fg="red")
            return
        if not os.path.isfile(filename):
            error_label.config(text=f"Файла с именем '{filename}' не существует.")
            return
        print(f"Отправляется файл: {filename}")
        popup.destroy()
        send_email(filename)

    def browse_file():
        filename = filedialog.askopenfilename()
        if filename:
            entry.delete(0, tk.END)
            entry.insert(0, filename)

    # Create the popup window
    popup = tk.Tk()

    # Set the window title
    popup.title("Имя файла для отправки")

    # Create the text entry field
    entry = tk.Entry(popup)
    entry.pack(pady=15, padx=10, anchor='center')
    entry.bind('<Return>', send_file)

    # Create the "Browse" button
    browse_button = tk.Button(popup, text="Browse", command=browse_file)
    browse_button.pack()

    # Create the "Submit" button
    submit_button = tk.Button(popup, text="Подтвердить", command=send_file)
    submit_button.pack(pady=10, padx=10, anchor='center')

    # Create the error label
    error_label = tk.Label(popup, text="", fg="red")
    error_label.pack()

    # Set the size of the window and center it on the screen
    window_width = 300
    window_height = 140
    screen_width = popup.winfo_screenwidth()
    screen_height = popup.winfo_screenheight()
    x = int((screen_width/2) - (window_width/2))
    y = int((screen_height/2) - (window_height/2))
    popup.geometry(f"{window_width}x{window_height}+{x}+{y}")

    # Run the main loop to display the window
    popup.mainloop()


main()
