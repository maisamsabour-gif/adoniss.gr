"""Historically added extra fields to FaNewSection / FaNewSectionItem.

NOTE (migration realigned during SQLite -> PostgreSQL migration):
The fields this migration originally added are now either:
  * already created by 0092_fanew_section_management_fields
    (description, item.subtitle, item.image_alt), or
  * no longer present on the current models
    (section: image_alt, mobile_image, show_on_homepage, updated_at;
     item:    card_size, show_on_homepage, icon, updated_at).

On SQLite these columns existed but were orphaned (the models stopped
declaring them without a corresponding RemoveField migration). Recreating
them caused duplicate-column / NOT NULL failures on PostgreSQL, which
strictly enforces the schema. To keep the schema identical to the live
models with zero drift, this migration is now a no-op. The accompanying
data already reflects the original badge -> card_size transformation, so
no data is lost.
"""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0103_seed_fa_projects_section'),
    ]

    operations = []
