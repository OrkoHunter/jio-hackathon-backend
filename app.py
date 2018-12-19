# -*- coding: utf-8 -*-
import os
import sys

import tables
import json
from flask import Flask, render_template, redirect, request

import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

"""
Fetch static data
"""
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))


engine = create_engine('mysql://fykfncuva5c32yws:y4581v48wq0jchft@ou6zjjcqbi307lip.cbetxkdyhwsb.us-east-1.rds.amazonaws.com:3306/qunovkvl5ol8c6pu', echo=True)
Session = sessionmaker(bind=engine)
# Session.configure(bind=engine)
session = Session()

SELL_LIST = ["Product Name", "Available Quantity", "Rate(R.s.) per KG", "minimum quantity"]
SELL_IDS = ["pname", "availQuant", "rate", "minQuant"]
SELL_INDEX = 0
SELL_FLAG = False


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
        body = request.json
        if body["object"] == "page" : 
            for entry in body["entry"] :
                event = entry["messaging"][0]
                print(event)

                #Getting the sender PSID
                psid = event["sender"]["id"]
                print("Sender ID " + psid)

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
    resp = {}
    if "text" in msg.keys() : 

        if SELL_FLAG : 
            if SELL_INDEX > 3 : 
                SELL_INDEX = 0
                UpdateFromDict("sell", SELL_VAL_DICT, psid)
                SELL_VAL_DICT = {}
                SELL_FLAG =False
                callSendAPI(psid, "Thank you for the information. Your listing has been posted. ")
            else : 
                SELL_VAL_DICT[SELL_IDS[SELL_INDEX]] = msg["text"]
                SELL_INDEX +=1
                callSendAPI(psid, {"text" : SELL_LIST[SELL_INDEX]})    
            

        elif "registration" in msg["text"] : 
            resp = getRegistrationDict()
            callSendAPI(psid, resp)
        # elif "buy" in msg["text"] : 
        #     print("found buy")
        #     resp = getBuyButtonRespFromList(12)
        #     print(resp)
        #     callSendAPI(psid, resp)

        elif "sell" in msg["text"] : 
            print("in sell")
            SELL_FLAG = True
            resp["text"] = "Please tell the {}".format(SELL_LIST[0])
            callSendAPI(psid, resp)
        else :
            resp["text"] = "You sent " + msg["text"]
            callSendAPI(psid, resp)

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
