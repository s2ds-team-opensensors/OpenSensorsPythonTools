#!/usr/bin/env python2.7

## @package OpenSensorsPythonTools
# Tools for analysing OpenSensors data (csv files)

# Libraries
from datetime import datetime, timedelta
import pandas as pd
import os, sys

import numpy as np

## OpenSensors Analyse class
class OpenSensorsAnalyse():

    ## constructor
    def __init__(self, csvFile):
        self.fileName = csvFile
        
    
    
    ## Example of a file's start and end date&times to split a file into a list of times of day
    # 8H time windows are used in this example with start 7h: Morning (7-15h), Evening (15-23h), Night (23-7h)
    def csvDaySplit(self, dayStartTime=7, dayInterval=8):
        
        if (24%dayInterval == 0 and dayStartTime < dayInterval):
            
            daySlice = 24 / dayInterval
        
            ## Reads the first and last datatime entries without having to read the csv as data frame
            with open(self.fileName, 'r') as f:
                for i, l in enumerate(f):
                    if i == 1: # Number of lines to skip before first entry
                        firstEntry = l.split(',')[0]
                        break
                
                f.seek(-2, 2)               # Jump to the second last byte.
                while f.read(1) != '\n':    # Until EOL is found...
                    f.seek(-2, 1)           # ...jump back the read byte plus one more.
                lastLine = f.readline()     # Read last line.
                lastEntry = lastLine.split(',')[0]
            
            # Cretes beginning of time slices
            startDatetime = datetime.strptime(firstEntry, '%Y-%m-%dT%H:%M:%S.%fZ')
        
            if (startDatetime.hour < dayStartTime ):
                
                strStyle = '%%Y-%%m-%%d %d:00:00' % (dayStartTime + ((daySlice-1) * dayInterval))
                st = startDatetime - timedelta(days=1)
                startStr = st.strftime(strStyle)
            
            else:
                
                for checkTime in range(1,daySlice+1):
                
                    if (startDatetime.hour < (dayStartTime + (checkTime * dayInterval) ) ):
                    
                        strStyle = '%%Y-%%m-%%d %d:00:00' % (dayStartTime + ((checkTime-1) * dayInterval) )
                        startStr = startDatetime.strftime(strStyle)
                        break
                
            print startDatetime, ' --> Start of range:', startStr
            
            
            # Cretes end of time slices
            endDatetime = datetime.strptime(lastEntry, '%Y-%m-%dT%H:%M:%S.%fZ')
            
            if (endDatetime.hour >= (dayStartTime + ((daySlice-1) * dayInterval))):

                strStyle = '%%Y-%%m-%%d %d:00:00' % dayStartTime
                st = endDatetime + timedelta(days=1)
                endStr = st.strftime(strStyle)
            
            else:
                
                for checkTime in range(0,daySlice):
                
                    if (endDatetime.hour < (dayStartTime + (checkTime * dayInterval) ) ):
                    
                        strStyle = '%%Y-%%m-%%d %d:00:00' % (dayStartTime + (checkTime * dayInterval) )
                        endStr = endDatetime.strftime(strStyle)
                        break
                
            print endDatetime, ' --> End of range:  ', endStr
            
            
            freq = '%dH' % dayInterval
            rng = pd.date_range(startStr, endStr, freq=freq)
            
            return rng
        
        else:
            print 'Invaild input: 24/%d not an integer OR dayStartTime < dayInterval' % dayInterval
    
    
    ## Prints head of DataFrame, to see its layout
    def dfHead(self, headNum=15):
        
        df = pd.read_csv(self.fileName, sep=',', nrows=headNum)
        df['datetime'] = pd.to_datetime(df['datetime'])
        df = df.set_index('datetime') 
        
        print df
    
    
    
    ## Read in csv file and sets the datetime object to the index
    def dfSetup(self):
        
        df = pd.read_csv(self.fileName, sep=',')
        df['datetime'] = pd.to_datetime(df['datetime'])
        df = df.set_index('datetime')
    
        return df
    
    
    
    def columnCount(self, columnName, dfOther=None):
        
        if (dfOther is None):
            df = self.dfSetup()
        
        elif (len(dfOther) > 1):
            df = dfOther
        
        else:
            print '!! Warning !! DataFrame too small'
            df = dfOther
        
        columnTotal = df[columnName].value_counts()
        
        return columnTotal
    

   
    def selectSubset(self, selectCol = [], splitCol=None, sepCol=None, startTime=None, endTime=None, deltaTime=True):

        df = self.dfSetup()
        
        ## Selects a list of columns to use and splits a column into single type if it contains more than one
        # eg. if a file contains multiple sensor readings 
        if (len(selectCol) > 0):
            dfSub = df[selectCol]
            
        else:
            dfSub = df
        
        if (splitCol and sepCol):
            dfSub = dfSub[dfSub[splitCol] == sepCol]
        
        ## Converts datetime column to datatime object index, then use it to create time slices
        # Time format '2015-10-17 09:00:00' May use the dfOther to use other data frames
        if (startTime and endTime):
            dfSub = dfSub[ startTime : endTime ]
        
        else:
            dfSub = dfSub
        
        ## adds a column containing the time different between entry and the previous entry, needs a datatime index
        if (deltaTime):
            dfSub['tmp_datetime'] = dfSub.index
            dfSub['deltatime'] = dfSub['tmp_datetime'].diff().fillna(0)
            dfSub = dfSub.drop(['tmp_datetime'], axis=1) # Remove tmp_datetime column
        
        return dfSub
    
    
    
    ## Uses data df time-series functions with value initalised and return several rolling stats seriesin data frame
    # Input should have datetime index and 1 value column
    def rollingStats(self, selectCol = [], splitCol=None, sepCol=None, startTime=None, endTime=None, window=60, quantile=0.1, freq='10s', min_periods=5 ):
        
        df = self.dfSetup()
        
        ## Selects a list of columns to use and splits a column into single type if it contains more than one
        # eg. if a file contains multiple sensor readings 
        if (len(selectCol) > 0):
            dfSub = df[selectCol]
            
        else:
            dfSub = df
        
        if (splitCol and sepCol):
            dfSub = dfSub[dfSub[splitCol] == sepCol]
        
        ## Converts datetime column to datatime object index, then use it to create time slices
        # Time format '2015-10-17 09:00:00' May use the dfOther to use other data frames
        if (startTime and endTime):
            dfSub = dfSub[ startTime : endTime ]
        
        else:
            dfSub = dfSub
        
        if (splitCol):
            dfSub = dfSub.drop(splitCol, axis=1) # Remove columns used to split entries
        
        
        valueName = dfSub.columns.values[0]
        outList = []
        
        counts = pd.rolling_count(dfSub,window,freq=freq).rename(columns = {valueName:'rolling_counts'})
        outList.append(counts)
        
        means = pd.rolling_mean(dfSub, window, min_periods=min_periods, freq=freq).rename(columns = {valueName:'rolling_mean'})
        outList.append(means)
        
        rms = np.sqrt(pd.rolling_mean(dfSub**2, window, min_periods=min_periods, freq=freq).rename(columns = {valueName:'rolling_rms'}) )
        outList.append(rms)
        
        medians = pd.rolling_median(dfSub, window, min_periods=min_periods, freq=freq).rename(columns = {valueName:'rolling_median'})
        outList.append(medians)
        
        stds = pd.rolling_std(dfSub, window, min_periods=min_periods, freq=freq).rename(columns = {valueName:'rolling_std'})
        outList.append(stds)
        
        mins = pd.rolling_min(dfSub, window, min_periods=min_periods, freq=freq).rename(columns = {valueName:'rolling_min'})
        outList.append(mins)
        
        maxs = pd.rolling_max(dfSub, window, min_periods=min_periods, freq=freq).rename(columns = {valueName:'rolling_max'})
        outList.append(maxs)
        
        quants = pd.rolling_quantile(dfSub, window, quantile, min_periods=min_periods, freq=freq).rename(columns = {valueName:'rolling_quantile'})
        outList.append(quants)

        
        dfOut = pd.concat(outList, axis=1)

        return dfOut
