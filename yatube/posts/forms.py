from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("text", "group", "image")
        label = {"text": "Напишите что-нибудь", "group": "Выберите группу"}
        help_text = {
            "text": "Самое время печатать буквы",
            "group": "Нужно выбрать группу",
        }

    def clean_text(self):
        text = self.cleaned_data["text"]
        if text == " ":
            raise forms.ValidationError("Напишите что-нибудь")
        return text


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        label = {
            'text': 'Напишите текст комментария'
        }

    def clean_text(self):
        text = self.cleaned_data["text"]
        if text == " ":
            raise forms.ValidationError('Напишите комментарий')
        return text
