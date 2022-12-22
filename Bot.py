from flask import Flask
from flask import request
from flask import Response
import requests
from bs4 import BeautifulSoup
import re
import schedule
import time
from datetime import date
import glob
from jproperties import Properties

# set webhook
configs = Properties()
with open('app-config.properties', 'rb') as config_file:
    configs.load(config_file)
TOKEN = configs.get("TOKEN").data
URL_STATUS_PENTAHO = configs.get("URL_STATUS_PENTAHO").data
URL_CHECK_LOGIN = configs.get("URL_CHECK_LOGIN").data

app = Flask(__name__)

#function
def saveLog(data):
    today  = date.today()
    print(today)
    nameFile = "./log_schedule/" +str(today) + ".txt"
    searchFile = "./log_schedule\\" +str(today) + ".txt"
    listFile = glob.glob("./log_schedule/*.txt")
    print(searchFile)
    print(listFile)
    if not (searchFile in listFile):
        f = open(nameFile, "x")
        f.write(data)
        f.close()
        return data
    else:
        f = open(nameFile, "r")
        fileData = f.read()
        #check trung
        f.close()
        if(fileData.find(data) >= 0):
            return '';
        else:
            f = open(nameFile, "w")
            writeData = fileData + "\n" + data;
            f.write(writeData)
            f.close()
            return data;
def updatJSessionId():
    f = open("./log_schedule/JSESSIONID.txt", "w")
    f.write(getJSESSIONID())
    f.close()

def getData():
    # importing the requests library
    f = open("./log_schedule/JSESSIONID.txt", "r")
    JSessionId = f.read()
    f.close()

    # api-endpoint
    URL = URL_STATUS_PENTAHO

    # defining a params dict for the parameters to be sent to the API
    headers = {'Cookie': 'JSESSIONID='+ JSessionId +';'}

    PARAMS = {}

    # sending get request and saving the response as response object
    r = requests.get(url = URL, params = PARAMS , headers=headers)

    if(r.status_code == 200):
        soup = BeautifulSoup(r.text)
        #check login
        print(soup.find("head").find("title"))
        if not (soup.find("head").find("title").text ==  'Kettle slave server status'):
            updatJSessionId()
            f = open("./log_schedule/JSESSIONID.txt", "r")
            JSessionId = f.read()
            f.close()
            headers = {'Cookie': 'JSESSIONID=' + JSessionId + ';'}
            r = requests.get(url=URL, params=PARAMS, headers=headers)
            print(soup.find("head").find("title"))


        # text = soup.find("finished")
        #cellTableCell cellTableFirstColumn cellTableEvenRowCell


        content = soup.find_all("td", class_=re.compile("cellTableEvenRowCell"))
        dataJob = soup.find_all("td", class_="cellTableCell cellTableEvenRowCell")

        result = ''
        try:
            if len(dataJob) > 0:
                # process array 4
                listContent = [];
                content = content[:len(content)-8]
                for i in range(int(len(content)/5)):
                    a = i*5;
                    listContent.append(content[a:a+4])
                for elm in listContent:
                    textLine = ' | '.join(str(e.string) for e in elm) + '\n'
                    result += saveLog(textLine)



                # n = 0
                # for i in content[:len(content)-8]:
                #     result += i.string + '|'
                #     if(n%4 == 0 and n > 0) : result += '\n'
                #     n+=1;
        except ValueError:
            print(ValueError)
            result = ''

        print(result);

        return result.replace('(with errors)', '🚫🚫(with errors)').replace('| Finished |','| 🟢🟢 Finished |');

    else:
        print(r.status_code)
        return 'error'


def getJSESSIONID():

    session = requests.session();
    res = session.get(URL_STATUS_PENTAHO)

    #
    payload = 'j_username=admin&j_password=password'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': 'JSESSIONID=' + session.cookies.get("JSESSIONID") +'; session-flushed=true; server-time=' + session.cookies.get("server-time") +'; session-expiry=' + session.cookies.get("session-expiry")
    }

    print(headers)
    #
    response = session.request("POST", URL_CHECK_LOGIN,  data=payload, headers=headers)
    return session.cookies.get("JSESSIONID");


def parse_message(message):
    print("message-->",message)
    chat_id = message['message']['chat']['id']
    txt = message['message']['text']
    print("chat_id-->", chat_id)
    print("txt-->", txt)
    return chat_id,txt
 
def tel_send_message(chat_id, text):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage'
    payload = {
                'chat_id': chat_id,
                'text': text
                }
   
    r = requests.post(url,json=payload)
    return r
 
# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         msg = request.get_json()
#
#         chat_id,txt = parse_message(msg)
#         if txt == "ioc":
#             text = getData()
#             tel_send_message(chat_id,text)
#         else:
#             tel_send_message(chat_id,'from webhook')
#
#         return Response('ok', status=200)
#     else:
#         return "<h1>Welcome!</h1>"
def sentReport():
    tel_send_message(669294645,getData())

def index():
    schedule.every(1).minutes.do(sentReport)
    while True:
        schedule.run_pending()
        time.sleep(1)



if __name__ == '__main__':
   index()

# job schedule
# greet()
# getData()






