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
### Prerequisites

What things you need to install the software and how to install them

```
Give examples
```

### Installing

A step by step series of examples that tell you have to get a development env running

Say what the step will be

```
Give the example
```

And repeat

```
until finished
```

End with an example of getting some data out of the system or using it for a little demo

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone who's code was used
* Inspiration
* etc

