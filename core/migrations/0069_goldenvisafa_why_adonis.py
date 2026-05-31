from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0068_goldenvisafa_intro_bullets_features'),
    ]

    operations = [
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='why_adonis_title',
            field=models.CharField(blank=True, default='چرا آدونیس؟', max_length=200,
                                   verbose_name='عنوان سکشن چرا آدونیس'),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='why_adonis_subtitle',
            field=models.CharField(
                blank=True,
                default='با بیش از یک دهه تجربه در بازار ملک یونان، آدونیس تنها انتخاب مطمئن شماست.',
                max_length=300, verbose_name='زیرعنوان سکشن چرا آدونیس'),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='why_item_1_icon',
            field=models.CharField(blank=True, default='🏆', max_length=10,
                                   verbose_name='آیکون دلیل اول'),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='why_item_1_title',
            field=models.CharField(blank=True, default='تجربه ۱۰+ ساله', max_length=120,
                                   verbose_name='عنوان دلیل اول'),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='why_item_1_text',
            field=models.TextField(
                blank=True,
                default='سابقه درخشان در انجام صدها پرونده موفق گلدن ویزا برای متقاضیان از سراسر جهان.',
                verbose_name='توضیح دلیل اول'),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='why_item_2_icon',
            field=models.CharField(blank=True, default='🤝', max_length=10,
                                   verbose_name='آیکون دلیل دوم'),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='why_item_2_title',
            field=models.CharField(blank=True, default='خدمات کامل زیر یک سقف', max_length=120,
                                   verbose_name='عنوان دلیل دوم'),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='why_item_2_text',
            field=models.TextField(
                blank=True,
                default='از انتخاب ملک تا اخذ کارت اقامت — تیم حقوقی، مالی و فنی آدونیس همه مراحل را مدیریت می‌کند.',
                verbose_name='توضیح دلیل دوم'),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='why_item_3_icon',
            field=models.CharField(blank=True, default='🛡️', max_length=10,
                                   verbose_name='آیکون دلیل سوم'),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='why_item_3_title',
            field=models.CharField(blank=True, default='امنیت سرمایه‌گذاری', max_length=120,
                                   verbose_name='عنوان دلیل سوم'),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='why_item_3_text',
            field=models.TextField(
                blank=True,
                default='پروژه‌های آدونیس با ضمانت بازپرداخت، تأییدیه حقوقی و اسناد رسمی ثبت‌شده ارائه می‌شوند.',
                verbose_name='توضیح دلیل سوم'),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='why_item_4_icon',
            field=models.CharField(blank=True, default='🌍', max_length=10,
                                   verbose_name='آیکون دلیل چهارم'),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='why_item_4_title',
            field=models.CharField(blank=True, default='پشتیبانی فارسی‌زبان', max_length=120,
                                   verbose_name='عنوان دلیل چهارم'),
        ),
        migrations.AddField(
            model_name='goldenvisafalandingpage',
            name='why_item_4_text',
            field=models.TextField(
                blank=True,
                default='تیم متخصص فارسی‌زبان آدونیس از اولین تماس تا دریافت کارت اقامت کنار شماست.',
                verbose_name='توضیح دلیل چهارم'),
        ),
    ]
