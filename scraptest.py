import requests
import urllib.request
from bs4 import BeautifulSoup
import os

def find_graph(word):
    #word = input('Input key word: ')
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
            #print('第 %d 張' % (index + 1))
    print('Done')