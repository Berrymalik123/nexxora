from django import forms
from .models import Post, Reel
class PostForm(forms.ModelForm):
    class Meta:
        model=Post
        fields=['content','image','video']
        widgets={'content':forms.Textarea(attrs={'rows':4,'placeholder':'What are you sharing?'})}
    def clean(self):
        cleaned=super().clean(); image=cleaned.get('image'); video=cleaned.get('video')
        if not cleaned.get('content') and not image and not video: raise forms.ValidationError('Add text, an image, or a video.')
        if image and image.size>100*1024*1024: self.add_error('image','Image must be 100 MB or smaller.')
        if video and video.size>100*1024*1024: self.add_error('video','Video must be 100 MB or smaller.')
        return cleaned
class ReelForm(forms.ModelForm):
    class Meta:
        model=Reel
        fields=['caption','video','thumbnail','audio_name']
        widgets={'caption':forms.Textarea(attrs={'rows':3,'placeholder':'Write a reel caption…'}),'audio_name':forms.TextInput(attrs={'placeholder':'Original audio'})}
    def clean_video(self):
        video=self.cleaned_data.get('video')
        if video and video.size>100*1024*1024: raise forms.ValidationError('Reel must be 100 MB or smaller.')
        return video
