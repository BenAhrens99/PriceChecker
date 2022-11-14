from concurrent.futures import ThreadPoolExecutor
import json
import time
import requests as r
from re import search
import csv
import os
FILENAME = 'test.txt'
def http_get_price(url: str, urlName: str, name: str):
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
    time.sleep(0.3)
    return urlName, name, value


def http_get_with_requests_parrallel(list_of_urls, list_of_names, list_of_url_names):
    results = []
    executor = ThreadPoolExecutor(max_workers=3)
    for result in executor.map(http_get_price, list_of_urls, list_of_url_names, list_of_names):
        results.append(result)
    return results

def updateItemsParallel():
    x = r.get('https://api.warframe.market/v1/items').json()
    items = x['payload']['items']
    httpList = []
    urlList = []
    nameList = []
    for item in items:
        urlName = item['url_name']
        if search("(prime[^d][^s])", urlName):
            name = item['item_name']
            httpList.append('https://api.warframe.market/v1/items/' + urlName + '/orders')
            urlList.append(urlName)
            nameList.append(name)
    #Put it all into a file
    return http_get_with_requests_parrallel(httpList, urlList, nameList)

    print("Done!")
def writeToFile(results):
    try:
        os.remove(FILENAME)
    except FileNotFoundError:
        print("No file found, creating new one.")
    f = open(FILENAME, "a")
    f.write("name,url,price\n")
    for i in results:
        #0 = Name, 1 = URL, 2 = Price
        fname = i[0]
        furl = i[1]
        fprice = i[2]
        f.write(fname + "," + furl + "," + str(fprice) + "\n")
    f.close()
def csvFileToList(): #TODO
    with open(FILENAME) as csv_file:
        reader = csv.reader(csv_file,delimiter=',')
        data = list(reader)
    return data
#Create a List in a file with ItemName, price and URL