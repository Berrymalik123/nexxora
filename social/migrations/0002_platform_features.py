from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies=[('social','0001_initial')]
    operations=[
      migrations.AddField(model_name='story',name='text',field=models.TextField(blank=True,max_length=1000)),
      migrations.AddField(model_name='story',name='story_type',field=models.CharField(choices=[('media','Media'),('text','Text')],default='media',max_length=10)),
      migrations.AlterField(model_name='story',name='media',field=models.FileField(blank=True,null=True,upload_to='stories/')),
      migrations.CreateModel(name='StorySeen',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('seen_at',models.DateTimeField(auto_now_add=True)),('story',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='seen_by',to='social.story')),('user',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,to='accounts.user'))],options={'unique_together':{('user','story')}}),
      migrations.CreateModel(name='Message',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('text',models.TextField(max_length=2000)),('created_at',models.DateTimeField(auto_now_add=True)),('is_read',models.BooleanField(default=False)),('recipient',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='received_messages',to='accounts.user')),('sender',models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,related_name='sent_messages',to='accounts.user'))],options={'ordering':['created_at']}),
      migrations.CreateModel(name='DeviceSession',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('device_token',models.CharField(max_length=128,unique=True)),('session_key',models.CharField(blank=True,max_length=100)),('last_seen',models.DateTimeField(auto_now=True)),('expires_at',models.DateTimeField()),('user',models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,related_name='device_session',to='accounts.user'))]),
      migrations.CreateModel(name='TwoFactorCode',fields=[('id',models.BigAutoField(auto_created=True,primary_key=True,serialize=False,verbose_name='ID')),('code_hash',models.CharField(max_length=128)),('expires_at',models.DateTimeField()),('attempts',models.PositiveIntegerField(default=0)),('user',models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,related_name='two_factor_code',to='accounts.user'))]),
    ]
