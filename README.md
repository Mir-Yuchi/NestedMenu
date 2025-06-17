# NestedMenu

NestedMenu — это гибкое Django‑приложение для создания и рендеринга многоуровневых (вложенных) меню с минимальным числом запросов к базе и встроенным кэшированием.

## Содержание

- [Особенности](#особенности)
- [Установка](#установка)
- [Использование](#использование)
- [Тестирование](#тестирование)


## Особенности

- **Иерархические меню**: Неограниченная вложенность пунктов меню.
- **Оптимизированные запросы**: Один запрос к базе данных с использованием `select_related`.
- **Кэширование**: Данные меню кэшируются на 1 час.
- **Выделение активного пункта**: Автоматическое выделение текущей страницы.
- **Интерактивные классы**: Использование класса `menu-toggle` для пунктов с подменю.
- **Доступность**: ARIA атрибуты улучшают доступность.
- **Предотвращение циклов**: Защита от циклических ссылок в модели меню.
- **Тестирование**: 8 тестов, охватывающих рендеринг, запросы и крайние случаи.
- **Code style**: Соответствие PEP 8 и PEP 257, использование `black` и `isort` для форматирования кода.

## Установка

1. **Клонировать репозиторий**
   ```bash
   git clone https://github.com/Mir-Yuchi/NestedMenu.git
   cd NestedMenu
   ```

2. **Создать виртуальное окружение**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Установить зависимости**
   ```bash
   pip install poetry
   poetry install
   ```

4. **Настроить переменные окружения**
   Создайте файл `.env` со следующим содержимым:
   ```env
   POSTGRES_DB=your_database_name
   POSTGRES_USER=your_database_user
   POSTGRES_PASSWORD=your_database_password

   DB_NAME=your_database_name
   DB_USER=your_database_user
   DB_PASSWORD=your_database_password
   DB_HOST=localhost или db # если используете Docker
   DB_PORT=5432
   ```

5. **Примените миграции и создайте суперпользователя:**
   ```bash
   poetry run python manage.py migrate
   poetry run python manage.py createsuperuser
   ```

6. **Запустить сервер**
   ```bash
   python manage.py runserver
   ```

### Установка через Docker

Для быстрого развёртывания с использованием Docker.

Соберите Docker-образ:
   ```bash
      docker-compose up --build
   ```


## Использование

- **Создание пунктов меню**
  Через админку Django по адресу `/admin/menus/menuitem/` или с помощью кода:
  ```python
  from menus.models import MenuItem
  MenuItem.objects.create(menu_name="main", title="Home", url="/", order=0)
  ```

- **Рендеринг меню**
  Используйте пользовательский тэг шаблона в ваших шаблонах:
  ```html
    {% load menus %}
    <!DOCTYPE html>
    <html>
    <head><title>Мой сайт</title></head>
    <body>
        {% draw_menu 'main' %}
        <!-- остальная разметка -->
    </body>
    </html>
  ```

- **Стилизация**
  Используются классы Tailwind CSS. Настройте стили через CSS или измените `menus.py` по мере необходимости.

## Тестирование

Запустите тесты командой:
```bash
pytest --maxfail=1 --disable-warnings -q
```

Тесты проверяют:

- Один оптимизированный запрос к базе данных.
- Корректный рендеринг классов active и open.
- Работу интерактивных классов (menu-toggle, level-N).
- Предотвращение циклов в меню.
- Правильный рендеринг домашней страницы.
- Эффективное кэширование.
