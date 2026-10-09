# Тесты для Django-проектов YaNews и YaNote

Набор автотестов для двух Django-приложений: новостного сайта с комментариями YaNews (pytest) и сервиса заметок YaNote (unittest).

## Что покрыто тестами

**YaNews — pytest и pytest-django**
- Доступность страниц для анонимных и авторизованных пользователей, редиректы на страницу входа.
- Контент: количество и порядок новостей на главной, сортировка комментариев, видимость формы комментария.
- Логика: создание комментариев, запрет на запрещённые слова, редактирование и удаление только автором.

**YaNote — unittest (Django TestCase)**
- Доступность страниц и защита чужих заметок.
- Контент: в списке только свои заметки, формы на страницах создания и редактирования.
- Логика: создание заметки, уникальность и автоматическая генерация slug, редактирование и удаление только автором.

Всего 26 тестовых функций, часть из них параметризована.

## Технологии

Python 3.10+, Django 5.1, pytest, pytest-django, pytest-lazy-fixture, unittest.

## Как запустить

```bash
git clone https://github.com/Vantied/django-testing.git
cd django-testing
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
bash run_tests.sh
```

## Что я вынес из проекта

- Тестирование маршрутов, контента и бизнес-логики Django-приложений.
- Фикстуры и параметризация в pytest, подтесты в unittest.

## Автор

Иван Богатов — [GitHub](https://github.com/Vantied) · Telegram [@Ivan_bogatov55](https://t.me/Ivan_bogatov55)
