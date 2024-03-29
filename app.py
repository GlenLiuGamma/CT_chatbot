import os
import sys

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
from fsm import TocMachine
from utils import send_text_message
import requests
import urllib.request
from bs4 import BeautifulSoup
from upload_image import upload_image

#scrap
def find_graph(word):
    url = 'https://www.google.com/search?q='+word+'&rlz=1C2CAFB_enTW617TW617&source=lnms&tbm=isch&sa=X&ved=0ahUKEwictOnTmYDcAhXGV7wKHX-OApwQ_AUICigB&biw=1128&bih=960'
    photolimit = 3
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url,headers = headers) #使用header避免訪問受到限制
    soup = BeautifulSoup(response.content, 'html.parser')
    items = soup.find_all('img')
    folder_path ='./photo/'

    if (os.path.exists(folder_path) == False): #判斷資料夾是否存在
        os.makedirs(folder_path) #Create folder
    for index , item in enumerate (items):

        if (item and index < photolimit ):
            html = requests.get(item.get('src')) # use 'get' to get photo link path , requests = send request
            img_name = folder_path + str(index + 1) + '.png'
            with open(img_name,'wb') as file: #以byte的形式將圖片數據寫入
                file.write(html.content)
                file.flush()
            file.close() #close file
        
    link = upload_image(img_name)    
    print('Done')
    return link
#endscrap


load_dotenv()

machine = TocMachine(
    states=["user", "search", "state2", "sendback"],
    transitions=[
        {
            "trigger": "advance",
            "source": "user",
            "dest": "search",
            "conditions": "is_going_to_search",
        },
        {
            "trigger": "advance",
            "source": "user",
            "dest": "state2",
            "conditions": "is_going_to_state2",
        },
        {
            "trigger": "advance",
            "source": "search",
            "dest": "sendback",
            "conditions": "is_going_to_sendback",
        },
        {"trigger": "go_back", "source": ["search" ,"state2", "sendback"], "dest": "user"},
    ],
    initial="user",
    auto_transitions=False,
    show_conditions=True,
)

app = Flask(__name__, static_url_path="")


# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        url = find_graph(event.message.text)
        image_message = ImageSendMessage(
            original_content_url=url,
            preview_image_url=url
        )
        line_bot_api.reply_message(
            event.reply_token, image_message)
    return "OK"


@app.route("/webhook", methods=["POST"])
def webhook_handler():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        print(f"\nFSM STATE: {machine.state}")
        print(f"REQUEST BODY: \n{body}")
        response = machine.advance(event)
        if response == False:
            send_text_message(event.reply_token, "Not Entering any State")

    return "OK"


@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    machine.get_graph().draw("state.png", prog="dot", format="png")
    #return send_file("state.png", root = './',mimetype="image/png")
    fsm_url = upload_image("state.png")
    image_message = ImageSendMessage(
            original_content_url=fsm_url,
            preview_image_url=fsm_url
        )
    line_bot_api.reply_message(event.reply_token, image_message)

if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)
