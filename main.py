import difflib
import tkinter as tk
import cv2 as cv
import numpy as np
import pyautogui as auto
import PySimpleGUI as sg
import pytesseract as tr
import requests as r
from overlay import Window
from PIL import Image, ImageOps, ImageGrab
from pynput.keyboard import Key, Listener
from controller import DBcontroller, WindowCapture
global nameList, urlList, priceList

wc = WindowCapture('Untitled - Paint')
c = DBcontroller()


def on_press(key):
    if hasattr(key, 'char'):
            if key.char == '0':
                c.checkSimilarAndGetPrice(wc.findResults(wc.captureWindow()))
                print("Done!")
listener = Listener(on_press=on_press)
listener.start()
listener.join()