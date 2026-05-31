from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0066_about_exterior_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpost',
            name='excerpt',
            field=models.TextField(
                max_length=2000,
                verbose_name='Excerpt / Summary',
                help_text='Short summary shown in blog list. Supports bold, italic, links.',
            ),
        ),
    ]
