from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from profiles.models import Profile
from social.models import Message
from .models import Reel


@override_settings(ALLOWED_HOSTS=['localhost', 'testserver'])
class ReelsPageTests(TestCase):
    def test_reels_page_loads(self):
        User = get_user_model()
        user = User.objects.create_user(username='hamza', password='hamza123')

        self.client.force_login(user)
        response = self.client.get('/reels/', HTTP_HOST='localhost')

        self.assertEqual(response.status_code, 200)

    def test_reel_can_be_sent_to_followed_friend(self):
        User = get_user_model()
        sender = User.objects.create_user(username='sender', password='sender123')
        friend = User.objects.create_user(username='friend', password='friend123')
        Profile.objects.get(user=friend).followers.add(sender)
        reel = Reel.objects.create(author=sender, caption='Test reel')

        self.client.force_login(sender)
        response = self.client.post(
            f'/social/messages/share-reel/{reel.id}/',
            {'usernames': [friend.username], 'text': 'Watch this!'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['ok'])
        message = Message.objects.get(sender=sender, recipient=friend)
        self.assertEqual(message.text, 'Watch this!')
        self.assertEqual(message.reel, reel)

    def test_recipient_can_open_one_time_message_once(self):
        User = get_user_model()
        sender = User.objects.create_user(username='once_sender', password='sender123')
        recipient = User.objects.create_user(username='once_recipient', password='recipient123')
        message = Message.objects.create(
            sender=sender,
            recipient=recipient,
            text='Private voice note',
            one_time=True,
        )

        self.client.force_login(recipient)
        response = self.client.get(f'/social/messages/{sender.username}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Open once')

        response = self.client.post(
            f'/social/messages/one-time/{message.id}/open/',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest',
        )
        self.assertEqual(response.status_code, 200)
        message.refresh_from_db()
        self.assertIsNotNone(message.opened_at)

        response = self.client.get(f'/social/messages/{sender.username}/')
        self.assertNotContains(response, 'Private voice note')

    def test_user_can_copy_the_reel_sound(self):
        User = get_user_model()
        source_author = User.objects.create_user(username='source', password='source123')
        remixer = User.objects.create_user(username='remixer', password='remixer123')
        source = Reel.objects.create(author=source_author, caption='Original reel', audio_name='Original audio')

        self.client.force_login(remixer)
        response = self.client.post(f'/reels/remix/{source.id}/')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['ok'])
        self.assertEqual(response.json()['audio_name'], 'Original audio')
        self.assertIn('copied', response.json()['message'].lower())
