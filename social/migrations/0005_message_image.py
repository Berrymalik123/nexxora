from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('social', '0004_alter_report_reason'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='messages/images/'),
        ),
    ]