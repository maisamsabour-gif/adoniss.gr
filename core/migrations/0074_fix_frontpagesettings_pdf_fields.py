from django.db import migrations


class Migration(migrations.Migration):
    """
    Stub migration: FrontPageSettings.catalogue_pdf_1/2 renamed to
    catalogue_btn1_pdf / catalogue_btn2_pdf to match the actual DB column
    names (catalogue_btn1_pdf, catalogue_btn2_pdf already exist in the DB).
    No ALTER TABLE needed.
    """

    dependencies = [
        ('core', '0073_about_hero_image_video'),
    ]

    operations = []
