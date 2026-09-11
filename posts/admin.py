from django.contrib import admin
from .models import Post,Like,Save,Share,Comment,Reel,ReelLike,ReelSave,ReelShare,ReelComment,Hashtag
for m in [Post,Like,Save,Share,Comment,Reel,ReelLike,ReelSave,ReelShare,ReelComment,Hashtag]: admin.site.register(m)
