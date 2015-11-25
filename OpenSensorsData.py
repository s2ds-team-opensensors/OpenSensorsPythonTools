#!/usr/bin/env python2.7

## @package OpenSensorsPythonTools
# Tools to extract the data from OpenSensors API 

# Libraries
import pandas as pd
import json

import time
from datetime import datetime, timedelta

# Local Code
from OpenSensorsAPI import *

## Functions for test the data to determine it's type
#
# eg is it a  json, single number or something else
def is_number(valTest):
    
    try:
        float(valTest)
        return True
    except ValueError:
        pass
    
    return False


    
def is_json(valTest):
  
    try:
        float(valTest)
        return False
    except ValueError, TypeError:
        pass
    try:
        json_object = json.loads(valTest)
        return True
    except ValueError, e:
        pass
    return False    

## OpenSensors Data class
class OpenSensorsData():
    
    ## constructor.
    def __init__(self, opensensors):
        self.OS = opensensors



    ## Testing the API key is working
    def testAPIkey(self):
        
        try:
            
            print('OpenSensors User: %s' % self.OS.whoAmI())
            return True
        
        except requests.exceptions.HTTPError as exc:
            
            print ('A Connection error occurred with this API key.', exc)
            return False



    ## Lists the topics in an org, with the option to save it to a txt file
    def orgTopicList(self, org, displayList=False, saveFile=False, checkStructure=False):

        topicsJSON = self.OS.listOrgTopics(org)

        topicList = []
        
        if (checkStructure):
            print 'Topic list entry has the keys: ', topicsJSON[0].keys()
        
        for topicIter, topic in enumerate(topicsJSON):

            currentTopic = topic['topic']
            topicList.append(currentTopic)
            
            if (displayList):
                print ('%d - Topic name: %s' % (topicIter, currentTopic))

        if (saveFile):
            
            save_name = ('%s_topics.txt' % org)
            f = open(save_name, 'w')
            
            for topicIter, topic in enumerate(topicList):

                f.write('%d - Topic name: %s\n' % (topicIter, topic))

            f.close()
        
        return topicList



    ## Function to read from the first entry of the API, convert it to a panda df
    def dfMake(self, currentTopic, startTime=None, endTime=None, colList=None, checkStructure=False):

        print ('\n\nUsing topic: %s' % currentTopic )

        data = self.OS.getMsgsByTopic(currentTopic, startTime, endTime)
        
        # Variables for counting, checking types. Flag and 
        dfList = []
        dataType = -999
        entryNum = 0
        
        # Creates list for df columns
        colName = []
        if (colList):
            colName += colList
        
        else:
            colName += ['datetime']
            dataType = 0
        
        # Setting data type to JSON if more than 2 columns
        if (len(colName) > 2):
            dataType = 1
            entryNum = len(colName) - 1

        ## Looping over the data until there is no next url 
        while(data):

            for dataEntry in data['messages']:
            
                ## The code tests the first full entry to determin structure of data (Save info to file ???)
                if(dataType == 0):
                    
                    if (checkStructure):
                        print 'Data entry has the keys: ', dataEntry.keys()
                    
                    if (is_json(dataEntry['payload']['text'])):

                        textJSON = json.loads(dataEntry['payload']['text'])
                        if (len(textJSON) > 0):
                            print 'Data is JSON - Variables within are: ', textJSON.keys()
                            colName += textJSON.keys()
                            entryNum = len(textJSON.keys())
                            dataType = 1

                    elif(is_number(dataEntry['payload']['text'])):
                        
                        print 'Data is a single number'
                        colName += ['value']
                        dataType = 2
                    
                    else:

                        print 'Data is other (eg. string, odd format JSON)'
                        print dataEntry['payload']['text']
                        colName += ['payload_text']
                        dataType = 3

                
                ## Extracting the data as JSON, single number or string
                extractedList = []
                extractedData = True
                
                # As JSON
                if (dataType == 1):

                    try:
                        textJSON = json.loads(dataEntry['payload']['text'])

                        # Checking the json return the expected number of entries
                        if (entryNum == len(textJSON.values())):
                            
                            extractedList.append(dataEntry['date'])
                            extractedList += textJSON.values()
                        
                        else:
                            print ('!! Warning !! device %s - unexpected number of JSON entries ' % dataEntry['device'])
                            print dataEntry['payload']['text']
                            extractedData = False

                    except (ValueError, KeyError) as e:

                        print ('!! Warning !! device %s - JSON error' % dataEntry['device'])
                        print e
                        print dataEntry['payload']['text']
                        extractedData = False
                
                # As single number
                elif (dataType == 2):
                    
                    try:
                        extractedList.append(dataEntry['date'])
                        extractedList.append(float(dataEntry['payload']['text']))
                    except ValueError:
                        print ('!! Warning !! device %s - Error converting to number' % dataEntry['device'])
                        print dataEntry['payload']['text']
                        extractedData = False
                
                # As string
                else:
                
                    extractedList.append(dataEntry['date'])
                    extractedList.append(dataEntry['payload']['text'])

                
                if (extractedData):
                    dfList.append(extractedList)

            # Uses API's link to next section of data
            if ('next' in data):
                nextUrl = data['next']
                data = self.OS.getMsgsByNextUrl(nextUrl)
            else:
                data = None

        if (len(dfList) == 0):
            print ('Topic dataset has no entries')
            df = pd.DataFrame()
        
        else:
            df = pd.DataFrame(dfList, columns=colName)
            df.sort_values('datetime') # ??? FutureWarning: sort(columns=....) is deprecated, use sort_values(by=.....)
    
        return df



    ## Function to save panda df to csv
    def csvMake(self, currentTopic, startTime=None, endTime=None, saveDir = './'):

        # Changes the topic name into a save name
        topicSaveName = currentTopic.replace('/','_')
        topicSaveName = topicSaveName[1:]
        fileName = saveDir + topicSaveName + '.csv'

        df = self.dfMake(currentTopic, startTime, endTime)
        df.to_csv(fileName, sep=',', index=False)

        print ('%s dataset has %d entries - Saved to %s.csv' % (currentTopic, len(df), topicSaveName))



    ## Function to read the csv and update them with the latest data
    def csvUpdate(self, currentTopic, fileName):
        
        colNames = []
        startTime = ''
        
        with open(fileName, 'r') as f:
            firstLine = f.readline()    # Read the first line.
            f.seek(-2, 2)               # Jump to the second last byte.
            while f.read(1) != '\n':    # Until EOL is found...
                f.seek(-2, 1)           # ...jump back the read byte plus one more.
            lastLine = f.readline()     # Read last line.
        
            colNames = firstLine.rstrip().split(',')
            startTime = lastLine.split(',')[0]
            
        
        dtObject = datetime.strptime(startTime, '%Y-%m-%dT%H:%M:%S.%fZ')
        startTime = (dtObject + timedelta(microseconds=1000)).isoformat()[:-3] + 'Z'
        
        endTime = datetime.utcnow().isoformat()[:-3] + 'Z'
        
        df = self.dfMake(currentTopic, startTime, endTime, colNames)
        
        if (len(df) > 0):
            
            df.to_csv(fileName, mode = 'a', header=False, index=False)
            print ('%s has %d additional entries' % (fileName, len(df)))

