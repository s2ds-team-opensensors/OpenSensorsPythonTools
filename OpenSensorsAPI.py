#!/usr/bin/env python2.7

## @package OpenSensorsPythonTools
# Tools for accessing https://opensensors.io historic API
#
# More details about using the API can be found here https://api.opensensors.io/index.html#/

# Libraries
import requests
import sys

BASE_URL = 'https://api.opensensors.io'

## OpenSensors API class
class OpenSensorsAPI():

    ## constructor.
    def __init__(self, API_KEY, user=None):
        self.user= user
        self.apiKey = API_KEY
        self.headers ={'Authorization':'api-key ' + self.apiKey }



    ## Connect to the API
    def connect(self,url):

        try:
            response = requests.get(url,headers=self.headers)
            if response.status_code == requests.codes.ok:
                return response
            else:
                response.raise_for_status()
        except requests.exceptions.ConnectionError as exc:
            print('A Connection error occurred.', exc)

   
   
    ## Get User's name
    def whoAmI(self):
        
        url= BASE_URL + '/v1/whoami'
        return self.connect(url).text

   
   
    ## List all the devices
    def listDevices(self):

        url= BASE_URL + ('/v1/users/%s/devices/' % self.whoAmI())
        return self.connect(url).json()

   
   
    ## List all the topics - Arguments: org name
    def listOrgTopics(self,org):
        
        url= BASE_URL + ('/v1/orgs/%s/topics' % org)
        return self.connect(url).json()

   
   
    ## Get messages for topic - Arguments: topic, start-date, end-date
    def getMsgsByTopic(self, topic, startdate=None, enddate=None):

        url = BASE_URL + ('/v1/messages/topic/%s' % topic)
        
        if(startdate):
            url = url + ('?start-date=%s' % startdate)
        if(startdate and enddate):
            url = url + ('&end-date=%s' % enddate)
            
        try:
            response = requests.get(url, headers=self.headers)
            if(response.status_code == 200):
                return response.json()
            else:
                sys.exit('Error - Request to %s failed' % url)
        
        except requests.exceptions.ConnectionError as exc:
            print('A Connection error occurred.', exc)

  
  
    ## Get next set of messages for topic - Arguments: next url
    def getMsgsByNextUrl(self,nextUrl):

        url = BASE_URL + nextUrl
        try:
            response = requests.get(url, headers=self.headers)
            if(response.status_code == 200):
                return response.json()
            else:
                sys.exit('Error - Request to %s failed' % url)
        
        except requests.exceptions.ConnectionError as exc:
            print('A Connection error occurred.', exc)
            
  
  
    ## Get realtime messages for topic - Arguments: next url !!! Currently not working !!!
    def getRealtimeMsgsByTopic(self, topic):
        
        url = 'https://realtime.opensensors.io/v1/events/topics/' + topic
        
        try:
            response = requests.get(url, headers=self.headers)
            if(response.status_code == 200):
                return response.json()
            else:
                sys.exit('Error - Request to %s failed' % url)
        
        except requests.exceptions.ConnectionError as exc:
            print('A Connection error occurred.', exc)       
        
