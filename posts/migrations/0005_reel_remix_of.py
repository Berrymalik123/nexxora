from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('posts', '0004_social_features'),
    ]

    operations = [
        migrations.AddField(
            model_name='reel',
            name='remix_of',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='remixes', to='posts.reel'),
        ),
    ]