from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages

from django.views import generic
from django.http import Http404

from braces.views import SelectRelatedMixin

from . import models
from . import forms

import pdb
from django.contrib.auth import get_user_model
User = get_user_model()

class PostList(SelectRelatedMixin, generic.ListView):
    model = models.Post
    select_related = ('user', 'group')

class UserPosts(generic.ListView):
    model = models.Post
    template_name = 'posts/user_post_list.html'

    def get_queryset(self):
        try:
            self.post_user = User.objects.prefetch_related('posts').get(username__iexact=self.kwargs.get('username'))
        except User.DoesNotExist:
            raise Http404
        else:
            return self.post_user.posts.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_user'] = self.post_user
        return context 

class PostDetail(SelectRelatedMixin, generic.DetailView):
    model = models.Post
    select_related = ('user', 'group')
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user__username__iexact=self.kwargs.get('username'))

class CreatePost(LoginRequiredMixin, SelectRelatedMixin, generic.CreateView):
    fields = ('message', 'group')
    model = models.Post

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user 
        self.object.save()
        return super().form_valid(form)

    
# def DeletePost(self,*args, **kwargs):
#     pdb.set_trace()
#     context = {
#         'posts': models.Post.objects.get(id=self.request.user.id).delete()
#     }
#     return redirect('', context)
class DeletePost(LoginRequiredMixin, SelectRelatedMixin, generic.DeleteView):
    model = models.Post
    select_related = ('user', 'group')
    success_url = reverse_lazy('posts:all')
    # def get_queryset(self):
    #     print('Hello2')
    #     queryset = super().get_queryset()   
    #     return queryset.filter(user_id = self.request.user.id)

    def delete(self,request, *args, **kwargs):
        self.object = self.get_object(self.request.user.id)
        can_delete = self.object.can_delete()
        if can_delete:
            return super(DeletePost, self).delete(request, *args, **kwargs)
        else:
            raise Http404('Object you are looking for doesn\'t exist')