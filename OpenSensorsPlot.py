#!/usr/bin/env python2.7

## @package OpenSensorsPythonTools
# Tools for plotting OpenSensors data (csv files)

# Libraries
from datetime import datetime, timedelta
import pandas as pd

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from scipy.stats import gaussian_kde


## ===> Colour Hex List <===

#ColourValues=["000000","1CE6FF","006FA6","0000A6","008941","FF34FF",
              #"A30059","FFDBE5","7A4900","FF4A46","63FFAC","B79762",
              #"004D43","8FB0FF","997D87","5A0007","809693","FEFFE6",
              #"1B4400","4FC601","3B5DFF","4A3B53","FF2F80","61615A",
              #"BA0900","6B7900","00C2A0","FFAA92","FF90C9","B903AA",
              #"D16100","DDEFFF","000035","7B4F4B","A1C299","300018",
              #"0AA6D8","013349","00846F","372101","FFB500","C2FFED",
              #"A079BF","CC0744","C0B9B2","C2FF99","001E09","00489C",
              #"6F0062","0CBD66","EEC3FF","456D75","B77B68","7A87A1",
              #"788D66","885578","FAD09F","FF8A9A","D157A0","BEC459",
              #"456648","0086ED","886F4C","34362D","B4A8BD","00A6AA",
              #"452C2C","636375","A3C8C9","FF913F","938A81","575329",
              #"00FECF","B05B6F","8CD0FF","3B9700","04F757","C8A1A1",
              #"1E6E00","7900D7","A77500","6367A9","A05837","6B002C",
              #"772600","D790FF","9B9700","549E79","FFF69F","201625",
              #"72418F","BC23FF","99ADC0","3A2465","922329","5B4534",
              #"FDE8DC","404E55"]
#M = len(ColourValues)

#def hex_to_rgb(value):
    #value = value.lstrip('#')
    #lv = len(value)
    #return tuple(int(value[i:i+lv/3], 16) for i in range(0, lv, lv/3))



## OpenSensors Plot class
class OpenSensorsPlot():

    ## constructor.
    def __init__(self, dfInput):
        self.df = dfInput
                
    
    
    def timeseriesPlot(self, ax, selectCol, colour='b'):
        
        if ( len(self.df[selectCol]) > 0):
        
            ax.plot_date(self.df.index, self.df[selectCol], '.', color=colour,  label=selectCol)
            ax.set_xticklabels(ax.xaxis.get_majorticklabels(), rotation=30, ha='right')
            ax.xaxis.set_major_locator(mdates.HourLocator(np.arange(0,25,12)))
            ax.xaxis.set_minor_locator(mdates.HourLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b %R'))
        
        else:
            
            ax.text(0.5, 0.5,'No Data', ha='center', va='center', fontsize=30)
            ax.set_xticks([])
            ax.set_yticks([])
            
            
        
    ## creates violin plots on an subplot
    def violinPlot(self, ax, selectCol, colour='b'):
        
        #create violin plots on an axis
        if ( len(self.df[selectCol]) > 1):
            
            w = min(0.15*max(0.0,1.0),0.5)

            data = self.df[selectCol].values
            data = data[~np.isnan(data)]
            k = gaussian_kde(data) #calculates the kernel density
            m = k.dataset.min() # lower bound of violin
            M = k.dataset.max() # upper bound of violin
            x = np.arange(m,M,(M-m)/100.) # support for violin
            v = k.evaluate(x) # violin profile (density curve)
            v = v/v.max()*w # scaling the violin to the available space
            ax.fill_betweenx(x,0,v,facecolor=colour,alpha=0.5)
            ax.fill_betweenx(x,0,-v,facecolor=colour,alpha=0.5)
            
            ax.set_xticks([])
            ax.set_xlim([-0.2,0.2])
            
        else:

            ax.text(0.5, 0.5,'No Data', ha='center', va='center', fontsize=30)
            ax.set_xticks([])
            ax.set_yticks([])
    
    
    
    ## Plot a histogram of the counts within column, default = delta time column in seconds
    def countHist(self,ax, selectCol='deltatime', colour='b'):
    

        if ( len(self.df[selectCol]) > 0):
            
            if (selectCol == 'deltatime'):
                self.df[selectCol].groupby( self.df[selectCol].dt.seconds ).count().plot(kind="bar", color=colour, alpha=0.5)
                
                axY = ax.get_ylim()
                ax.set_ylim( [axY[0], axY[1]*1.1] )
                ax.set_xticklabels(ax.xaxis.get_majorticklabels())
                ax.set_xlabel('Delta time (seconds)', fontsize=12)
                
            else:
                self.df[selectCol].value_counts().plot(kind="bar", color=colour, alpha=0.5)
                
                axY = ax.get_ylim()
                ax.set_ylim( [axY[0], axY[1]*1.1] )
                ax.set_xticklabels(ax.xaxis.get_majorticklabels())
                
            rects = ax.patches

            for rect in rects:
                height = rect.get_height()
                label = '%d' % height
                ax.text(rect.get_x() + rect.get_width()/2, height + 5, label, ha='center', va='bottom')
            
        else:
            
            ax.text(0.5, 0.5,'No Data', ha='center', va='center', fontsize=30)
            ax.set_xticks([])
            ax.set_yticks([])
