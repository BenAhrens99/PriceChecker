import difflib
import json
import re
import threading
import time
import tkinter as tk
import cv2 as cv
import numpy as np
import pyautogui as auto
import PySimpleGUI as sg
import pytesseract as tr
import requests as r
from overlay import Window
from PIL import Image, ImageOps
from pynput.keyboard import Key, Listener
from updateDB import updateItemsParallel
from updateDB import csvFileToList
inventory = []
resultList = []
nameList, urlList, priceList = csvFileToList()
t0 = time.time()
def updateList():
    updateItemsParallel()
    nameList, urlList, priceList = csvFileToList()
    return nameList,urlList
def checkResults(screenRegion, pageSegmentMode):
    t3 = time.time()
    im2 = auto.screenshot(region=screenRegion)
    im2 = ImageOps.grayscale(im2)
    im2 = im2.resize([im2.width * 3, im2.height * 3])

    #Convert to Black and White
    im_gray = np.array(im2.convert('L'))
    thresh = 128
    maxval = 255
    im_bool = (im_gray > thresh) * maxval
    binary = Image.fromarray(np.uint8(im_bool))
    binary.save('C:\\Users\\BpA\\Desktop\\Projects\\pyAutoGUI\\test.png')
    t2 = time.time()
    print(t3-t2)
    text = tr.image_to_string(binary, config='--oem 3 --psm ' + pageSegmentMode + '\
        -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz') #Using PSM 7 for single item (i.e inventory) and PSM 12 for a line of items, i.e reward screen
    listOfText = text.split('\n')
    t2 = time.time()
    print(t3 - t2)
    print(listOfText)
    return(listOfText)


def checkSimilar(itemName, list):
    result = difflib.get_close_matches(itemName,list, n = 1, cutoff=0.6)
    if result:
        getItemPrice(result, list)
    else:
        result = difflib.get_close_matches((itemName + " Blueprint"),list, n=1,cutoff=0.75)
        if result:
            getItemPrice(result, list)
def getItemPrice(result, list):
    return priceList[list.index(result)]
def on_press(key):
    if hasattr(key, 'char'):
        if key.char == '0':
            text = checkResults([460,410,990,50],'12')
            #Check all rewards, get prices
            for t in text:
                checkSimilar(t, nameList)   
listener = Listener(on_press=on_press)
checkSimilar("braton prime stock", nameList)
listener.start()