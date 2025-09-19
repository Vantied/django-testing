import pytest

from django.urls import reverse
from django.conf import settings

from news.forms import CommentForm


@pytest.mark.django_db
def test_home_page_news_count(a_lot_news, client):
    """На главной странице не больше 10 новостей"""
    response = client.get(reverse('news:home'))
    news_on_page = response.context['news_list']
    assert len(news_on_page) == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_home_page_news_order(a_lot_news, client):
    """Новости на главной странице отсортированы от свежей к старой"""
    response = client.get(reverse('news:home'))
    news_on_page = response.context['news_list']
    news_dates = [news_item.date for news_item in news_on_page]
    assert news_dates == sorted(news_dates, reverse=True)


@pytest.mark.django_db
def test_comments_order(news, comments, client):
    """Комментарии на странице новости отсортированы хронологически"""
    url = reverse('news:detail', kwargs={'pk': news.id})
    response = client.get(url)

    news_obj = response.context.get('news') or response.context['object']
    all_comments = news_obj.comment_set.all().order_by('created')
    comment_timestamps = [comment.created for comment in all_comments]
    assert comment_timestamps == sorted(comment_timestamps)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'client_fixture, form_visible',
    [
        ('client', False),
        ('author_client', True),
    ]
)
def test_comment_form_visibility(client_fixture, form_visible, request, news):
    """Проверяем видимость формы комментария в зависимости от пользователя"""
    client = request.getfixturevalue(client_fixture)
    response = client.get(reverse('news:detail', args=(news.id,)))

    if form_visible:
        assert 'form' in response.context
        assert isinstance(response.context['form'], CommentForm)
    else:
        assert 'form' not in response.context
