<<<<<<< HEAD
from datetime import datetime, timedelta

import pytest
=======
import pytest

from datetime import datetime, timedelta

>>>>>>> 2e84e9cc880724d151b294f7c73a7d096298586f
from django.test.client import Client
from django.conf import settings

from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    return News.objects.create(
        title='Заголовок',
        text='Текст заметки',
    )


@pytest.fixture
<<<<<<< HEAD
def lot_news():
=======
def a_lot_news():
>>>>>>> 2e84e9cc880724d151b294f7c73a7d096298586f
    today = datetime.today()
    news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(news)
    return news


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news,
        text='Текст комментария',
        author=author,
    )


@pytest.fixture
def comments(news, author):
    now = datetime.now()
    comment_list = []
    for index in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
        comment_list.append(comment)
    return comment_list
