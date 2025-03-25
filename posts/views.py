from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView, TemplateView
from .models import Post, Author, Category
from .filters import PostFilter
from .forms import PostForm
from parameters import *
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required

class PostsList(ListView):
    # Указываем модель, объекты которой мы будем выводить
    model = Post
    # Поле, которое будет использоваться для сортировки объектов
    ordering = '-date'
    # Указываем имя шаблона, в котором будут все инструкции о том,
    # как именно пользователю должны быть показаны наши объекты
    template_name = 'news.html'
    # Это имя списка, в котором будут лежать все объекты.
    # Его надо указать, чтобы обратиться к списку объектов в html-шаблоне.
    context_object_name = 'news'
    paginate_by = 10
    paginate_orphans = 2

class PostDetail(DetailView):
    # Модель всё та же, но мы хотим получать информацию по отдельному товару
    model = Post
    # Используем другой шаблон — product.html
    template_name = 'post.html'
    # Название объекта, в котором будет выбранный пользователем продукт
    context_object_name = 'post'

class PostSearch(ListView):
    model = Post
    ordering = '-date'
    template_name = 'search.html'
    context_object_name = 'search'
    paginate_by = 10
    paginate_orphans = 2

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем в контекст объект фильтрации.
        context['filterset'] = self.filterset
        # context['is_not_subscriber'] = self.user not in self.category.subscribers.all()
        # for post in self.object_list:
        # print(self.request.GET.getlist('category'))
        print('-------------НАЧАЛО ТУТ-------------')
        print(context['filterset'].data.getlist('category'))
        return context

class PostCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('posts.add_post',)
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):
        cur_post = form.save(commit=False)
        if 'news/' in f'{self.request}':
            cur_post.type = news
        else:
            cur_post.type = post

        return super().form_valid(form)

class PostUpdate(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    permission_required = ('posts.change_post',)
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

class PostDelete(DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_list')

@login_required
def subscribe(request, data):
    user = request.user
    categories = [int(i) for i in data.getlist('category')]
    for c_pk in categories:
        Category.objects.get(id=c_pk).add(user)
    message = 'Вы успешно подписались на выбранные категории!'
    print(data)
    return render(request, 'subscribe.html', {'categories':categories, 'message': message})
