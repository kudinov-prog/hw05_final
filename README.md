# Социальная сеть Yatube

Социальная сеть для обмена заметками. Позволяет подписываться, отписываться, просматривать ленту избранных авторов, оставлять комментарии. У каждого зарегестрированного пользователся есть своя страничка с профайлом.

## Запуск локально
Клонируем репозиторий к себе на машину коммандой 
```
git clone <link>
```
Создаем виртуальное окружение для проeкта
```
python -m venv venv
```
Активируем его
```
source venv/scripts/activate
```
Устанавливаем необходимые зависимости (они находятся в файле проекта requirements.txt)
```
pip install -r requirements.txt
```
Делаем миграции моделей в базу данных
```
python manage.py makemigrations
python manage.py migrate
```
Запускаем локальный сервер проекта
```
python manage.py runserver
```
Если все сделано правильно, то появится следующая надпись, и проект развернется по адресу http://127.0.0.1:8000/
```
System check identified no issues (0 silenced).
December 02, 2020 - 21:02:38
Django version 3.0.8, using settings 'yatube.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```
