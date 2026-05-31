from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0065_wa_number_max_length'),
    ]

    operations = [
        migrations.AddField(
            model_name='aboutpagesettings',
            name='about_exterior_image',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to='about/',
                verbose_name='Company Exterior Image',
                help_text='Photo of the company building exterior, shown next to the "Who We Are" text.',
            ),
        ),
    ]
