#!/usr/bin/env python2.7

## @package OpenSensorsPythonTools
# Main file for running OpenSensors Python Tools 

# Libraries
import matplotlib.pyplot as plt

# Local Code
from OpenSensorsAPI import *
from OpenSensorsData import *
from OpenSensorsAnalyse import *
from OpenSensorsPlot import *


## User's API key
# 
# API keys can be generated on https://opensensors.io user's home page
API_KEY = ''

def main():
    
    ## ===> API Example <===
    
    ### Creates OpenSensorsAPI object using your API
    #OS_API = OpenSensorsAPI(API_KEY)
    
    ## ===> Data Example <===
    
    ### Creates OpenSensorsData object using your OpenSensorsAPI object
    #OS_DATA = OpenSensorsData(OS_API)
    #connected = OS_DATA.testAPIkey()
        
    #if (connected):
        
        #topics = OS_DATA.orgTopicList('breatheheathrow')#,displayList=True)#, saveFile=True)
        
        #topicNum = [58]#[11, 27, 43, 58, 74]
        
        #for i in topicNum:
            #OS_DATA.csvMake(topics[i]) 
        
        #df = OS_DATA.dfMake('/orgs/breatheheathrow/noise', '2015-11-02T00:00:00.000Z', '2015-11-02T12:00:00.000Z')

        #print 'Dataset start date & time: ' + df['datetime'].iloc[0]
        #print 'Dataset end date & time: ' + df['datetime'].iloc[-1]
        #OS_DATA.csvUpdate('/orgs/breatheheathrow/noise', 'orgs_breatheheathrow_noise.csv')
    
    
    ## ===> Analysis Example <===
    
    OS_ANALYSIS =  OpenSensorsAnalyse('./new_noise.csv')  
    listSplit = OS_ANALYSIS.csvDaySplit()
    #OS_ANALYSIS.dfHead(50)

    #print OS_ANALYSIS.columnCount('serial-number')
    
    dfSel =  OS_ANALYSIS.selectSubset( ['serial-number', 'converted-value'], 'serial-number', 20630012, listSplit[0],listSplit[10], True)
    
    dfRollStats =  OS_ANALYSIS.rollingStats(['serial-number', 'converted-value'], 'serial-number', 20630012, listSplit[0],listSplit[5])
    
    
    ## ===> Plotting Example <===
    
    OS_PLOT1 = OpenSensorsPlot(dfSel)
    OS_PLOT2 = OpenSensorsPlot(dfRollStats)
    
    fig = plt.figure(figsize=(32,18))
    
    ax1 = fig.add_subplot(2, 2, 1)
    OS_PLOT1.violinPlot(ax1, 'converted-value')
    
    ax2 = fig.add_subplot(2, 2, 2)
    OS_PLOT1.countHist(ax2)
    
    ax3 = fig.add_subplot(2, 2, 3)
    OS_PLOT2.timeseriesPlot(ax3, 'rolling_mean')
    
    ax4 = fig.add_subplot(2, 2, 4)
    OS_PLOT2.timeseriesPlot(ax4, 'rolling_rms')
    
    fig.savefig('./plot1.png')
    


if __name__ == '__main__':

    main()

    print '===> OpenSensorsRun.py finished <===='
