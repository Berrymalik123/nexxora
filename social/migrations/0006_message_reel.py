from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('posts', '0004_social_features'),
        ('social', '0005_message_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='reel',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.CASCADE, related_name='messages', to='posts.reel'),
        ),
    ]