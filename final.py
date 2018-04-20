from __future__ import print_function
import time 
import requests
import cv2
import operator
import numpy as np
import os
import datetime

_url = 'https://westus.api.cognitive.microsoft.com/face/v1.0/detect'
_vurl = 'https://westus.api.cognitive.microsoft.com/face/v1.0/verify'
_key = '' #Here you have to paste your primary key
_maxNumRetries = 10

def notify(title, subtitle, message): #Function to notify on MAC
    t = '-title {!r}'.format(title)
    s = '-subtitle {!r}'.format(subtitle)
    m = '-message {!r}'.format(message)
    os.system('terminal-notifier {}'.format(' '.join([m, t, s])))


def processRequest( json, data, headers, params ):

    """
    Helper function to process the request to Project Oxford

    Parameters:
    json: Used when processing images from its URL. See API Documentation
    data: Used when processing image read from disk. See API Documentation
    headers: Used to pass the key information and the data type request
    """

    retries = 0
    result = None

    while True:

        response = requests.request( 'post', _url, json = json, data = data, headers = headers, params = params )
        # print(response.content)
        if response.status_code == 429: 

            print( "Message: %s" % ( response.json()['error']['message'] ) )

            if retries <= _maxNumRetries: 
                time.sleep(1) 
                retries += 1
                continue
            else: 
                print( 'Error: failed after retrying!' )
                break

        elif response.status_code == 200 or response.status_code == 201:

            if 'content-length' in response.headers and int(response.headers['content-length']) == 0: 
                result = None 
            elif 'content-type' in response.headers and isinstance(response.headers['content-type'], str): 
                if 'application/json' in response.headers['content-type'].lower(): 
                    result = response.json() if response.content else None 
                elif 'image' in response.headers['content-type'].lower(): 
                    result = response.content
        else:
            print( "Error code: %d" % ( response.status_code ) )
            print( "Message: %s" % ( response.json()['error']['message'] ) )

        break

    return result

# pathToFileInDisk = r'/Users/shubhankarmohapatra/faceapi/test.jpg'
# with open( pathToFileInDisk, 'rb' ) as f:
#     data = f.read()

params = { 'returnFaceAttributes': 'age,gender', 'returnFaceLandmarks': 'true'} 
    	
headers= dict()
headers['Ocp-Apim-Subscription-Key'] = _key
headers['Content-Type'] = 'application/octet-stream'

json = None

cap = cv2.VideoCapture(0) #Turning on the camera

while(True):
    # Capture frame-by-frame 
    ret, frame = cap.read() #Reading from camera

    # Our operations on the frame come here
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Display the resulting frame
    # cv2.imshow('frame',gray)
    # if cv2.waitKey(2) & 0xFF == ord('p'):
    time.sleep(5)
    cv2.imwrite('c1.png',frame) #saving image to be checked.
    pathToFileInDisk = r'/Users/shubhankarmohapatra/faceapi/c1.png'
    with open( pathToFileInDisk, 'rb' ) as f:
		data = f.read()   	
	

    result = processRequest( json, data, headers, params )
	# print(result)

    headers1 = dict()
    headers1['Ocp-Apim-Subscription-Key'] = _key
    headers1['Content-Type'] = 'application/json'
    flag=False #Check for user
    no_one=True #Variable to check someone is present or not
    for id in result:
        no_one=False
        print(id['faceId'])
        data = {"faceId1": "e87bf915-3ea3-4706-9ae7-12d584e4f88b" , "faceId2": id['faceId']}
        # print(data)
        response = requests.request( 'post', _vurl, json = data, headers = headers1 )
        print(response.content)
        # for res in response.content:
        # response.content=response.content.json()
        if response.content[15:19]=='true': #Finding identicallity from response
            flag=True

    if no_one==True:
        notify(title    = 'Security Check',subtitle = 'Finding user',message  = 'No one is currently using laptop. Shubhankar come back.') 
    elif flag==True:
        notify(title    = 'Hey Shubhankar :)',subtitle = 'Welcome',message  = 'It\'s nice to see you again.')    
    else:
        notify(title    = 'Intruder Warning !',subtitle = 'Stop using laptop',message  = 'I will inform Shubhankar about this.') 
        now=datetime.datetime.now()
        filename="Intruder "+str(now)+".jpg"
        cv2.imwrite(filename,frame)



    if cv2.waitKey(1) & 0xFF == ord('q'): #To break from loop if using imshow()
        break


# When everything done, release the capture
cap.release() #Release camera
cv2.destroyAllWindows()





