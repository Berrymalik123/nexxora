# Deploy Nexxora for free

1. Put this project in a GitHub or GitLab repository. The repository root must contain `manage.py`, `render.yaml`, and `build.sh`.
2. Create a free PostgreSQL database at Supabase or Neon and copy its connection string. Keep the string private.
3. In Render, choose **New > Blueprint** and connect the repository.
4. Apply the blueprint using the free web-service plan. When Render asks for `DATABASE_URL`, paste the PostgreSQL connection string.
5. After the first deploy, replace `nexxora.onrender.com` in `CSRF_TRUSTED_ORIGINS` with the actual Render hostname.
6. Set `DJANGO_ALLOWED_HOSTS` to the hostname without `https://`.
7. Open the deployed URL and create the first account.

## Required production settings

Render generates `DJANGO_SECRET_KEY` and sets `DJANGO_DEBUG=False` through `render.yaml`.
Set `DATABASE_URL` manually to your free Supabase/Neon PostgreSQL connection string. Do not commit it to GitHub.

For a custom domain, set:

- `DJANGO_ALLOWED_HOSTS`: `yourdomain.com,www.yourdomain.com`
- `CSRF_TRUSTED_ORIGINS`: `https://yourdomain.com,https://www.yourdomain.com`

## Free-plan limitations

Render's free web service can sleep after inactivity, so the first request may be slow. Its local filesystem is ephemeral.

## Uploads

The current `media/` directory is local disk storage. Configure Cloudinary's free tier or an S3-compatible object-storage provider before using permanent image, video, reel, story, or chat-image uploads. Otherwise uploads can disappear after a redeploy or service restart.