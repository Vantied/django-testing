import pytest
from django.urls import reverse
from django.conf import settings

from news.forms import CommentForm


@pytest.mark.django_db
def test_home_page_news_count(lot_news, client):
    """На главной странице не больше 10 новостей"""
    response = client.get(reverse('news:home'))
    news_on_page = response.context['news_list']
    assert len(news_on_page) == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_home_page_news_order(lot_news, client):
    """Новости на главной странице отсортированы от свежей к старой"""
    response = client.get(reverse('news:home'))
    news_on_page = response.context['news_list']
    news_dates = [news_item.date for news_item in news_on_page]
    assert news_dates == sorted(news_dates, reverse=True)


@pytest.mark.django_db
def test_comments_order(news, comments, client):
    """Комментарии на странице новости отсортированы по времени создания"""
    url = reverse('news:detail', kwargs={'pk': news.id})
    response = client.get(url)

    news_obj = response.context.get('news') or response.context['object']
    all_comments = news_obj.comment_set.all().order_by('created')
    comment_timestamps = [comment.created for comment in all_comments]
    assert comment_timestamps == sorted(comment_timestamps)


@pytest.mark.django_db
def test_comment_form_visible_for_authenticated_user(author_client, news):
    """Форма комментария отображается для авторизованного пользователя"""
    url = reverse('news:detail', args=(news.id,))
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


@pytest.mark.django_db
def test_comment_form_not_visible_for_anonymous(client, news):
    """Форма комментария отсутствует для анонимного пользователя"""
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert 'form' not in response.context
