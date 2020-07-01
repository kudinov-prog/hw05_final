from django import forms
from .models import Group, Post, Comment


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ['group', 'text', 'image']
        labels = {'group': 'Группа', 'text': 'Текст', 'image': 'Картинка'}
        help_texts = {
            'group': 'Если знаете тематику, то выберите группу!',
            'text': 'Постарайтесь выкладывать годный контент!',
            'image': 'Выберите картинку!'
            }


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ['text']
        labels = {'text': 'Текст'}
        help_texts = {'text': 'Введите комментарий!'}
