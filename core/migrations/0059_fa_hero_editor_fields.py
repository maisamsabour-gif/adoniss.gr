from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('core', '0058_invert_fa_hero_image_darkness_scale')]

    operations = [
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='hero_content_vertical_align',
            field=models.CharField(default='bottom', max_length=12),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='hero_content_horizontal_align',
            field=models.CharField(default='right', max_length=12),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='hero_title_color',
            field=models.CharField(default='#FFFFFF', max_length=7),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='hero_subtitle_color',
            field=models.CharField(default='#F3F6FB', max_length=7),
        ),
    ]
