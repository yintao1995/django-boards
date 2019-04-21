from django.test import TestCase
from django.urls import reverse, resolve
# from boards.views import home
from boards.views import BoardListView
from boards.models import Board


class HomeTests(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name='Django', description='Django board.')
        url = reverse('home') # reverse从 标识符名称 反解析 出url
        self.response = self.client.get(url)

    def test_home_view_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_home_url_resolves_home_view(self):
        view = resolve('/')    # resolve 从相对url解析视图
        # self.assertEqual(view.func, home)
        self.assertEqual(view.func.view_class, BoardListView)

    def test_home_view_contains_link_to_topics_page(self):
        board_topics_url = reverse('board_topics', kwargs={'pk':self.board.pk})
        self.assertContains(self.response, 'href="{0}'.format(board_topics_url))
