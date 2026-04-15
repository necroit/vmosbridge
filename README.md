# VMOS Roblox Telegram Bot

Telegram бот для управления запуском Roblox на Android через VMOS/Termux.

## Возможности
- Запуск нескольких экземпляров Roblox с задержкой
- Остановка всех процессов Roblox
- Мониторинг системы (память, процессы)
- Скриншоты экрана
- Автообновление через Git
- Защита доступа (только админ)

## Установка

### 1. Клонирование репозитория
```bash
git clone https://github.com/yourusername/vmosbridge.git
cd vmosbridge
```

### 2. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 3. Настройка
```bash
python setup.py
```
Введите:
- API ID и API Hash (с https://my.telegram.org/)
- Bot Token (с @BotFather)
- Ваш Telegram User ID
- Количество экземпляров Roblox
- Задержка между запусками
- Ссылки на Roblox (через запятую)

### 4. Запуск
```bash
python main.py
```

## Команды бота
- `/start` - Запустить Roblox в Freeform окнах (автоматически активирует Freeform режим)
- `/stop` - Остановить Roblox
- `/status` - Статус системы (память в МБ/ГБ, процессы)
- `/optimize` - МАКСИМАЛЬНАЯ оптимизация системы для лучшей производительности
- `/setup` - Перезапуск настройки
- `/update` - Обновление кода

## Автозапуск в Termux
```bash
mkdir -p ~/.termux/boot
cp scripts/start.sh ~/.termux/boot/start.sh
chmod +x ~/.termux/boot/start.sh
```
Отредактируйте путь в `start.sh`.

## Безопасность
- Только владелец с `admin_id` может использовать бота
- `config.json` не загружается в Git (в .gitignore)
- Используйте private репозиторий

## Структура проекта
```
vmosbridge/
├── bot/              # Telegram бот
├── launcher/         # Управление Roblox
├── utils/            # Утилиты
├── config/           # Конфигурация
├── scripts/          # Скрипты
├── main.py           # Точка входа
├── setup.py          # Настройка
├── requirements.txt  # Зависимости
└── README.md         # Этот файл
```