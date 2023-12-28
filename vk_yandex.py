import requests
import os
import yadisk
import json

def get_vk_photos(user_id, access_token, folder_path):
    url = 'https://api.vk.com/method/photos.get'
    params = {
        'owner_id': user_id,
        'album_id': 'profile',
        'extended': 1,
        'photo_sizes': 1,
        'access_token': access_token,
        'v': '5.131'  # Версия API
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        photos_data = response.json()['response']['items']
        download_photos(photos_data, folder_path)
    else:
        print("Ошибка при получении данных с VK")


def download_photos(photos, folder_path):
    for index, photo in enumerate(photos):
        likes = photo['likes']['count']
        photo_url = photo['sizes'][-1]['url']

        # Формирование имени файла с учетом количества лайков
        file_name = f"{likes}_likes.jpg"
        file_path = os.path.join(folder_path, file_name)

        # Если есть файл с таким же именем, добавляем уникальный суффикс
        suffix = 1
        while os.path.exists(file_path):
            file_name = f"{likes}_likes_{suffix}.jpg"
            file_path = os.path.join(folder_path, file_name)
            suffix += 1

        # Скачиваем и сохраняем фото
        response = requests.get(photo_url)
        if response.status_code == 200:
            with open(file_path, 'wb') as f:
                f.write(response.content)
                print(f"Фото {file_name} загружено")
        else:
            print(f"Ошибка при загрузке фото {file_name}")


# Путь к папке, куда сохранить фотографии
folder_path = r'M:\Programs\Python_Git\vk_yandex\phot'

user_id = input("Введите ID пользователя VK: ")  # ID пользователя VK
token = input("Введите токен доступа VK API: ")  # Токен доступа VK API

get_vk_photos(user_id, token, folder_path)

def upload_to_yandex_disk(folder_path, yandex_folder_url, yandex_token):
    photos = os.listdir(folder_path)
    uploaded_files = []  # Список для хранения информации о загруженных файлах

    for photo in photos:
        photo_path = os.path.join(folder_path, photo)
        headers = {"Authorization": f"OAuth {yandex_token}"}

        # Создаем ресурс для загрузки на Яндекс.Диск
        response = requests.get(
            f"https://cloud-api.yandex.net/v1/disk/resources/upload?path=/vk_yandex/{photo}&overwrite=true",
            headers=headers
        )

        if response.status_code == 200:
            upload_url = response.json()['href']

            with open(photo_path, 'rb') as f:
                # Загружаем фото на Яндекс.Диск методом PUT
                upload_response = requests.put(upload_url, headers=headers, files={"file": f})

                if upload_response.status_code == 201:
                    print(f"Фото {photo} успешно загружено на Яндекс.Диск")
                    uploaded_files.append({"file_name": photo, "size": os.path.getsize(photo_path)})
                else:
                    print(f"Ошибка при загрузке фото {photo} на Яндекс.Диск")
        else:
            print(f"Ошибка при получении ссылки для фото {photo}")

    # Путь для сохранения JSON-файла в той же папке, что и фотографии
    json_path = os.path.join(folder_path, 'uploaded_files.json')

    # Создаем JSON-файл с информацией о загруженных файлах
    with open(json_path, 'w') as json_file:
        json.dump(uploaded_files, json_file)


folder_path = r'M:\Programs\Python_Git\vk_yandex\phot'
yandex_folder_url = 'https://disk.yandex.lt/client/disk'
yandex_token = input("Введите токен Яндекс.Диска: ")

upload_to_yandex_disk(folder_path, yandex_folder_url, yandex_token)