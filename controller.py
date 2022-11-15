from concurrent.futures import ThreadPoolExecutor
import difflib
import json
import time
import requests as r
from re import search
import csv
import os
from PIL import ImageOps, Image
import numpy as np
from pytesseract import image_to_string
from win32 import win32gui
import win32ui
import win32con
FILENAME = 'test.txt'


class DBcontroller:
    nameList, urlList, priceList = None, None, None
    def __init__(self):
        try:
            self.csvFileToList()
        except FileNotFoundError:
            print("No file currently loaded, Creating now")
            self.writeToFile(self.updateItemsParallel())
            self.csvFileToList()

    def http_get_price(self,url: str, urlName: str, name: str):
        x = r.get(url).json()
        try:
            orders = x['payload']['orders']
            count = 0
            plat = 0
            for o in orders:
                quant = o['quantity']
                plat = plat + (o['platinum'] * quant)
                count = count + (1 * quant)
            value = round(plat / count)
        except IndexError:
            value = 0
        formattedString = urlName + "  " + name + "  Price: " + str(value)
        print(formattedString)
        #Slows it down for the 3 requests per second limit
        time.sleep(0.5)
        return urlName, name, value
    def updateItemsParallel(self):
        x = r.get('https://api.warframe.market/v1/items').json()
        items = x['payload']['items']
        httpList = []
        urlList = []
        nameList = []
        for item in items:
            urlName = item['url_name']
            if search("(prime[^d])(?!set)", urlName):
                name = item['item_name']
                httpList.append('https://api.warframe.market/v1/items/' + urlName + '/orders')
                urlList.append(urlName)
                nameList.append(name)
        #Put it all into a file
        return self.http_get_with_requests_parrallel(httpList, urlList, nameList)
    def http_get_with_requests_parrallel(self,list_of_urls, list_of_names, list_of_url_names):
        results = []
        executor = ThreadPoolExecutor(max_workers=2)
        for result in executor.map(self.http_get_price, list_of_urls, list_of_url_names, list_of_names):
            results.append(result)
        return results
    def writeToFile(self,results):
    #Will most likely change to a actual database so it can pull images aswell, will impact refresh time so TBD
        try:
            os.remove(FILENAME)
        except FileNotFoundError:
            print("No file found, creating new one.")
        f = open(FILENAME, "a")
        for i in results:
            #0 = Name, 1 = URL, 2 = Price
            fname = i[0]
            furl = i[1]
            fprice = i[2]
            f.write(fname + "," + furl + "," + str(fprice) + "\n")
        #Kappa beacon
        f.write("Forma Blueprint,kappa_beacon,0")
        f.close()
    def csvFileToList(self): #TODO Find a more optimal way return the data
        with open(FILENAME) as csv_file:
            reader = csv.reader(csv_file,delimiter=',')
            data = list(reader)
            self.nameList,self.urlList,self.priceList = [sublist[0] for sublist in data], [sublist[1] for sublist in data], [sublist[2] for sublist in data]
    def checkSimilarAndGetPrice(self,itemName):
        result = difflib.get_close_matches(itemName,self.nameList, n = 1, cutoff=0.6)
        return self.getItemPrice(result[0])
    def getItemPrice(self,result):
        price = self.priceList[self.nameList.index(result)]
        print(result + " Price: " + price)
        return price


class WindowCapture:
    w = 0
    h = 0
    hwnd = None
    def __init__(self,windowName):
        self.hwnd = win32gui.FindWindow(None, windowName)
        if not self.hwnd:
            raise Exception('Window not found: {}'.format(windowName))
        self.w = 1920
        self.h = 1080
    def captureWindow(self):
        wDC = win32gui.GetWindowDC(self.hwnd)
        dcObj=win32ui.CreateDCFromHandle(wDC)
        cDC=dcObj.CreateCompatibleDC()
        dataBitMap = win32ui.CreateBitmap()
        dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0,0),(self.w, self.h) , dcObj, (0,0), win32con.SRCCOPY)
        signedIntsArray = dataBitMap.GetBitmapBits(False)
        img = np.array(signedIntsArray).astype(dtype="uint8")
        img.shape = (self.h, self.w, 4)
        img = img[...,:3]
        img = np.ascontiguousarray(img)
        return img

    def findResults(self, screenshot):
        #TODO Changing to game Capture, test will be chrome
        #im2 = auto.screenshot(region=screenRegion)
            im2 = Image.fromarray(screenshot)
            im2 = ImageOps.grayscale(im2)
            im2 = im2.resize([im2.width * 3, im2.height * 3])

            #Convert to Black and White
            im_gray = np.array(im2.convert('L'))
            thresh = 128
            maxval = 255
            im_bool = (im_gray > thresh) * maxval
            binary = Image.fromarray(np.uint8(im_bool))
            binary.save('test.png')
            #Save as image
            text = image_to_string(binary, config='--oem 3 --psm 1 \
                -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz') #Using PSM 7 for single item (i.e inventory) and PSM 12 for a line of items, i.e reward screen
            listOfText = text.split('\n')
            print(listOfText)
            return(listOfText)

