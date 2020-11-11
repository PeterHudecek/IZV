import requests
from bs4 import BeautifulSoup
from os import path
import zipfile
import os
import numpy as np
import csv
from io import TextIOWrapper
from timeit import default_timer as timer
import pickle
import gzip as gz

def isFloat(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

def isInt(string):
    try:
        int(string)
        return True
    except ValueError:
        return False


class  DataDownloader:


     
    def __init__(self, url="https://ehw.fit.vutbr.cz/izv/",folder="data", cache_filename="data_{}.pkl.gz"):
        self.url = url
        self.folder = folder
        self.cache_filename = cache_filename

    def download_data(self):
        r = requests.get(self.url, stream=True, headers={"User-Agent":"Mozilla/5.0"})
        soup = BeautifulSoup(r.content, 'html.parser')
        b = soup.find_all('a', class_='btn btn-sm btn-primary', href=True)
        b.reverse()
        newestflag = True
        if not os.path.exists(self.folder):
            os.mkdir(self.folder)

        for a in b:
            if newestflag == True:
                re = requests.get(self.url + a['href'])
                with open(a['href'],'wb') as f:
                   for chunk in re.iter_content(chunk_size=128):
                       if chunk:
                         f.write(chunk)
                   newestflag = False
            elif a['href'].find("01-") != -1:
                newestflag = True

    def parse_region_data(self, region):
        regiondict = {
            "PHA": "00.csv",
            "STC": "01.csv",
            "JHC": "02.csv",
            "PLK": "03.csv",
            "KVK": "19.csv",
            "ULK": "04.csv",
            "LBK": "18.csv",
            "HKK": "05.csv",
            "PAK": "17.csv",
            "OLK": "14.csv",
            "MSK": "07.csv",
            "JHM": "06.csv",
            "ZLK": "15.csv",
            "VYS": "16.csv"
        }

        header = ["p1","p36","p37","p2a","weekday(p2a)","p2b","p6","p7","p8","p9","p10","p11","p12","p13a",
        "p13b","p13c","p14","p15","p16","p17","p18","p19","p20","p21","p22","p23","p24","p27","p28","p34",
        "p35","p39","p44","p45a","p47","p48a","p49","p50a","p50b","p51","p52","p53","p55a","p57","p58","a",
        "b","d","e","f","g","h","i","j","k","l","n","o","p","q","r","s","t","p5a"]


        templist = [[] for _ in range(65)]
        finallist = [[] for _ in range(65)]

        for filename in os.listdir(self.folder):
            if filename.endswith(".zip"):
                tempzip = zipfile.ZipFile(self.folder + '/' + filename,"r")

                with tempzip.open(regiondict.get(region), 'r') as f:
                    reader = csv.reader(TextIOWrapper(f,"windows-1250"), delimiter=";")
                    for row in reader:
                        for i in range(64):
                            if i in range(0,3) or i in range(4,45) or i in range(60,62) or i == 63:
                                #int
                                if isInt(row[i]):
                                    templist[i].append(row[i])
                                else:
                                    templist[i].append('-1')

                            elif i == 3:
                                #date
                                templist[i].append(row[i])

                            elif i in range(45,51) or i == 57:
                                #float
                                tempvar = row[i].replace(',','.')
                                if isFloat(tempvar):
                                    templist[i].append(tempvar)
                                else:
                                    templist[i].append("-1")

                            elif i in range(51,57) or i in range(59,60) or i == 62:
                                #string
                                templist[i].append(row[i])
                                
                        templist[64].append(region)
       
        for i in range(65):
                           if i in range(0,3) or i in range(4,45) or i in range(60,62) or i == 63:
                                #int
                                finallist[i] = np.array(templist[i], dtype=np.int64)
                           elif i == 3:
                                #date
                                finallist[i] = np.array(templist[i], dtype=np.datetime64)
                           elif i in range(45,51) or i == 57:
                                #float
                                finallist[i] = np.array(templist[i], dtype=np.float64)
                           elif i in range(51,57) or i in range(58,60) or i == 62 or i == 64:
                                #string
                                finallist[i] = np.array(templist[i])

        regiontuple = (header,finallist)
        return regiontuple

    def get_list(self, regions = None):
        #if none regions were specified, every region is used
        if regions == None:
            regions = ["PHA","STC","JHC","PLK","KVK","ULK","LBK","HKK","PAK","OLK","MSK","JHM","ZLK","VYS"]

        header = ["p1","p36","p37","p2a","weekday(p2a)","p2b","p6","p7","p8","p9","p10","p11","p12","p13a",
        "p13b","p13c","p14","p15","p16","p17","p18","p19","p20","p21","p22","p23","p24","p27","p28","p34",
        "p35","p39","p44","p45a","p47","p48a","p49","p50a","p50b","p51","p52","p53","p55a","p57","p58","a",
        "b","d","e","f","g","h","i","j","k","l","n","o","p","q","r","s","t","p5a"]
        lists = [[] for _ in range(65)]
        finaltuple = (header,lists)

        for region in regions:
            #if cache file for current region already exists load from cache
            if os.path.isfile(self.cache_filename.format(region)):
                with open(self.cache_filename.format(region),'rb') as f:
                    temptuple = pickle.load(f)
            #if it doesnt, parse zipfiles from data folder and load it into cache
            else: 
                temptuple = self.parse_region_data(region)
                with open(self.cache_filename.format(region),'wb') as f:
                    pickle.dump(temptuple, f)

            #append current region from regions into final tuple
            for i in range(65):
                if i == 3:
                    try:
                        finaltuple[1][i] = np.concatenate((finaltuple[1][i],temptuple[1][i]), axis=None)
                    except TypeError:
                       finaltuple[1][i] = np.array(temptuple[1][i], dtype=np.datetime64) 
                else:
                    finaltuple[1][i] = np.concatenate((finaltuple[1][i],temptuple[1][i]), axis=None)

        print(finaltuple[1][0].size)
        return finaltuple 



