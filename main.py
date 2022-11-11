import difflib
import pyautogui as auto
import cv2 as cv
import numpy as np
from numpy import asarray
import pytesseract as tr
from PIL import Image, ImageOps
import requests as r
import re
import json
from pynput.keyboard import Listener, Key
import PySimpleGUI as sg
import threading
import time
from overlay import Window
import tkinter as tk
def createWindow():
    win.hide()
    itemFont = ("Roboto",20,'bold')
    win.launch()
nameList = []
inventory = []
resultList = []
win = Window(alpha=0.7)
createWindow()
t0 = time.time()
def updateList():
    f = open("Relics.json",encoding="utf8")
    items = json.loads(f.read())
    urlList = []
    for i in items:
        for reward in i['rewards']:
            itemName = reward['item']['name']
            nameList.append(itemName)
            try: 
                itemURL = reward['item']['warframeMarket']['urlName']
            except KeyError:
                itemURL = ("N/A")
                #Reward doesn't have a warframeMarket link
            urlList.append(itemURL)
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

def getItemPrice(result, list):
    name = urlList[list.index(result[0])]
    if name != "N/A":
        #x = r.get('https://warframe.market/items/'+ name)
        x = r.get('https://api.warframe.market/v1/items/' + name + '/orders').json()
        value = x['payload']['orders'][-1]['platinum']
        #results = re.search("Price: [0-9]{1,}", x.text)
        #TODO Store Value or Display Text
        resultList.append([result[0],value])
        label = tk.Label(win.root, text=result[0] +" Price: "+ str(value), background='grey',fg='black',font=itemFont)
        label.pack()
        print(result[0] +" Price: "+ str(value))
def checkSimilar(itemName, list):
    result = difflib.get_close_matches(itemName,list, n = 1, cutoff=0.6)
    if result:
        getItemPrice(result, list)
    else:
        result = difflib.get_close_matches((itemName + " Blueprint"),list, n=1,cutoff=0.75)
        if result:
            getItemPrice(result, list)

nameList, urlList = updateList()
def on_press(key):
    if hasattr(key, 'char'):
        if key.char == '0':
            resultList = []
            t0 = time.time()
            text = checkResults([460,410,990,50],'12')
            #Check all rewards, get prices
            for t in text:
                checkSimilar(t, nameList)
            print(resultList)
            t1 = time.time()
            print(t1-t0)
            win.position = 1350,270
            win.show()
listener = Listener(on_press=on_press)
listener.start()