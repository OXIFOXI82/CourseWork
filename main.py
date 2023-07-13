import json
import requests
import os
import datetime
from pprint import pprint
from dotenv import load_dotenv

class VK:

        def __init__(self, access_token, version='5.131'):

           self.token = access_token
           self.version = version
           self.params = {'access_token': self.token, 'v': self.version}
           self.token = access_token

        def get_picture(self, user_vk,offset=0, count=50):

            url = 'https://api.vk.com/method/photos.get'
            params = {'owner_id': user_vk,
                      'album_id': 'profile',
                      'access_token': self.token,
                      'extended': 1,
                      'v': '5.131'
                      }
            res = requests.get(url=url, params=params)
            return res.json()

class YaUploader:
    def __init__(self, token: str):
        self.token = token

    # def upload(self, file_path: str,photo: str,url: str,namedir: str):
    #     """Метод загружает файлы по списку file_list на яндекс диск"""
    #
    #     str= photo + '.jpg'
    #     params = {
    #         "path": namedir+"/"+str,
    #         'overwrite': 'true'
    #     }
    #     headers = {
    #         "Authorization": self.token
    #     }
    #     response = requests.get(url, headers=headers)
    #     if 200 <= response.status_code < 300:
    #         print(response.status_code)
    #
    #     rr = requests.get(url + r"/resources/upload", headers=headers, params=params)
    #     print(rr.json())
    #     href_for_load = rr.json()["href"]
    #
    #     with open(f'{file_path}/{str}', 'rb') as file:
    #         response2 = requests.put(href_for_load, files={"file": file})

    def uploadStrong(self, url_vk: str, photo: str, url_ya: str, namedir: str):
        urlvk = requests.get(url_vk)
        str = photo + '.jpg'
        params = {
            "path": namedir + "/" + str,
            'overwrite': 'true'
        }
        headers = {
            "Authorization": self.token
        }
        rr = requests.get(url_ya + r"/resources/upload", headers=headers, params=params)
        url_for_load = rr.json()["href"]
        load = requests.put(url_for_load, data=urlvk)
        print(f"Фото {photo} результат {load.status_code}")

    def create_dir(self,namedir: str,url: str):

        params = {
            'path': f'{namedir}',
            'overwrite': 'false'
        }
        headers = {
            "Authorization": self.token
        }

        response = requests.put(url=url+ r"/resources", headers=headers, params=params)


def Input_Output(token_vk,user_vk,token_ya,url_ya,namedir):

    vk = VK(token_vk)
    dataFromVK = vk.get_picture(user_vk)
    # YADisk
    uploader = YaUploader(token_ya)
    uploader.create_dir(namedir,url_ya)

    url_pict = []
    with open("log_file.txt", 'w', encoding='utf-8') as log:
        log.write('Начинаем считывание информации с VK \n')

    for pict in dataFromVK['response']['items']:

        max_size = 0
        max_list={}
        for pict_size in pict['sizes']:
               if pict_size['height'] >= max_size:
                   max_size = pict_size['height']
                   max_list=pict_size
        url_pict.append({
                    'url':  max_list['url'],
                    'likes': pict['likes']['count'],
                    'date': pict['date'],
                    'type':  max_list['type']
                })

    # Cортируем и отбираем 5 фото

    al = []
    for ob in url_pict:
        al.append(str(ob["likes"]) + "|" + datetime.datetime.fromtimestamp(ob["date"]).strftime(
            "%Y-%m-%d_%H-%M-%S") + "|" + ob["url"] + "|" + ob["type"])
    al.sort(reverse=True)
    like_pred = ''
    pict_json = []
    for i in range(0, 5):
        like, dated, url_vk_pict,type = al[i].split('|')
        if like == like_pred :
            pict_name = like + '_' + dated
        else:
            pict_name = like
        pict_json.append({
            'file_name': pict_name + '.jpeg',
            'size': type,
            'likes': like
        })
        like_pred = like

        # Скачиваем фотографии c VK  и записываем на ЯД
        uploader.uploadStrong(url_vk_pict,pict_name,url_ya,namedir)
        with open("log_file.txt", 'a', encoding='utf-8') as log:
            log.write(f'считана и записана фотография - {pict_name}.jpg \n')
    with open("pictures.json", "w") as file:
        json.dump(pict_json, file, indent=4)
    with open("log_file.txt", 'a', encoding='utf-8') as log:
        log.write(f'Фотографии записаны на ЯндексДиск в папку : https://disk.yandex.ru/client/disk/{namedir} \n')


if __name__ == '__main__':
    load_dotenv()
    token_vk = os.getenv('token_vk')
    user_vk = os.getenv('user_vk')
    token_ya = os.getenv('token_ya')
    url_ya = 'https://cloud-api.yandex.net:443/v1/disk'

    namedir= input('Введите наименование папки на ЯДиске : ')

    Input_Output(token_vk, user_vk, token_ya,url_ya,namedir)






