from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('social', '0006_message_reel'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='audio',
            field=models.FileField(blank=True, null=True, upload_to='messages/audio/'),
        ),
        migrations.AddField(
            model_name='message',
            name='one_time',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='message',
            name='opened_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]