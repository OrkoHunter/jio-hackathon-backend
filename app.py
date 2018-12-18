# -*- coding: utf-8 -*-
import os
import sys

import tables

from flask import Flask, render_template, redirect, request

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
            print(1)
            for entry in body["entry"] :
                event = entry["messaging"][0]
                print(event)

                #Getting the sender PSID
                psid = event["sender"]["id"]
                print("Sender ID " + psid)

                if event["message"] : 
                    handleMessage(psid,event["message"] )
                    #Handle messages

                elif event["postback"] : 
                    #Handle Postbacks 
                    pass
                return "Entry Rec",200
    else : 
        return "error",404

@app.route("/webhook", methods= ["POST", "GET"])
def webhook() : 
    if request.method == "POST" : 
        body = request.json
        if body["object"] == "page" : 
            print(1)
            for entry in body["entry"] :
                event = entry["messaging"][0]
                print(event)

                #Getting the sender PSID
                psid = event["sender"]["id"]
                print("Sender ID " + psid)

                if event["message"] : 
                    handleMessage(psid,event["message"] )
                    #Handle messages

                elif event["postback"] : 
                    #Handle Postbacks 
                    pass
                return "Entry Rec",200
        else : 
            return "error",404


def handleMessage(psid, msg) : 
    resp = {}
    if msg["text"] : 
        resp["text"] = "You sent " + msg["text"]

    callSendAPI(psid,resp)
def handlePostback(psid, postBack) :
    pass

def callSendAPI(psdi, resp) : 

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
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
