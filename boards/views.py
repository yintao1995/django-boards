from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import  Board, Post, Topic
from django.contrib.auth.models import User
from django.db.models import Count
from django.http import Http404
from boards.forms import NewTopicForm, PostForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView, ListView
from django.utils import timezone
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.


# 基于函数的视图 Function-Based Views
# def home(request):
#     boards = Board.objects.all()
#     return render(request, 'home.html', {'boards': boards})
#     # 第三个参数是将本处的boards 传递给 html语句中的 boards

#基于类的视图 Class-Based Views
class BoardListView(ListView):
    model = Board
    context_object_name = 'boards'
    template_name = 'home.html'


def home2(request):
    return HttpResponse('<a href="http://www.baidu.com">hello again~</a>')


def about(request):
    return render(request, 'about.html')
    # return HttpResponse('About Page')


# def board_topics(request,  pk):
#     board = get_object_or_404(Board, pk=pk)
#     queryset = board.topics.order_by('-last_updated').annotate(replies=Count('posts')-1) # 可用topic.replies访问回复数
#     page = request.GET.get('page', 1)   # 第一页
#     paginator = Paginator(queryset, 20) # 每页显示20个对象
#     try:
#         topics = paginator.page(page)
#     except PageNotAnInteger:    # 页数不是整数，则显示第一页
#         topics = paginator.page(1)
#     except EmptyPage:
#         topics = paginator.page(paginator.num_pages)    # 页面不存在，则显示最后一页
#     return render(request, 'topics.html', {'board':board, 'topics': topics})


class TopicListView(ListView):
    model = Topic
    context_object_name = 'topics'
    template_name = 'topics.html'
    paginate_by = 20

    def get_context_data(self, *, object_list=None, **kwargs):
        kwargs['board'] = self.board
        return super(TopicListView, self).get_context_data(**kwargs)

    def get_queryset(self):
        self.board = get_object_or_404(Board, pk=self.kwargs.get('pk'))
        queryset = self.board.topics.order_by('-last_updated').annotate(replies=Count('posts')-1)
        return queryset


@login_required
def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)
    # user = User.objects.first() # 从数据库查询出来的第一个用户
    if request.method == 'POST': # 发送，提交表格时发送
        form = NewTopicForm(request.POST)
        if form.is_valid(): # 表单有效则返回前面的链接，无效则提示无效不返回
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = request.user
            topic.save()
            post = Post.objects.create(
                message =form.cleaned_data.get('message'),
                topic = topic,
                created_by = request.user
            )
            return redirect('board_topics',pk=pk) # TODO:redirect to the created topic page
        else:
            pass
    else: # GET 请求，则新建一个表格
        form=NewTopicForm()
    return render(request, 'new_topic.html', {'board':board,'form':form})


# def topic_posts(request, pk, topic_pk):
#     topic = get_object_or_404(Topic, board__pk = pk, pk=topic_pk) #board__pk是双下划线
#     topic.views += 1
#     topic.save()
#     return render(request, 'topic_posts.html', {'topic':topic})


class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'topic_posts.html'
    paginate_by =10

    def get_context_data(self, *, object_list=None, **kwargs):
        session_key = 'viewed_topic_{}'.format(self.topic.pk)
        if not self.request.session.get(session_key, False):
            self.topic.views += 1
            self.topic.save()
            self.request.session[session_key]=True
        kwargs['topic'] = self.topic
        # print(type(kwargs)) # 字典
        return super(PostListView, self).get_context_data(**kwargs)

    def get_queryset(self):
        self.topic = get_object_or_404(Topic, board__pk =self.kwargs.get('pk'), pk=self.kwargs.get('topic_pk'))
        queryset = self.topic.posts.order_by('created_at')
        return queryset


@login_required
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by=request.user
            post.save()
            topic.last_updated = timezone.now()
            topic.save()
            topic_url = reverse('topic_posts', kwargs={'pk':pk, 'topic_pk':topic_pk})
            topic_post_url = '{url}?page={page}#{id}'.format(
                url = topic_url,
                id=post.pk,
                page=topic.get_page_count()
            )
            return redirect(topic_post_url)
    else:
        form = PostForm()
    return render(request, 'reply_topic.html',{'topic':topic,'form':form})


@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    fields = ('message', )
    template_name = 'edit_post.html'
    pk_url_kwarg = 'post_pk'
                #
                # ⽤于检索 Post 对象的关键字参数的名称。从url直接访问时，即使board.pk和topic.pk乱写,
                # 只要post_pk对了就能打开对应的页面，前提是post_pk一一对应
    context_object_name = 'post'

    def get_queryset(self):
        queryset = super(PostUpdateView, self).get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect('topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)
