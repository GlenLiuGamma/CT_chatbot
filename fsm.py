from transitions.extensions import GraphMachine
from utils import send_text_message
import requests
import urllib.request
from bs4 import BeautifulSoup
from upload_image import upload_image
import os
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
            html = requests.get(item.get('src')) # use 'get' to get photo link path 
            img_name = folder_path + str(index + 1) + '.png'
            with open(img_name,'wb') as file: #以byte的形式將圖片數據寫入
                file.write(html.content)
                file.flush()
            file.close() #close file
        
    link = upload_image(img_name)    
    print('Done')
    return link


class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)

    def is_going_to_search(self, event):
        text = event.message.text
        return text.lower() == "搜尋"

    def is_going_to_sendback(self, event):
        text = event.message.text
        return text!=""

    def is_going_to_state2(self, event):
        text = event.message.text
        return text.lower() == "go to state2"

    def on_enter_search(self, event):
        print("entering search")
        reply_token = event.reply_token
        send_text_message(reply_token, "請輸入要搜尋的內容")
        #self.go_back()

    def on_enter_sendback(self, event):
        print("entering sendback")
        reply_token = event.reply_token
        url = find_graph(event.message.text)
        send_text_message(reply_token, url)
        self.go_back()

    """
    def on_exit_search(self):
        print("Leaving search")
    """

    def on_exit_sendback(self):
        print("Leaving sendback")

    def on_enter_state2(self, event):
        print("I'm entering state2")

        reply_token = event.reply_token
        send_text_message(reply_token, "Trigger state2")
        self.go_back()

    def on_exit_state2(self):
        print("Leaving state2")
