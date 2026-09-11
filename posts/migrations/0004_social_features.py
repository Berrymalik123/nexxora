from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies=[('posts','0003_alter_post_image')]
    operations=[
      migrations.AddField(model_name='post',name='updated_at',field=models.DateTimeField(auto_now=True)),
      migrations.AddField(model_name='post',name='is_public',field=models.BooleanField(default=True)),
      migrations.AddField(model_name='reel',name='thumbnail',field=models.ImageField(blank=True,null=True,upload_to='reels/thumbnails/')),
      migrations.AddField(model_name='reel',name='audio_name',field=models.CharField(blank=True,default='Original audio',max_length=120)),
      migrations.AddField(model_name='reel',name='updated_at',field=models.DateTimeField(auto_now=True)),
      migrations.CreateModel(name='Save',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('created_at',models.DateTimeField(auto_now_add=True)),('post',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='saves',to='posts.post')),('user',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to='accounts.user'))],options={'unique_together':{('user','post')}}),
      migrations.CreateModel(name='Share',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('created_at',models.DateTimeField(auto_now_add=True)),('post',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='shares',to='posts.post')),('user',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to='accounts.user'))]),
      migrations.CreateModel(name='ReelSave',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('created_at',models.DateTimeField(auto_now_add=True)),('reel',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='saves',to='posts.reel')),('user',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to='accounts.user'))],options={'unique_together':{('user','reel')}}),
      migrations.CreateModel(name='ReelShare',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('created_at',models.DateTimeField(auto_now_add=True)),('reel',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='shares',to='posts.reel')),('user',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to='accounts.user'))]),
      migrations.CreateModel(name='ReelComment',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('content',models.TextField()),('created_at',models.DateTimeField(auto_now_add=True)),('reel',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='comments',to='posts.reel')),('user',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to='accounts.user'))]),
      migrations.CreateModel(name='Hashtag',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('name',models.CharField(max_length=80,unique=True)),('posts',models.ManyToManyField(blank=True,related_name='hashtags',to='posts.post')),('reels',models.ManyToManyField(blank=True,related_name='hashtags',to='posts.reel'))]),
    ]
