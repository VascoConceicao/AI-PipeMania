import pyautogui
import time

x = 2286
y = 330

pyautogui.moveTo(x, y)
pyautogui.scroll(-300)

time.sleep(2)
pyautogui.scroll(-100)

x = 3015
y = 986
pyautogui.moveTo(x, y)
pyautogui.click()
