# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 16:28:21 2019

@author: justRandom / Andreas Kellermann

##TODO: Find a way to sort that messy table 
##TODO: Start program with arguments?
##TODO: Improve notification, popup window or similar...
##TODO: Documentation (?)

"""

import requests
import lxml.html as lh
import pandas as pd
import os
import sys
import re

# Get user inputs
url = ''
searchTerms = []
onlyNew = True

while(True):
    userInput = sys.argv
    if userInput[1] == '-help' or userInput[1] == '--help':
        print('\
              usage: reitkalender [url] [option] ... [-s search][-s search] ... \n \
              [url] : Website Link with html table on reitkalender, eg: "https://www.reitkalender.ch/abfragen/patrouillenritt_termine.asp"\n \
              -all  : option, displays all data, default is only new data \n \
              -s    : Search Term (can use multiple search terms) \n\n\
              simple example to run: "reitkalender -w https://www.reitkalender.ch/abfragen/patrouillenritt_termine.asp -all -s AG -s ZH \
              ')     
        exit()        
    else:
         #search file
         url = userInput[1]
         if str(userInput).find('-all') is not -1:
            onlyNew = False
                  
         sPos = []
         if str(userInput).find('-s') is not -1:
             sPos = userInput.index('-s')
             for i in range(len(userInput)):
                 if userInput[i] == '-s':
                     searchTerms.append(userInput[i+1])
         break


#Get data from reitkalender website
##url='https://www.reitkalender.ch/abfragen/patrouillenritt_termine.asp'
page = requests.get(url)
doc = lh.fromstring(page.content)
tr_elements = doc.xpath('//tr')
[len(T) for T in tr_elements[:12]]
tr_elements = doc.xpath('//tr')
col=[]
i=0

#Parse Website Data into List
eventList = []
for i in range(len(tr_elements)):
    eventStr = ''
    for j in tr_elements[i]:    
        buf = str(j.text_content()).strip('        \r\n').replace('\xa0', ', ')
        eventStr += (buf + ', ') 
    eventList.append(eventStr[:-2].split(','))
tableHead = eventList[-0]
eventList = eventList[1:] #Remove Table head since it is incomplete anyway


#Search List and remove all which do not match (if search terms are specified...)
getLine = []
if len(searchTerms) != 0:
    for i in range(len(eventList)):
        flag = False
        lineStr = ' '.join(eventList[i])
        for k in range(len(searchTerms)):      
            if lineStr.lower().find(str(searchTerms[k]).lower()) is not -1 and flag is False:
                getLine.append(i)
                flag = True

bufferList = []
for i in range(len(getLine)):
    bufferList.append(eventList[getLine[i]])
eventList = bufferList


#Make Path Relative
script_dir = os.path.dirname(__file__) #absolute dir the script is in
rel_path = "patrouillien.csv" #file name
abs_file_path = os.path.join(script_dir, rel_path)

# Open File with CVS Table
file = open(abs_file_path, "r")
csvList = file.read()
file.close()

# Search for new events
# Check if Event is already in CVS
newEvents = ''
newEventsCounter = 0
for i in range(len(eventList)):
    if csvList.find(str(eventList[i][5])) == -1:
        newEvents += (','.join(eventList[i]) + '\n')
        newEventsCounter += 1
        
#Nice Table and table head
headList = ['Datum', ' Nennschluss', ' PLZ', ' Ort', ' Kanton', ' Name']
head = '' 
for j in range(len(headList)):
    head += '{0: <20}'.format(headList[j])

#Output String
outStr = ''
#Only new events in console
if newEventsCounter > 0 or onlyNew is True:
    outStr += str(newEventsCounter) + " neue Events gefunden!\n\n" + head + "\n" + str(newEvents) 
#Print all events in console
if onlyNew is False:
    strEventList = ''
    for i in range(len(eventList)):
        for j in range(len(eventList[i])):
            strEventList += '{0: <20}'.format(eventList[i][j])
        strEventList += '\n'
    outStr += str(len(eventList)) + " Events gefunden!\n\n" + head + "\n" + strEventList
    
#Print in console TODO: Replace with popup
print(outStr)

#Dialog for overwriting old events
if newEventsCounter > 0 and onlyNew is True:    
    # Replace Table?
    print("Neue Termine notiert? CVS Liste überschreiben? [y/n]")
    if input() == 'y':
        file = open(abs_file_path, "w")
        # Write new Events into CSV
        for element in range(len(eventList)):
            file.write(', '.join(eventList[element]) + '\n')
        file.close()
    print()  
    
    
        