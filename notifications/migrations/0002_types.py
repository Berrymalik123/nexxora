from django.db import migrations, models
class Migration(migrations.Migration):
 dependencies=[('notifications','0001_initial')]
 operations=[migrations.AlterField(model_name='notification',name='notification_type',field=models.CharField(choices=[('follow','Follow'),('like','Like'),('comment','Comment'),('share','Share'),('story','Story')],max_length=20))]
