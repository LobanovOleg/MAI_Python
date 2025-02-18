# Авторизация  
## Шаги запуска программы  
1. python -m venv .venv  
2. source .venv/bin/activate  
3. pip install -r requirements.txt  
4. uvicorn main:app --reload  
## Далее есть 2 способа проверки 
1. Использовать в соседнем окне терминала команды  
2. Подключиться через браузер  

## Первый способ
1. Запустите программу  
2. Откройте соседнее окно терминала  
3. Введите следующие команды:  
    а. Команда для регистрации пользователя  
        curl -X POST "http://127.0.0.1:8000/register" -H "Content-Type: application/json" -d '{"email": "user@example.com", "password": "password"}'  
    в. Команда для получения токена  
        curl -X POST "http://127.0.0.1:8000/token" -H "Content-Type: application/x-www-form-urlencoded" -d "username=user@example.com&password=password"  
    с. Использовать токен для получения информации о пользователе  
        curl -X GET "http://127.0.0.1:8000/me" -H "Authorization: Bearer ваш_токен"  

## Второй способ  
1. Запустите программу  
2. Откройте браузер  
3. Введите данный адрес http://127.0.0.1:8000/docs  
4. В default можно испытать команды