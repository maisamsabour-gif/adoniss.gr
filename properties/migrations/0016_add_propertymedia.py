"""
Step 1 of 3 – add the PropertyMedia table.
Old columns (main_image, image_2..20, video, video_poster) are kept here
so the data migration in 0017 can still read them.
"""
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0015_add_images_16_to_20'),
    ]

    operations = [
        migrations.CreateModel(
            name='PropertyMedia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(
                    blank=True, upload_to='properties/gallery/',
                    verbose_name='Photo',
                    help_text='Upload a photo. HEIC/iPhone photos are automatically converted to JPEG.',
                )),
                ('video', models.FileField(
                    blank=True, upload_to='properties/videos/',
                    verbose_name='Video',
                    help_text='MP4 recommended, max 500 MB. Leave blank when uploading a photo.',
                )),
                ('poster', models.ImageField(
                    blank=True, upload_to='properties/posters/',
                    verbose_name='Video Poster',
                    help_text='Thumbnail shown before the video plays (only used with a video).',
                )),
                ('caption', models.CharField(blank=True, max_length=200, verbose_name='Caption / Alt text')),
                ('is_cover', models.BooleanField(
                    default=False, verbose_name='Cover photo',
                    help_text='Mark as the main/cover image shown in property cards.',
                )),
                ('order', models.PositiveIntegerField(
                    default=0, verbose_name='Order',
                    help_text='Lower numbers appear first in the gallery.',
                )),
                ('property', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='media',
                    to='properties.property',
                    verbose_name='Property',
                )),
            ],
            options={
                'verbose_name': 'Media',
                'verbose_name_plural': 'Media',
                'ordering': ['order', 'pk'],
            },
        ),
    ]
