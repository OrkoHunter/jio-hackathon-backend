# -*- coding: utf-8 -*-
import os
import sys
import unnati
import tables
import json
from flask import Flask, render_template, redirect, request
import time
import requests
from flask_sqlalchemy import SQLAlchemy
import pickle

"""
Fetch static data
"""
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

# engine = create_engine('sqlite:///:memory:', echo=True)
# # engine = create_engine('mysql://fykfncuva5c32yws:y4581v48wq0jchft@ou6zjjcqbi307lip.cbetxkdyhwsb.us-east-1.rds.amazonaws.com:3306/qunovkvl5ol8c6pu', echo=True)
# Session = sessionmaker(bind=engine)
# # Session.configure(bind=engine)
# session = Session()
SELL_LIST = ["Product Name", "picture","available quantity (in KG)", "Rate(R.S.) per KG", "minimum order quantity you wish to receive"]
SELL_IDS = ["prod_id", "picture", "available_item", "price_per_unit", "minimum_item"]

def savePickle(index, flag ) :
  
    d= {
    "SELL_INDEX" : index,
    "SELL_FLAG" : flag
    }

    # Store data (serialize)
    with open('asd.pickle', 'wb') as handle:
        pickle.dump(d, handle)

    with open('sellDict.pickle', 'wb') as handle:
        pickle.dump({}, handle)
savePickle(0, False)

def getPickleDict() : 
    with open('asd.pickle', 'rb') as handle:
        unserialized_data = pickle.load(handle)
    return unserialized_data

def updateSELLVALPick(d) : 
    print("Dict to add")
    print(d)
    with open('sellDict.pickle', 'rb') as handle:
        data = pickle.load(handle)
        print("init dict")
        print(data)
        for k,v in d.items() : 
            data[k] = v 
    print("Final Dict")
    print(data)
    with open('sellDict.pickle', 'wb') as handle:
        pickle.dump(data, handle)
def getSellValDict():
    with open('sellDict.pickle', 'rb') as handle:
        unserialized_data = pickle.load(handle)
    return unserialized_data    

app = Flask(__name__, static_url_path='/static')
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
# db = SQLAlchemy(app)
# app.config['SESSION_TYPE'] = 'filesystem'


# class User(db.Model):
#     __tablename__ = 'user'
#     user_id = db.Column(db.Integer, primary_key=True)
#     user_name = db.Column(db.String)
#     address = db.Column(db.String)
#     phone = db.Column(db.String)
#     user_stock = db.relationship("Stock")
    
#     def __repr__(self):
#         return "<User(name={}, user_id={},address={},phone={},stock={})>".format(self.user_name,self.user_id,self.address,self.phone,self.user_stock)

# class Buyer(db.Model):
#     __tablename__ = 'buyer'
#     user_id = db.Column(db.Integer, primary_key=True)
#     user_name = db.Column(db.String)
#     address = db.Column(db.String)
#     phone = db.Column(db.String)
    
#     def __repr__(self):
#         return "<Buyer(name={}, user_id={},address={},phone={})>".format(self.user_name,self.user_id,self.address,self.phone)

# class Stock(db.Model):
#     __tablename__ = 'stock'
#     prod_id = db.Column(db.String, primary_key=True)
#     unit_type = db.Column(db.String)
#     available_item = db.Column(db.Integer)
#     price_per_unit = db.Column(db.Float)
#     minimum_item = db.Column(db.Integer)
#     picture = db.Column(db.String)
#     owner_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))

#     def __repr__(self):
#         return "<User(id={}, unit_type={},available_item={},price_per_unit={},min_item={})>".format(self.prod_id,self.unit_type,self.available_item,self.price_per_unit,self.minimum_item)


# db.create_all()
# user1 = User(user_id=1,user_name="Ramu",address="Medinipur, West Bengal",phone="7897897897")
# item1 = Stock(prod_id="1aa", unit_type="kg", available_item="200",price_per_unit="20",minimum_item="50",picture="https://cdn1.woolworths.media/content/wowproductimages/medium/144329.jpg",owner_id=1) 
# db.session.add(user1)
# db.session.add(item1)
# db.session.commit()
# print(User.query.all())
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
                if entry.get("postback") : 
                    postb = entry["postback"]
                    payload = postb["payload"]
                    print(payload)
                    return "ok", 200
                try : 
                    event = entry["messaging"][0]
                except : 
                    return "", 404
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

                return "Entry Rec",200
    else : 
        return "error",404


def handleMessage(psid, msg) : 
    global  SELL_INDEX, SELL_LIST, SELL_IDS
    SELL_VAL_DICT = {}
    globDict = getPickleDict()
    resp = {}
    if "text" in msg.keys() : 
        
        if globDict["SELL_FLAG"] : 
            # updateSELLVALPick({SELL_IDS[globDict["SELL_INDEX"]] : msg["text"]})
            addSellData(psid,SELL_IDS[globDict["SELL_INDEX"]], msg["text"] )
            globDict["SELL_INDEX"] = (globDict["SELL_INDEX"] + 1)

            if globDict["SELL_INDEX"] > 4 : 
                globDict["SELL_INDEX"] = 0
                UpdateFromDict("sell", getSellValDict(), psid)
                print(getSellValDict())
                globDict["SELL_FLAG"] =False
                callSendAPI(psid,{"text" : "Thank you for the information. Your listing has been posted. "})
                print()
            else : 
                if SELL_IDS[globDict["SELL_INDEX"]] == "picture" : 
                    callSendAPI(psid, {"text" : "Please send a picture of the harvest."})
                else :
                    callSendAPI(psid, {"text" : "Please tell the " + SELL_LIST[globDict["SELL_INDEX"]]})    

        elif "registration" in msg["text"].lower() : 
            globDict["SELL_INDEX"] = 0
            resp = getRegistrationDict()
            callSendAPI(psid, resp)

        # elif "buy" in msg["text"] : 
        #     print("found buy")
        #     resp = getBuyButtonRespFromList(12)
        #     print(resp)
        #     callSendAPI(psid, resp)

        elif "sell" in msg["text"].lower() : 
            print("in sell")
            globDict["SELL_FLAG"] = True
            globDict["SELL_INDEX"] = 0
            resp["text"] = "Please tell the {}".format(SELL_LIST[0])
            savePickle(0, True)
            callSendAPI(psid, resp)

        elif "fertilizer" in msg["text"].lower() : 
            print("in fert")
            resp["text"] = "Please send your current location to know optimum fertilizer quantity"
            callSendAPI(psid, resp)
        else :
            globDict["SELL_INDEX"] = 0
            resp["text"] = "You sent " + msg["text"]
            callSendAPI(psid, resp)
        
        savePickle(globDict["SELL_INDEX"], globDict["SELL_FLAG"])
        
    elif msg.get("attachments") : 
        if msg["attachments"][0]["type"] == "image" :
            if globDict["SELL_FLAG"] : 
                addSellData(psid,SELL_IDS[globDict["SELL_INDEX"]], msg["attachments"][0]["payload"]["url"] )
                globDict["SELL_INDEX"] = (globDict["SELL_INDEX"] + 1)
                callSendAPI(psid, {"text" : SELL_LIST[globDict["SELL_INDEX"]]}) 
            else : 
            #Found the image now send it to API to get result  
                attachmentUrl = msg["attachments"][0]["payload"]["url"]
                callSendAPI(psid,{"text" : "Got your image. Please wait till I process it."})
                sending_sender_action(psid, 'typing_on')
                #Send results 
                sending_sender_action(psid, 'typing_off')
        elif msg["attachments"][0]["type"] == "audio" :
            attachmentUrl = msg["attachments"][0]["payload"]["url"]
            callSendAPI(psid,{"text" : "Got your audio. Please wait till I process it."})

        elif msg["attachments"][0]["type"] == "location" :
            callSendAPI(psid, {"text" : "Thank you for sharing your location. "})
            nit, phos = unnati.getData(msg["attachments"][0]["payload"]["coordinates"]["lat"], msg["attachments"][0]["payload"]["coordinates"]["long"])
            sending_sender_action(psid, 'typing_on')
            time.sleep(1000)

            print(nit)
            print(phos)
            callSendAPI(psid, {"text" : "Below are the recommended fertiliser dosages for nitrogen requirement."})
            callSendAPI(psid, getFertiliserResponse(nit, "http://i.imgur.com/BHlC0zj.jpg"))
            sending_sender_action(psid, 'typing_on')
            time.sleep(1000)
            callSendAPI(psid, {"text" : "Below are the recommended fertiliser dosages for phosphorus requirement."})
            callSendAPI(psid, getFertiliserResponse(phos,"http://i.imgur.com/Ao1vPNe.jpg"))
        # print("attachmentUrl")
        # resp["text"] = attachmentUrl
    # callSendAPI(psid,resp)

def getFertiliserResponse(data,img) : 
    resp = {
    "attachment":{
      "type":"template",
      "payload":{
        "template_type":"generic",
        "elements":[
            ]
        }
        }
    }

    for k,v in data.items():
        item_to_sell =  {
        "title":k,
        "subtitle":"{} KG/Ha".format(v),
        "image_url":img,
        "buttons":[
            {
                "type":"web_url",
                "url":"https://www.google.com/search?q=" + k,
                "title":"More info"
              }]      
        }
        resp["attachment"]["payload"]["elements"].append(item_to_sell)
    return resp

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

def sending_sender_action(recipient_id, sender_action):
    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps(
        {
            "recipient": {
                "id": recipient_id
            },
            "sender_action": sender_action
        })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
                      params=params, headers=headers, data=data)

def addSellData(psid,key,val) : 
    print(key)
    print(val)
    # seller = db.session.query(User).get(psid)
    # stck = seller.user_stock
    # setattr(stck, key, val)
    # db.session.commit()

def UpdateFromDict(table, values, user_id):
    if table=="user":
        seller = db.session.query(User).get(user_id)
        unit = tables.Stock(**values)
        seller.user_stock.append(unit)
        db.session.add(unit)
    db.session.commit()    

def ItemsList():
    resp = {
    "attachment":{
      "type":"template",
      "payload":{
        "template_type":"generic",
        "elements":[
            ]
        }
        }
    }

    for instance in db.session.query(User).order_by(user_id):
        for it in instance.user_stock:
            item_to_sell =  {
            "title":"",
            "subtitle":"",
            "image_url":"",
            "buttons":[
                {
                "type":"postback",
                "title":"Buy Now!",
                "payload":""
                }]      
            }
            item_to_sell["title"] = it.prod_id
            item_to_sell["subtitle"] = it.price_per_unit
            item_to_sell["image_url"] = it.picture
            item_to_sell["buttons"]["payload"] = "BUYNOW_"+it.prod_id
            resp["attachment"]["payload"]["elements"].append(item_to_sell)
    
    return resp
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    
