"""
Add media fields (side_image, section_video, layout_style) to all section models.
This enables the Page Builder to show images/videos alongside text in each section.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('persian_cms', '0013_remove_fapropertygalleryimage_property_and_more'),
    ]

    operations = [
        # ══════════════════════════════════════════════════════════════════════
        # GVBenefitsSection - Add media fields
        # ══════════════════════════════════════════════════════════════════════
        migrations.AddField(
            model_name='gvbenefitssection',
            name='side_image',
            field=models.ImageField(blank=True, upload_to='gv_landing/benefits/', verbose_name='تصویر کناری'),
        ),
        migrations.AddField(
            model_name='gvbenefitssection',
            name='side_image_alt',
            field=models.CharField(blank=True, max_length=200, verbose_name='Alt تصویر کناری'),
        ),
        migrations.AddField(
            model_name='gvbenefitssection',
            name='section_video',
            field=models.FileField(blank=True, upload_to='gv_landing/benefits/videos/', verbose_name='ویدیو بخش'),
        ),
        migrations.AddField(
            model_name='gvbenefitssection',
            name='video_poster',
            field=models.ImageField(blank=True, upload_to='gv_landing/benefits/', verbose_name='پوستر ویدیو'),
        ),
        migrations.AddField(
            model_name='gvbenefitssection',
            name='layout_style',
            field=models.CharField(choices=[('full', 'تمام عرض'), ('text_left', 'متن چپ - تصویر راست'), ('text_right', 'متن راست - تصویر چپ'), ('text_top', 'متن بالا - تصویر پایین'), ('text_bottom', 'متن پایین - تصویر بالا'), ('bg_image', 'تصویر پس‌زمینه'), ('video_bg', 'ویدیو پس‌زمینه')], default='full', max_length=20, verbose_name='نحوه چیدمان'),
        ),

        # ══════════════════════════════════════════════════════════════════════
        # GVEligibilitySection - Add media fields
        # ══════════════════════════════════════════════════════════════════════
        migrations.AddField(
            model_name='gveligibilitysection',
            name='side_image',
            field=models.ImageField(blank=True, upload_to='gv_landing/eligibility/', verbose_name='تصویر کناری'),
        ),
        migrations.AddField(
            model_name='gveligibilitysection',
            name='side_image_alt',
            field=models.CharField(blank=True, max_length=200, verbose_name='Alt تصویر کناری'),
        ),
        migrations.AddField(
            model_name='gveligibilitysection',
            name='section_video',
            field=models.FileField(blank=True, upload_to='gv_landing/eligibility/videos/', verbose_name='ویدیو بخش'),
        ),
        migrations.AddField(
            model_name='gveligibilitysection',
            name='video_poster',
            field=models.ImageField(blank=True, upload_to='gv_landing/eligibility/', verbose_name='پوستر ویدیو'),
        ),
        migrations.AddField(
            model_name='gveligibilitysection',
            name='layout_style',
            field=models.CharField(choices=[('full', 'تمام عرض'), ('text_left', 'متن چپ - تصویر راست'), ('text_right', 'متن راست - تصویر چپ'), ('text_top', 'متن بالا - تصویر پایین'), ('text_bottom', 'متن پایین - تصویر بالا'), ('bg_image', 'تصویر پس‌زمینه'), ('video_bg', 'ویدیو پس‌زمینه')], default='full', max_length=20, verbose_name='نحوه چیدمان'),
        ),

        # ══════════════════════════════════════════════════════════════════════
        # GVProcessSection - Add media fields
        # ══════════════════════════════════════════════════════════════════════
        migrations.AddField(
            model_name='gvprocesssection',
            name='background_image',
            field=models.ImageField(blank=True, upload_to='gv_landing/process/', verbose_name='تصویر پس‌زمینه'),
        ),
        migrations.AddField(
            model_name='gvprocesssection',
            name='side_image',
            field=models.ImageField(blank=True, upload_to='gv_landing/process/', verbose_name='تصویر کناری'),
        ),
        migrations.AddField(
            model_name='gvprocesssection',
            name='side_image_alt',
            field=models.CharField(blank=True, max_length=200, verbose_name='Alt تصویر کناری'),
        ),
        migrations.AddField(
            model_name='gvprocesssection',
            name='section_video',
            field=models.FileField(blank=True, upload_to='gv_landing/process/videos/', verbose_name='ویدیو بخش'),
        ),
        migrations.AddField(
            model_name='gvprocesssection',
            name='video_poster',
            field=models.ImageField(blank=True, upload_to='gv_landing/process/', verbose_name='پوستر ویدیو'),
        ),
        migrations.AddField(
            model_name='gvprocesssection',
            name='layout_style',
            field=models.CharField(choices=[('full', 'تمام عرض'), ('text_left', 'متن چپ - تصویر راست'), ('text_right', 'متن راست - تصویر چپ'), ('text_top', 'متن بالا - تصویر پایین'), ('text_bottom', 'متن پایین - تصویر بالا'), ('bg_image', 'تصویر پس‌زمینه'), ('video_bg', 'ویدیو پس‌زمینه')], default='full', max_length=20, verbose_name='نحوه چیدمان'),
        ),

        # ══════════════════════════════════════════════════════════════════════
        # GVStatisticsSection - Add media fields
        # ══════════════════════════════════════════════════════════════════════
        migrations.AddField(
            model_name='gvstatisticssection',
            name='side_image',
            field=models.ImageField(blank=True, upload_to='gv_landing/stats/', verbose_name='تصویر کناری'),
        ),
        migrations.AddField(
            model_name='gvstatisticssection',
            name='side_image_alt',
            field=models.CharField(blank=True, max_length=200, verbose_name='Alt تصویر کناری'),
        ),
        migrations.AddField(
            model_name='gvstatisticssection',
            name='section_video',
            field=models.FileField(blank=True, upload_to='gv_landing/stats/videos/', verbose_name='ویدیو بخش'),
        ),
        migrations.AddField(
            model_name='gvstatisticssection',
            name='video_poster',
            field=models.ImageField(blank=True, upload_to='gv_landing/stats/', verbose_name='پوستر ویدیو'),
        ),
        migrations.AddField(
            model_name='gvstatisticssection',
            name='layout_style',
            field=models.CharField(choices=[('full', 'تمام عرض'), ('text_left', 'متن چپ - تصویر راست'), ('text_right', 'متن راست - تصویر چپ'), ('text_top', 'متن بالا - تصویر پایین'), ('text_bottom', 'متن پایین - تصویر بالا'), ('bg_image', 'تصویر پس‌زمینه'), ('video_bg', 'ویدیو پس‌زمینه')], default='bg_image', max_length=20, verbose_name='نحوه چیدمان'),
        ),

        # ══════════════════════════════════════════════════════════════════════
        # GVFamilySection - Add media fields
        # ══════════════════════════════════════════════════════════════════════
        migrations.AddField(
            model_name='gvfamilysection',
            name='main_image_alt',
            field=models.CharField(blank=True, max_length=200, verbose_name='Alt تصویر اصلی'),
        ),
        migrations.AddField(
            model_name='gvfamilysection',
            name='section_video',
            field=models.FileField(blank=True, upload_to='gv_landing/family/videos/', verbose_name='ویدیو بخش'),
        ),
        migrations.AddField(
            model_name='gvfamilysection',
            name='video_poster',
            field=models.ImageField(blank=True, upload_to='gv_landing/family/', verbose_name='پوستر ویدیو'),
        ),
        migrations.AddField(
            model_name='gvfamilysection',
            name='layout_style',
            field=models.CharField(choices=[('full', 'تمام عرض'), ('text_left', 'متن چپ - تصویر راست'), ('text_right', 'متن راست - تصویر چپ'), ('text_top', 'متن بالا - تصویر پایین'), ('text_bottom', 'متن پایین - تصویر بالا'), ('bg_image', 'تصویر پس‌زمینه'), ('video_bg', 'ویدیو پس‌زمینه')], default='text_right', max_length=20, verbose_name='نحوه چیدمان'),
        ),

        # ══════════════════════════════════════════════════════════════════════
        # GVDocumentsSection - Add media fields
        # ══════════════════════════════════════════════════════════════════════
        migrations.AddField(
            model_name='gvdocumentssection',
            name='background_image',
            field=models.ImageField(blank=True, upload_to='gv_landing/documents/', verbose_name='تصویر پس‌زمینه'),
        ),
        migrations.AddField(
            model_name='gvdocumentssection',
            name='side_image',
            field=models.ImageField(blank=True, upload_to='gv_landing/documents/', verbose_name='تصویر کناری'),
        ),
        migrations.AddField(
            model_name='gvdocumentssection',
            name='side_image_alt',
            field=models.CharField(blank=True, max_length=200, verbose_name='Alt تصویر کناری'),
        ),
        migrations.AddField(
            model_name='gvdocumentssection',
            name='section_video',
            field=models.FileField(blank=True, upload_to='gv_landing/documents/videos/', verbose_name='ویدیو بخش'),
        ),
        migrations.AddField(
            model_name='gvdocumentssection',
            name='video_poster',
            field=models.ImageField(blank=True, upload_to='gv_landing/documents/', verbose_name='پوستر ویدیو'),
        ),
        migrations.AddField(
            model_name='gvdocumentssection',
            name='layout_style',
            field=models.CharField(choices=[('full', 'تمام عرض'), ('text_left', 'متن چپ - تصویر راست'), ('text_right', 'متن راست - تصویر چپ'), ('text_top', 'متن بالا - تصویر پایین'), ('text_bottom', 'متن پایین - تصویر بالا'), ('bg_image', 'تصویر پس‌زمینه'), ('video_bg', 'ویدیو پس‌زمینه')], default='full', max_length=20, verbose_name='نحوه چیدمان'),
        ),

        # ══════════════════════════════════════════════════════════════════════
        # GVCostSection - Add media fields
        # ══════════════════════════════════════════════════════════════════════
        migrations.AddField(
            model_name='gvcostsection',
            name='background_image',
            field=models.ImageField(blank=True, upload_to='gv_landing/costs/', verbose_name='تصویر پس‌زمینه'),
        ),
        migrations.AddField(
            model_name='gvcostsection',
            name='side_image',
            field=models.ImageField(blank=True, upload_to='gv_landing/costs/', verbose_name='تصویر کناری'),
        ),
        migrations.AddField(
            model_name='gvcostsection',
            name='side_image_alt',
            field=models.CharField(blank=True, max_length=200, verbose_name='Alt تصویر کناری'),
        ),
        migrations.AddField(
            model_name='gvcostsection',
            name='section_video',
            field=models.FileField(blank=True, upload_to='gv_landing/costs/videos/', verbose_name='ویدیو بخش'),
        ),
        migrations.AddField(
            model_name='gvcostsection',
            name='video_poster',
            field=models.ImageField(blank=True, upload_to='gv_landing/costs/', verbose_name='پوستر ویدیو'),
        ),
        migrations.AddField(
            model_name='gvcostsection',
            name='layout_style',
            field=models.CharField(choices=[('full', 'تمام عرض'), ('text_left', 'متن چپ - تصویر راست'), ('text_right', 'متن راست - تصویر چپ'), ('text_top', 'متن بالا - تصویر پایین'), ('text_bottom', 'متن پایین - تصویر بالا'), ('bg_image', 'تصویر پس‌زمینه'), ('video_bg', 'ویدیو پس‌زمینه')], default='full', max_length=20, verbose_name='نحوه چیدمان'),
        ),

        # ══════════════════════════════════════════════════════════════════════
        # GVTestimonialsSection - Add media fields
        # ══════════════════════════════════════════════════════════════════════
        migrations.AddField(
            model_name='gvtestimonialssection',
            name='background_image',
            field=models.ImageField(blank=True, upload_to='gv_landing/testimonials/', verbose_name='تصویر پس‌زمینه'),
        ),
        migrations.AddField(
            model_name='gvtestimonialssection',
            name='side_image',
            field=models.ImageField(blank=True, upload_to='gv_landing/testimonials/', verbose_name='تصویر کناری'),
        ),
        migrations.AddField(
            model_name='gvtestimonialssection',
            name='side_image_alt',
            field=models.CharField(blank=True, max_length=200, verbose_name='Alt تصویر کناری'),
        ),
        migrations.AddField(
            model_name='gvtestimonialssection',
            name='section_video',
            field=models.FileField(blank=True, upload_to='gv_landing/testimonials/videos/', verbose_name='ویدیو بخش'),
        ),
        migrations.AddField(
            model_name='gvtestimonialssection',
            name='video_poster',
            field=models.ImageField(blank=True, upload_to='gv_landing/testimonials/', verbose_name='پوستر ویدیو'),
        ),
        migrations.AddField(
            model_name='gvtestimonialssection',
            name='layout_style',
            field=models.CharField(choices=[('full', 'تمام عرض'), ('text_left', 'متن چپ - تصویر راست'), ('text_right', 'متن راست - تصویر چپ'), ('text_top', 'متن بالا - تصویر پایین'), ('text_bottom', 'متن پایین - تصویر بالا'), ('bg_image', 'تصویر پس‌زمینه'), ('video_bg', 'ویدیو پس‌زمینه')], default='full', max_length=20, verbose_name='نحوه چیدمان'),
        ),

        # ══════════════════════════════════════════════════════════════════════
        # GVFAQSection - Add media fields
        # ══════════════════════════════════════════════════════════════════════
        migrations.AddField(
            model_name='gvfaqsection',
            name='background_image',
            field=models.ImageField(blank=True, upload_to='gv_landing/faq/', verbose_name='تصویر پس‌زمینه'),
        ),
        migrations.AddField(
            model_name='gvfaqsection',
            name='side_image',
            field=models.ImageField(blank=True, upload_to='gv_landing/faq/', verbose_name='تصویر کناری'),
        ),
        migrations.AddField(
            model_name='gvfaqsection',
            name='side_image_alt',
            field=models.CharField(blank=True, max_length=200, verbose_name='Alt تصویر کناری'),
        ),
        migrations.AddField(
            model_name='gvfaqsection',
            name='section_video',
            field=models.FileField(blank=True, upload_to='gv_landing/faq/videos/', verbose_name='ویدیو بخش'),
        ),
        migrations.AddField(
            model_name='gvfaqsection',
            name='video_poster',
            field=models.ImageField(blank=True, upload_to='gv_landing/faq/', verbose_name='پوستر ویدیو'),
        ),
        migrations.AddField(
            model_name='gvfaqsection',
            name='layout_style',
            field=models.CharField(choices=[('full', 'تمام عرض'), ('text_left', 'متن چپ - تصویر راست'), ('text_right', 'متن راست - تصویر چپ'), ('text_top', 'متن بالا - تصویر پایین'), ('text_bottom', 'متن پایین - تصویر بالا'), ('bg_image', 'تصویر پس‌زمینه'), ('video_bg', 'ویدیو پس‌زمینه')], default='full', max_length=20, verbose_name='نحوه چیدمان'),
        ),
    ]
