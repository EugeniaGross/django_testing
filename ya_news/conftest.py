from datetime import datetime, timedelta
import pytest

from django.conf import settings
from django.utils import timezone

from news.forms import BAD_WORDS
from news.models import Comment, News


@pytest.fixture
def new():
    new = News.objects.create(title='Заголовок', text='Текст')
    return new


@pytest.fixture
def id_for_args(new):
    return new.id,


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def comment(new, author):
    comment = Comment.objects.create(
        news=new,
        author=author,
        text='Текст'
    )
    return comment


@pytest.fixture
def comment_id_for_args(comment):
    return comment.id,


@pytest.fixture
def news():
    today = datetime.today()
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            # Для каждой новости уменьшаем дату на index дней от today,
            # где index - счётчик цикла.
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    return News.objects.bulk_create(all_news)


@pytest.fixture
def comments(new, author):
    now = timezone.now()
    # Создаём комментарии в цикле.
    for index in range(2):
        # Создаём объект и записываем его в переменную.
        comment = Comment.objects.create(
            news=new, author=author, text=f'Tекст {index}',
        )
    # Сразу после создания меняем время создания комментария.
        comment.created = now + timedelta(days=index)
    # И сохраняем эти изменения.
        comment.save()


@pytest.fixture
def form_data():
    return {'text': 'Текст комментария'}


@pytest.fixture
def bad_words_data():
    return {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
