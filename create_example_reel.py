import os
import shutil
import subprocess
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django

django.setup()

from django.contrib.auth import get_user_model
from PIL import Image
from posts.models import Reel

User = get_user_model()
user = User.objects.filter(username='hamza').first()
if not user:
    user = User.objects.create_user(username='hamza', password='hamza123')

media_dir = Path('media/reels')
thumb_dir = media_dir / 'thumbnails'
media_dir.mkdir(parents=True, exist_ok=True)
thumb_dir.mkdir(parents=True, exist_ok=True)

video_path = media_dir / 'example_reel.mp4'
thumb_path = thumb_dir / 'example_reel_thumb.jpg'

ffmpeg = shutil.which('ffmpeg')
if ffmpeg and not video_path.exists():
    subprocess.run([
        ffmpeg,
        '-y',
        '-f', 'lavfi',
        '-i', 'color=c=#101828:s=720x1280:d=2',
        '-vf', 'fps=24,format=yuv420p',
        '-movflags', '+faststart',
        str(video_path),
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)

if not thumb_path.exists():
    img = Image.new('RGB', (720, 1280), (16, 24, 39))
    img.save(thumb_path, format='JPEG')

reel = Reel.objects.filter(author=user).first()
if not reel:
    reel = Reel.objects.create(
        author=user,
        caption='Example reel for the Nexxora Instagram-style layout.',
        audio_name='Original audio',
        video='reels/example_reel.mp4',
        thumbnail='reels/thumbnails/example_reel_thumb.jpg',
    )
else:
    reel.caption = reel.caption or 'Example reel for the Nexxora Instagram-style layout.'
    reel.audio_name = reel.audio_name or 'Original audio'
    reel.video = reel.video or 'reels/example_reel.mp4'
    reel.thumbnail = reel.thumbnail or 'reels/thumbnails/example_reel_thumb.jpg'
    reel.save()

print(f'REEL_ID={reel.id}')
print(f'VIDEO={reel.video.name}')
print(f'THUMBNAIL={reel.thumbnail.name}')
print(f'TOTAL_REELS={Reel.objects.count()}')
