from django.db import migrations, models
class Migration(migrations.Migration):
    dependencies=[('social','0002_platform_features')]
    operations=[migrations.AddField(model_name='contentview',name='session_key',field=models.CharField(blank=True,default='',max_length=100))]
