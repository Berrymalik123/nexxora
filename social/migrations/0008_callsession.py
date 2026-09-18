from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [('social', '0007_message_audio_one_time')]

    operations = [
        migrations.CreateModel(
            name='CallSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind', models.CharField(choices=[('voice', 'Voice'), ('video', 'Video')], default='voice', max_length=10)),
                ('status', models.CharField(default='ringing', max_length=12)),
                ('offer', models.JSONField(blank=True, default=dict)),
                ('answer', models.JSONField(blank=True, default=dict)),
                ('caller_candidates', models.JSONField(blank=True, default=list)),
                ('recipient_candidates', models.JSONField(blank=True, default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('caller', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='calls_started', to=settings.AUTH_USER_MODEL)),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='calls_received', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
