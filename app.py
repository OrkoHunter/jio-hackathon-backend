# -*- coding: utf-8 -*-
import os
import sys

import tables
import json
from flask import Flask, render_template, redirect, request

import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pickle

"""
Fetch static data
"""
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))


engine = create_engine('mysql://fykfncuva5c32yws:y4581v48wq0jchft@ou6zjjcqbi307lip.cbetxkdyhwsb.us-east-1.rds.amazonaws.com:3306/qunovkvl5ol8c6pu', echo=True)
Session = sessionmaker(bind=engine)
# Session.configure(bind=engine)
session = Session()
SELL_LIST = ["Product Name", "Available Quantity", "Rate(R.s.) per KG", "minimum quantity"]
SELL_IDS = ["pname", "availQuant", "rate", "minQuant"],

def savePickle(index=0, flag = False ) : 
    d= {
    "SELL_INDEX" : 0,
    "SELL_FLAG" : False
    }
    # Store data (serialize)
    with open('asd.pickle', 'wb') as handle:
        pickle.dump(d, handle, protocol=pickle.HIGHEST_PROTOCOL)

savePickle()

def getPickleDict() : 
    with open('asd.pickle', 'rb') as handle:
        unserialized_data = pickle.load(handle)
        return unserialized_data

def updateSELLVALPick(d) : 
    x= None
    try : 
        with open('sellDict.pickle', 'rb') as handle:
            data = pickle.load(handle)
            for k,v in d.items() : 
                data[k] = v 
                x= data
    except : 
        x =d
    with open('sellDict.pickle', 'wb') as handle:
        pickle.dump(x, handle, protocol=pickle.HIGHEST_PROTOCOL)


SELL_VAL_DICT = {
    
}

app = Flask(__name__, static_url_path='/static')

app.config['SESSION_TYPE'] = 'filesystem'

# Valid routes
@app.route("/")
def main():
    return "Hello"

@app.route("/verify_facebook", methods=["POST", "GET"])
def verify_facebook():
    VERIFY_TOKEN = "1234553asdcds3"

    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        # Verify
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            return challenge
    if request.method == "POST" : 
        globDict = getPickleDict()
      
        body = request.json
        if body["object"] == "page" : 
            for entry in body["entry"] :
                event = entry["messaging"][0]
                print(event)

                #Getting the sender PSID
                psid = event["sender"]["id"]
                print("Sender ID " + psid)
                print("Sell Index is " + str(globDict["SELL_INDEX"]))
                print("Sell Flag is " + str(globDict["SELL_FLAG"]))
                if psid == "1013601592174583" : 
                    return "Entry Rec",200
                if "message" in event.keys() : 
                    handleMessage(psid,event["message"] )
                    #Handle messages

                elif "postback" in event.keys() : 
                    #Handle Postbacks 
                    pass
                return "Entry Rec",200
    else : 
        return "error",404


def handleMessage(psid, msg) : 
    global SELL_FLAG, SELL_INDEX, SELL_LIST, SELL_IDS, SELL_VAL_DICT
    globDict = getPickleDict()
    SELL_FLAG = globDict["SELL_INDEX"]
    resp = {}
    if "text" in msg.keys() : 
        
        if globDict["SELL_FLAG"] : 
            SELL_VAL_DICT[SELL_IDS[globDict["SELL_INDEX"]]] = msg["text"]
            globDict["SELL_INDEX"] +=1

            if globDict["SELL_INDEX"] > 3 : 
                globDict["SELL_INDEX"] = 0
                UpdateFromDict("sell", SELL_VAL_DICT, psid)
                SELL_VAL_DICT = {}
                globDict["SELL_FLAG"] =False
                callSendAPI(psid,{"text" : "Thank you for the information. Your listing has been posted. "})
            else : 
                callSendAPI(psid, {"text" : SELL_LIST[globDict["SELL_INDEX"]]})    

        elif "registration" in msg["text"] : 
            globDict["SELL_INDEX"] = 0
            resp = getRegistrationDict()
            callSendAPI(psid, resp)

        # elif "buy" in msg["text"] : 
        #     print("found buy")
        #     resp = getBuyButtonRespFromList(12)
        #     print(resp)
        #     callSendAPI(psid, resp)

        elif "sell" in msg["text"] : 
            print("in sell")
            globDict["SELL_FLAG"] = True
            globDict["SELL_INDEX"] = 0
            resp["text"] = "Please tell the {}".format(SELL_LIST[0])
            callSendAPI(psid, resp)
        else :
            globDict["SELL_INDEX"] = 0
            resp["text"] = "You sent " + msg["text"]
            callSendAPI(psid, resp)
        savePickle(globDict["SELL_INDEX"], globDict["SELL_FLAG"])
    elif msg.get("attachments") : 
        attachmentUrl = msg["attachments"][0]["payload"]["url"]
        print("attachmentUrl")
        resp["text"] = attachmentUrl
    # callSendAPI(psid,resp)



def getRegistrationDict() :
    resp = {"attachment":{
      "type":"template",
      "payload":{
        "template_type":"button",
        "text":"What do you want to do next?",
        "buttons":[
          {
            "type":"postback",
            "payload":"user_name",
            "title":"Name"
          },
          {
            "type":"postback",
            "payload":"address",
            "title":"Address"
          },
          {
            "type":"postback",
            "payload":"phone",
            "title":"Phone number"
          }
        ]
      }
    }}

    return resp

def handlePostback(psid, postBack) :
    pass

def callSendAPI(psid, resp) : 
    print(resp)
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": psid
        },
        "message": resp
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
                      params=params, headers=headers, data=data)
    print(r)
    print(r.text)

def UpdateFromDict(table, values, user_id):
    if table=="user":
        seller = session.query(User).get(user_id)
        unit = tables.Stock(**values)
        seller.user_stock.append(unit)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    
