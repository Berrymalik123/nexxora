from django import forms
from .models import Post, Reel


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content', 'image']
        widgets = {'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'What are you sharing?'})}

    def clean(self):
        cleaned = super().clean()
        image = cleaned.get('image')
        if not cleaned.get('content') and not image:
            raise forms.ValidationError('Add text or an image.')
        if image and image.size > 100 * 1024 * 1024:
            self.add_error('image', 'Image must be 100 MB or smaller.')
        return cleaned


class ReelForm(forms.ModelForm):
    class Meta:
        model = Reel
        fields = ['video', 'caption', 'thumbnail', 'audio_name']
        widgets = {
            'video': forms.ClearableFileInput(attrs={'accept': 'video/mp4,video/webm,video/quicktime,video/x-m4v'}),
            'caption': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write a caption for this post…'}),
            'audio_name': forms.TextInput(attrs={'placeholder': 'Original audio'}),
        }

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('video'):
            self.add_error('video', 'Choose a video for your reel.')
        return cleaned
