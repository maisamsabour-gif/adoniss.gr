from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0067_blogpost_excerpt_maxlength'),
    ]

    operations = [
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='intro_bullet_1',
            field=models.CharField(
                blank=True, default='اقامت دائم بدون شرط حضور',
                max_length=200, verbose_name='بولت اول',
                help_text='گزینه اول برجسته زیر متن.',
            ),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='intro_bullet_2',
            field=models.CharField(
                blank=True, default='شامل کل خانواده (همسر و فرزندان)',
                max_length=200, verbose_name='بولت دوم',
                help_text='گزینه دوم برجسته.',
            ),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='intro_bullet_3',
            field=models.CharField(
                blank=True, default='امکان سرمایه‌گذاری و درآمد اجاره‌ای',
                max_length=200, verbose_name='بولت سوم',
                help_text='گزینه سوم برجسته.',
            ),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='intro_feature_1_icon',
            field=models.CharField(
                blank=True, default='🏡', max_length=10,
                verbose_name='آیکون ویژگی اول',
                help_text='یک ایموجی. مثال: 🏡 🌍 ⚖️',
            ),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='intro_feature_1_text',
            field=models.CharField(
                blank=True, default='ملک در قلب اروپا',
                max_length=120, verbose_name='متن ویژگی اول',
            ),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='intro_feature_2_icon',
            field=models.CharField(
                blank=True, default='🌍', max_length=10,
                verbose_name='آیکون ویژگی دوم',
                help_text='یک ایموجی. مثال: 🌍 🛂 💼',
            ),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='intro_feature_2_text',
            field=models.CharField(
                blank=True, default='سفر بدون ویزا به ۲۶ کشور شنگن',
                max_length=120, verbose_name='متن ویژگی دوم',
            ),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='intro_feature_3_icon',
            field=models.CharField(
                blank=True, default='⚖️', max_length=10,
                verbose_name='آیکون ویژگی سوم',
                help_text='یک ایموجی. مثال: ⚖️ 🤝 📋',
            ),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='intro_feature_3_text',
            field=models.CharField(
                blank=True, default='پشتیبانی حقوقی کامل',
                max_length=120, verbose_name='متن ویژگی سوم',
            ),
        ),
    ]
