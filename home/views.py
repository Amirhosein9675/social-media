from typing import Any
from django.http import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from .models import Post
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .forms import PosteCreateUpdateForm, CreateCommentForm,PostSearchForm
from django.utils.text import slugify
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class HomeView(View):
    class_form = PostSearchForm
    def get(self, request):
        posts = Post.objects.all()
        if request.GET.get('search'):
           posts = posts.filter(body__contains = request.GET['search'])
        return render(request, 'home/index.html', {'posts': posts,'form':self.class_form})


class DetailPostView(View):
    form_class = CreateCommentForm

    def setup(self, request, *args, **kwargs):
        self.post_instance = Post.objects.get(
            pk=kwargs['post_id'], slug=kwargs['post_slug'])
        return super().setup(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        comments = self.post_instance.pcomment.filter(is_reply=False)
        return render(request, 'home/detail.html', {'post': self.post_instance, 'comments': comments, 'form': self.form_class})

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.user = request.user
            new_comment.post = self.post_instance
            new_comment.save()
            messages.success(
                request, 'your comment submitted successfuly', 'success')
            return redirect('home:detail_post', self.post_instance.id, self.post_instance.slug)


class DeletePostView(LoginRequiredMixin, View):
    def get(self, request, post_id):
        post = Post.objects.get(id=post_id)
        if (request.user.id == post.user.id):
            post.delete()
            messages.success(request, 'post delete successfully', 'success')
        else:
            messages.error(request, 'you cant delete post', 'danger')
        return redirect('home:home')


class UpdatePostView(LoginRequiredMixin, View):
    form_class = PosteCreateUpdateForm

    def setup(self, request, *args, **kwargs):
        self.instanc_post = Post.objects.get(pk=kwargs['post_id'])
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        post = self.instanc_post
        if request.user.id != post.user.id:
            messages.error(request, 'you cant update this post ', 'danger')
            return redirect('home:home')
        return super().dispatch(request, *args, **kwargs)

    def get(self, requset, post_id):
        post = self.instanc_post
        form = self.form_class(instance=post)
        return render(requset, 'home/update.html', {'form': form})

    def post(self, request, post_id):
        post = self.instanc_post
        form = self.form_class(request.POST, instance=post)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.slug = slugify(form.cleaned_data['body'][:30])
            new_post.save()
            messages.success(request, 'post updated successfully', 'success')
            return redirect('home:detail_post', post.id, post.slug)


class CreatePostView(LoginRequiredMixin, View):
    form_class = PosteCreateUpdateForm

    def get(self, request):
        form = self.form_class()
        return render(request, 'home/create.html', {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.slug = slugify(form.cleaned_data['body'][:30])
            new_post.user = request.user
            new_post.save()
            messages.success(request, 'new post create successfully', 'succes')
            return redirect('home:detail_post', new_post.id, new_post.slug)
