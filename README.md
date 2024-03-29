# Описание проекта
## Этот проект представляет собой Django приложение для создания трекера полезных и приятных привычек.
## Проект использует Poetry для управления зависимостями и средой виртуализации Python.
## В проекте используется подключение telegram-уведомлений о выполнении привычек переодических задач через celery.
## В проекте используется подключение Docker, настройки которого прописаны в файлах Dockerfile, docker-compose.yaml, .dockerignore.
## Установка

Стек: Django, DRF, CORS, Celery, unitest, flake8, Docker, PostgreSQL, Telegram

Убедитесь, что у вас установлен Python версии 3.11 и Poetry.
Клонируйте репозиторий из удаленного сервера GitHub.

Установите зависимости с помощью Poetry:
poetry install
Примените миграции:
poetry run python manage.py migrate
Запустите сервер:
python manage.py runserver
Запустите создание Docker-образа:
docker-compose up -d --build  
Проверить успешное создание Docker-образа в Docker Desktop
Запустить Docker-образ в Docker Desktop