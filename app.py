import requests
from bs4 import BeautifulSoup
from flask_pymongo import PyMongo
from flask import Flask, jsonify
from threading import Thread
import telegram_send
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

DATABASE_URI = os.environ.get("DATABASE_URI")
app = Flask(__name__)
app.config["DEBUG"] = True
app.config["MONGO_URI"] = DATABASE_URI
mongo = PyMongo(app)


def sendToChannel(newNotice):
    """
  Sends the new notice to the channel using telegram bot
  """
    newNoticeStr = f'Title:{newNotice["title"]}\nLink:{newNotice["link"]}'
    telegram_send.send(messages=[newNoticeStr], conf="telegram-send.conf")
    return 200


responseList = []


def saveToDB(scrapedData):
   '''
  Receives the scrapedData list, checks if the dict item in the list exists in the db
  If exists then skips
  else inserts the item in the db and makes a call to sendToChannel function
  '''
  for dictItem in scrapedData:
      if mongo.db.amityplacements.find_one({"id_": dictItem["id_"]}) is not None:
          continue
      else:
          mongo.db.amityplacements.insert_one(dictItem)
          responseList.append(sendToChannel(newNotice=dictItem))
  return responseList


def fetchNewData():
    """
  Scrapes the placement website and returns the scraped data.
  Returns a list of dicts, with each dict containing title, id, and link of the new notice.
  """
    response = requests.get("https://www.amity.edu/placement/upcoming-recruitment.asp")
    soup = BeautifulSoup(response.content, "html.parser")
    notice_class = soup.find("ul", attrs={"class": "notices"})
    allNotices = notice_class.find_all("li")
    scrapedData = []
    title = ""
    link = ""
    _id = ""
    for liItem in allNotices:
        link = f"https://amity.edu/placement/{liItem.find('a')['href']}"
        _id = link.split("=")[1]
        title = liItem.strong.text.strip()
        scrapedData.append({"id_": _id, "title": title, "link": link})
    return scrapedData


@app.route("/")
def home():
    return "I'm alive"


@app.route("/send", methods=["GET"])
def send():
    scrapedData = fetchNewData()
    response = saveToDB(scrapedData)
    return jsonify({"response": response})


if __name__ == "__main__":
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
