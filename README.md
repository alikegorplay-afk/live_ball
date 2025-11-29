# Парсер сайта [liveball.sx](https://liveball.sx)

##  Предварительные требования
1. Python 3.13+
2. pip (менеджер пакетов Python)

# Установка и запуск
## Клонирование репозитория

```bash
git clone https://github.com/alikegorplay-afk/live_ball.git
cd live_ball
```

## Установка зависимостей

```bash
pip install -r requirements.txt
```

## Настройка браузера

```bash
playwright install chromium
```

## Запуск парсера
```bash
python main.py
```

## Альтернативная установка (для виртуального окружения)
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
# или
venv\Scripts\activate     # для Windows
pip install -r requirements.txt
playwright install chromium
```