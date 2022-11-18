import difflib
import tkinter as tk
import cv2 as cv
import numpy as np
import pyautogui as auto
import PySimpleGUI as sg
import pytesseract as tr
import requests as r
import time
from overlay import Window
from PIL import Image, ImageOps, ImageGrab
from pynput.keyboard import Key, Listener
from controller import DBcontroller, WindowCapture
global nameList, urlList, priceList

wc = WindowCapture('Warframe')
c = DBcontroller()


def on_press(key):
    if hasattr(key, 'char'):
            if key.char == '0':
                t0 = time.time()
                results = wc.findResults(wc.captureWindow())
                for r in results:
                    c.checkSimilarAndGetPrice(r)
                print("Done!")
                t1 = time.time()
                print(t1 - t0)
            if key.char == '9':
                c.writeToFile(c.updateItemsParallel())
                c.csvFileToList()
listener = Listener(on_press=on_press)
listener.start()
listener.join()