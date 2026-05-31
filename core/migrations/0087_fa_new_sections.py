from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0086_fanewsettings_header_logo'),
    ]

    operations = [
        migrations.CreateModel(
            name='FaNewSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('section_type', models.CharField(
                    choices=[
                        ('why_greece', 'چرا یونان؟'),
                        ('why_adonis', 'چرا آدونیس؟'),
                        ('routes', 'مسیرهای گلدن ویزا'),
                        ('projects', 'پروژه‌های منتخب'),
                        ('process', 'فرآیند همکاری'),
                        ('trust', 'اعتماد و تجربه'),
                        ('consult', 'مشاوره رایگان'),
                    ],
                    max_length=20,
                    verbose_name='نوع بخش',
                )),
                ('order', models.PositiveIntegerField(
                    db_index=True, default=0,
                    help_text='عدد کوچک‌تر = بالاتر در صفحه',
                    verbose_name='ترتیب نمایش',
                )),
                ('is_active', models.BooleanField(
                    default=True,
                    help_text='غیرفعال کردن این بخش را از صفحه پنهان می‌کند.',
                    verbose_name='فعال',
                )),
                ('eyebrow', models.CharField(
                    blank=True, max_length=100,
                    help_text='متن کوچک بالای عنوان اصلی (مثال: چرا یونان؟)',
                    verbose_name='متن بالای عنوان',
                )),
                ('title', models.CharField(blank=True, max_length=250, verbose_name='عنوان اصلی')),
                ('subtitle', models.TextField(
                    blank=True,
                    help_text='پاراگراف زیر عنوان اصلی',
                    verbose_name='توضیح کوتاه',
                )),
            ],
            options={
                'verbose_name': 'بخش صفحه فارسی',
                'verbose_name_plural': 'بخش‌های صفحه /fa-new/',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='FaNewSectionItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('section', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='items',
                    to='core.fanewsection',
                    verbose_name='بخش',
                )),
                ('order', models.PositiveIntegerField(default=0, verbose_name='ترتیب')),
                ('title', models.CharField(blank=True, max_length=200, verbose_name='عنوان')),
                ('body', models.TextField(
                    blank=True,
                    help_text=(
                        'برای مسیرهای گلدن ویزا: هر ویژگی را در یک خط بنویسید. '
                        'برای نقل‌قول: متن کامل نقل‌قول را اینجا بنویسید.'
                    ),
                    verbose_name='متن / توضیح',
                )),
                ('badge', models.CharField(
                    blank=True, max_length=50,
                    help_text='ویژگی: ۰۱، ۰۲ … | مسیر: پایه، پریمیوم | فرآیند: ۱، ۲ …',
                    verbose_name='برچسب / شماره',
                )),
                ('amount', models.CharField(
                    blank=True, max_length=100,
                    help_text='فقط برای مسیرهای گلدن ویزا، مثال: از ۲۵۰٬۰۰۰ یورو',
                    verbose_name='مبلغ',
                )),
                ('is_featured', models.BooleanField(
                    default=False,
                    help_text='فقط برای مسیرها — کارت را برجسته (طلایی) می‌کند',
                    verbose_name='پیشنهاد ویژه؟',
                )),
                ('stat_number', models.CharField(
                    blank=True, max_length=20,
                    help_text='فقط برای بخش «چرا آدونیس؟» — مثال: ۱۲+  یا  ۹۸٪',
                    verbose_name='عدد آمار',
                )),
                ('author_name', models.CharField(
                    blank=True, max_length=100,
                    help_text='فقط برای نقل‌قول‌ها',
                    verbose_name='نام گوینده',
                )),
                ('author_meta', models.CharField(
                    blank=True, max_length=200,
                    help_text='مثال: تهران → آتن، ۱۴۰۲',
                    verbose_name='اطلاعات تکمیلی گوینده',
                )),
                ('location', models.CharField(
                    blank=True, max_length=100,
                    help_text='فقط برای پروژه‌ها — مثال: آلیموس · آتن',
                    verbose_name='موقعیت',
                )),
                ('image', models.ImageField(
                    blank=True, null=True,
                    help_text='فقط برای پروژه‌ها',
                    upload_to='fa-new/sections/',
                    verbose_name='تصویر',
                )),
                ('cta_label', models.CharField(blank=True, max_length=100, verbose_name='متن دکمه')),
                ('cta_url', models.CharField(
                    blank=True, max_length=500,
                    help_text='آدرس لینک یا anchor مثل #adonis-fa-new-consult',
                    verbose_name='لینک دکمه',
                )),
            ],
            options={
                'verbose_name': 'آیتم',
                'verbose_name_plural': 'آیتم‌ها',
                'ordering': ['order'],
            },
        ),
    ]
