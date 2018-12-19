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
import github_api as gist
"""
Fetch static data
"""
ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

# engine = create_engine('sqlite:///:memory:', echo=True)
# # engine = create_engine('mysql://fykfncuva5c32yws:y4581v48wq0jchft@ou6zjjcqbi307lip.cbetxkdyhwsb.us-east-1.rds.amazonaws.com:3306/qunovkvl5ol8c6pu', echo=True)
# Session = sessionmaker(bind=engine)
# # Session.configure(bind=engine)
# session = Session()
SELL_LIST = ["Product Name", "picture","available quantity (in KG)", "rate(R.S.) per KG", "minimum order quantity you wish to receive (in KG)"]
SELL_IDS = ["prodName", "picture", "available_item", "price_per_unit", "minimum_item"]


DISEASE_IMAGE = {
    "apple black rot":"http://farm3.static.flickr.com/2659/5707297440_3922255890.jpg",
    "healthy apple":"https://cdn0.iconfinder.com/data/icons/simple-icons-ii/69/04-512.png",
    "cedar apple rust":"https://www.fs.fed.us/wildflowers/plant-of-the-week/images/cedarapplerust/Gymnosparangium_juniperi-virginianae_23A_lg.jpg",
    "apple scab":"http://www.missouribotanicalgarden.org/Portals/0/Gardening/Gardening%20Help/images/Pests/Apple_Scab1411.jpg"
}
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
                print(get_user(psid))
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
                # UpdateFromDict("sell", getSellValDict(), psid)
                print(getSellValDict())
                globDict["SELL_FLAG"] =False
                dataS = gist.read_database()
                dataS["data"]["products"].append({})
                gist.write_database(dataS)
                callSendAPI(psid,{"text" : "Thank you for the information. Your listing has been posted. "})

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

        elif "news" in msg["text"].lower() : 

            callSendAPI(psid, getNews())

        elif "buy" in msg["text"].lower() : 
            resp = getBuyResp()
            callSendAPI(psid, getBuyResp())
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
                savePickle(globDict["SELL_INDEX"], globDict["SELL_FLAG"])
                callSendAPI(psid, {"text" : "Please tell the " + SELL_LIST[globDict["SELL_INDEX"]]}) 
            else : 
            #Found the image now send it to API to get result  
                attachmentUrl = msg["attachments"][0]["payload"]["url"]
                callSendAPI(psid,{"text" : "Got your image. Please wait till I process it."})
                sending_sender_action(psid, 'typing_on')
                #Send results 
                # endpoint = "http://disection.herokuapp.com/disease_check"
                # r = requests.post(endpoint, {"image_url": attachmentUrl})
                res = fetch_data_from_url(attachmentUrl)
                sending_sender_action(psid, 'typing_off')
                # # print(r.content)
                callSendAPI(psid,getDiseaaseResponse(res) )
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
def getBuyResp() : 
    d = gist.read_database()
    prd = d["data"]["products"]
     
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
    for i in prd :
        item_to_sell =  {
        "title":i["prodName"],
        "subtitle":"Price per unit - {}\nAvailable Quantity - {} kg\nMinimum Order - {} kg".format(i["price_per_unit"], i["available_item"], i["minimum_item"]),
        "image_url": i["picture"],
        "buttons":[
            {
                "type":"web_url",
                "url":"https://www.google.com/",
                "title":"Buy Now"
              }]      
        }
        resp["attachment"]["payload"]["elements"].append(item_to_sell)
    return resp




def fetch_data_from_url(sample_image_url)  : 
    endpoint = "http://disection.herokuapp.com/disease_check"
    r = requests.post(endpoint, {"image_url": sample_image_url})
    content = json.loads(r.content.decode("utf-8"))['data']
    # response = json.loads(str.encode("utf-8").strip())['data']
    return content

def getDiseaaseResponse(data) : 
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
    for d in data : 
        item_to_sell =  {
        "title":d["disease"],
        "subtitle":"Probability : {} %".format(d["score"]),
        "image_url":DISEASE_IMAGE[d["disease"]],
        "buttons":[
            {
                "type":"web_url",
                "url":"https://www.google.com/search?q=" + d["disease"],
                "title":"More info"
              }]      
        }
        resp["attachment"]["payload"]["elements"].append(item_to_sell)
    return resp

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
    oldDict = gist.read_database()
    oldDict["data"]["products"][-1][key] = val
    oldDict["data"]["products"][-1]["by"] = psid
    gist.write_database(oldDict)
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

def getNews():
    resp = {
        "attachment": {
        "type": "template",
        "payload": {
            "template_type": "list",
            "top_element_style": "large",
            "elements": [
            {
                "title": "Farm loan waivers: What does it mean for economy?",
                "image_url": "https://www.livemint.com/rf/Image-621x414/LiveMint/Period2/2017/04/10/Photos/Processed/farmloans-kjuD--621x414@LiveMint.jpg",          
                "buttons": [
                {
                    "title": "Read",
                    "type": "web_url",
                    "url": "https://economictimes.indiatimes.com/news/economy/agriculture//news/economy/agriculture/farm-loan-waivers-what-does-it-mean-for-economy/videoshow/67156150.cms",
                    "messenger_extensions": True,
                    "webview_height_ratio": "compact",            
                }
                ]
            },
            {
                "title": "Agri schemes not disjointed but linked at various stages: Agri Min",
                "image_url": "https://img.etimg.com/thumb/msid-67146006,width-300,imgsize-582300,resizemode-4/agriculture-afp.jpg",
                "buttons": [
                {
                    "title": "Read",
                    "type": "web_url",
                    "url": "https://economictimes.indiatimes.com/news/economy/agriculture/agri-schemes-not-disjointed-but-linked-at-various-stages-agri-min/articleshow/67145806.cms",
                    "messenger_extensions": True,
                    "webview_height_ratio": "compact",            
                }
                ]
            },
            {
                "title": "Madhya Pradesh to waive up to $5.3 billion in farm debts",
                "image_url": "https://img.etimg.com/thumb/msid-67138922,width-300,imgsize-186074,resizemode-4/kamal-nath-pti.jpg",
                "buttons": [
                {
                    "title": "Read",
                    "type": "web_url",
                    "url": "https://economictimes.indiatimes.com/news/economy/agriculture/madhya-pradesh-to-waive-up-to-5-3-billion-in-farm-debts/articleshow/67138942.cms",
                    "messenger_extensions": True,
                    "webview_height_ratio": "compact",            
                }
                ]
            }
            ,{
                "title": "With eye on 2019, BJP government in Maharashtra woos onion growers",
                "image_url": "https://img.etimg.com/thumb/msid-67113487,width-300,imgsize-383064,resizemode-4/onion-pti.jpg",
                "buttons": [
                {
                    "title": "Read",
                    "type": "web_url",
                    "url": "https://economictimes.indiatimes.com/news/economy/agriculture/with-eye-on-2019-bjp-government-in-maharashtra-woos-onion-growers/articleshow/67113488.cms",
                    "messenger_extensions": True,
                    "webview_height_ratio": "compact",            
                }
                ]
            }
            
            ],
            "buttons": [
            {
                "title": "View More",
                "type": "postback",
                "payload": "payload"            
            }
            ]  
        }
        }
    }
    
    return resp
def get_user(sender_id):
    '''
    The user_details dictionary will have following keys
    first_name : First name of user
    last_name : Last name of user
    profile_pic : Profile picture of user
    locale : Locale of the user on Facebook
    '''
    base_url = "https://graph.facebook.com/v2.6/{}?fields=first_name,last_name,profile_pic,locale,timezone,gender&access_token={}".format(
        sender_id, os.environ["PAGE_ACCESS_TOKEN"])
    user_details = requests.get(base_url).json()
    return user_details
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
    
