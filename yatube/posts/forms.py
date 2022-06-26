from django.forms import ModelForm

from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ["text", "group", "image"]
        labels = {
            'text': 'Текст поста',
            'group': 'Группа',
            'image': 'Изображение'
        }
        help_text = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост',
            'image': 'Добавить изображение'
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
