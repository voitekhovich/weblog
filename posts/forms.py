from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from .models import Comment, Post


class PostForm(ModelForm):
    class Meta():
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': _('Сообщение'),
            'group': _('Группа'),
        }
        help_texts = {
            'name': _('Текст поста'),
            'group': _('Выберите группу для поста')
        }


class CommentForm(ModelForm):
    class Meta():
        model = Comment
        fields = ('text',)
