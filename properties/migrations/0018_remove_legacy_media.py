"""
Step 3 of 3 – remove legacy image/video columns from Property and drop the
old PropertyImage table now that all data lives in PropertyMedia.
"""
from django.db import migrations


OLD_COLUMNS = [
    'main_image',
    'image_2',  'image_3',  'image_4',  'image_5',
    'image_6',  'image_7',  'image_8',  'image_9',  'image_10',
    'image_11', 'image_12', 'image_13', 'image_14', 'image_15',
    'image_16', 'image_17', 'image_18', 'image_19', 'image_20',
    'video',
    'video_poster',
]


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0017_migrate_media_data'),
    ]

    operations = [
        # Drop each legacy image/video column from Property
        *[
            migrations.RemoveField(model_name='property', name=col)
            for col in OLD_COLUMNS
        ],
        # Drop the old PropertyImage table
        migrations.DeleteModel(name='PropertyImage'),
    ]
