import difflib
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

import updateDB as u

def updateList():
    global nameList, urlList, priceList
    u.writeToFile(u.updateItemsParallel())
try:
    nameList, urlList, priceList = u.csvFileToList()
except FileNotFoundError:
    print("No file currently loaded, Creating now")
    updateList()
    nameList, urlList, priceList = u.csvFileToList()

def checkResults(screenRegion, pageSegmentMode):
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
    text = tr.image_to_string(binary, config='--oem 3 --psm ' + pageSegmentMode + '\
        -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz') #Using PSM 7 for single item (i.e inventory) and PSM 12 for a line of items, i.e reward screen
    listOfText = text.split('\n')
    print(listOfText)
    return(listOfText)


def checkSimilar(itemName, list):
    result = difflib.get_close_matches(itemName,list, n = 1, cutoff=0.6)
    return getItemPrice(result[0], list)
    
def getItemPrice(result, list):
    price = priceList[list.index(result)]
    print(result + " Price: " + price)
    return price
def on_press(key):
    if hasattr(key, 'char'):
        if key.char == '0':
            text = checkResults([460,410,990,50],'12')
            #Check all rewards, get prices
            for t in text:
                checkSimilar(t, nameList)
        if key.char == '9':
            updateList()
        if key.char == '8':
            checkSimilar("Braton Prime Stock", nameList)
listener = Listener(on_press=on_press)
listener.start()
listener.join()