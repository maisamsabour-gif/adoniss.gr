# Generated manually for adding hero position and font size settings

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0113_add_subtitle_alignment'),
    ]

    operations = [
        migrations.AddField(
            model_name='fanewsettings',
            name='hero_content_vertical_position',
            field=models.CharField(
                blank=True,
                choices=[('top', 'بالا'), ('center', 'وسط'), ('bottom', 'پایین')],
                default='center',
                help_text='تعیین می\u200cکند عنوان و زیرعنوان در کجای صفحه هیرو قرار بگیرند.',
                max_length=12,
                verbose_name='جایگاه عمودی محتوای هیرو',
            ),
        ),
        migrations.AddField(
            model_name='fanewsettings',
            name='hero_title_font_size',
            field=models.CharField(
                blank=True,
                default='48px',
                help_text='مثال: 48px, 56px, 64px — مقدار پیش\u200cفرض: 48px',
                max_length=10,
                verbose_name='اندازه فونت عنوان هیرو',
            ),
        ),
        migrations.AddField(
            model_name='fanewsettings',
            name='hero_subtitle_font_size',
            field=models.CharField(
                blank=True,
                default='18px',
                help_text='مثال: 16px, 18px, 20px — مقدار پیش\u200cفرض: 18px',
                max_length=10,
                verbose_name='اندازه فونت زیرعنوان هیرو',
            ),
        ),
    ]
