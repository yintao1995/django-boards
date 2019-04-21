from django.test import TestCase
from django.urls import reverse, resolve
from boards.views import TopicListView
from boards.models import Board



class BoardTopicsTests(TestCase):
    def setUp(self):
        Board.objects.create(name='Django', description='Django board.')

    def test_board_topics_view_success_status_code(self):
        url = reverse('board_topics',kwargs={'pk':1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_board_topics_view_not_found_status_code(self):
        url = reverse('board_topics',kwargs={'pk':99})
        # print(url)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


    def test_board_topics_url_resolves_board_topics_view(self):
        view = resolve('/boards/1/')
        self.assertEqual(view.func.view_class, TopicListView)

    def test_board_topics_view_contains_link_back_to_homepage(self):
        board_topics_url =reverse('board_topics',kwargs={'pk':'1'})
        response = self.client.get(board_topics_url)
        homepage_url1 = reverse('home')
        # print(homepage_url1)            #   /
        # print(response)
        # print('href="{}"'.format(homepage_url1))        #href="/"
        self.assertContains(response, 'href="{0}"'.format(homepage_url1))
        # response  类型 <class 'django.http.response.HttpResponse'>
        # 等价于 self.assertContains(response,"href="+'"'+homepage_url1+'"')

    def test_board_topics_view_contains_navigation_links(self):
        board_topics_url = reverse('board_topics',kwargs={'pk':1})
        homepage_url = reverse('home')
        new_topic_url = reverse('new_topic', kwargs={'pk':1})
        response = self.client.get(board_topics_url)
        self.assertContains(response, 'href="{0}"'.format(homepage_url))
        self.assertContains(response,'href="{0}"'.format(new_topic_url))
