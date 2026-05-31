"""
Management command: backfill_translated_slugs

After installing django-modeltranslation the migration creates _en / _tr
columns but does NOT copy existing data into them (the original column values
remain in the un-suffixed column, e.g. `slug`, `title`, `name`).

This command copies every translated field's original value into the _en
column, then copies _en → _tr for all slug fields (so Turkish URLs work
before individual translations have been entered).

Run once after the first `migrate` following modeltranslation installation.
"""

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Backfill _en fields from original columns for all modeltranslation models'

    # Table → list of (original_col, en_col, tr_col_or_None)
    # For non-slug fields tr_col is None → only copy to _en
    FIELD_MAP = {
        'core_blogpost': [
            ('title',            'title_en',            None),
            ('slug',             'slug_en',             'slug_tr'),
            ('excerpt',          'excerpt_en',          None),
            ('content',          'content_en',          None),
            ('meta_title',       'meta_title_en',       None),
            ('meta_description', 'meta_description_en', None),
            ('og_title',         'og_title_en',         None),
            ('og_description',   'og_description_en',   None),
        ],
        'core_event': [
            ('title',             'title_en',             None),
            ('slug',              'slug_en',              'slug_tr'),
            ('short_description', 'short_description_en', None),
            ('full_description',  'full_description_en',  None),
        ],
        'core_blogcategory': [
            ('name',        'name_en',        None),
            ('description', 'description_en', None),
        ],
        'core_service': [
            ('title',       'title_en',       None),
            ('description', 'description_en', None),
        ],
        'core_faq': [
            ('question', 'question_en', None),
            ('answer',   'answer_en',   None),
        ],
        'core_goldenvisacard': [
            ('title',       'title_en',       None),
            ('subtitle',    'subtitle_en',    None),
            ('description', 'description_en', None),
        ],
        'core_testimonial': [
            ('content', 'content_en', None),
        ],
        'core_footersettings': [
            ('description',          'description_en',          None),
            ('whatsapp_button_text', 'whatsapp_button_text_en', None),
        ],
        'core_headersettings': [
            ('hero_title',           'hero_title_en',           None),
            ('hero_subtitle',        'hero_subtitle_en',        None),
            ('intro_title',          'intro_title_en',          None),
            ('intro_text',           'intro_text_en',           None),
            ('contact_button_text',  'contact_button_text_en',  None),
        ],
        'core_frontpagesettings': [
            ('services_badge',       'services_badge_en',       None),
            ('services_title',       'services_title_en',       None),
            ('services_description', 'services_description_en', None),
            ('process_badge',        'process_badge_en',        None),
            ('process_title',        'process_title_en',        None),
            ('process_description',  'process_description_en',  None),
            ('catalogue_badge_text', 'catalogue_badge_text_en', None),
            ('catalogue_heading',    'catalogue_heading_en',    None),
            ('catalogue_subtext',    'catalogue_subtext_en',    None),
            ('catalogue_btn1_title', 'catalogue_btn1_title_en', None),
            ('catalogue_btn1_label', 'catalogue_btn1_label_en', None),
            ('catalogue_btn2_title', 'catalogue_btn2_title_en', None),
            ('catalogue_btn2_label', 'catalogue_btn2_label_en', None),
            ('contact_badge',        'contact_badge_en',        None),
            ('contact_title',        'contact_title_en',        None),
            ('contact_description',  'contact_description_en',  None),
        ],
        'core_partnershippagesettings': [
            ('hero_title',        'hero_title_en',        None),
            ('hero_subtitle',     'hero_subtitle_en',     None),
            ('video_title',       'video_title_en',       None),
            ('video_subtitle',    'video_subtitle_en',    None),
            ('b2b_title',         'b2b_title_en',         None),
            ('b2b_text',          'b2b_text_en',          None),
            ('benefit_1_title',   'benefit_1_title_en',   None),
            ('benefit_1_text',    'benefit_1_text_en',    None),
            ('benefit_2_title',   'benefit_2_title_en',   None),
            ('benefit_2_text',    'benefit_2_text_en',    None),
            ('benefit_3_title',   'benefit_3_title_en',   None),
            ('benefit_3_text',    'benefit_3_text_en',    None),
            ('benefit_4_title',   'benefit_4_title_en',   None),
            ('benefit_4_text',    'benefit_4_text_en',    None),
            ('benefit_5_title',   'benefit_5_title_en',   None),
            ('benefit_5_text',    'benefit_5_text_en',    None),
            ('benefit_6_title',   'benefit_6_title_en',   None),
            ('benefit_6_text',    'benefit_6_text_en',    None),
            ('cta_title',         'cta_title_en',         None),
            ('cta_text',          'cta_text_en',          None),
            ('cta_button_text',   'cta_button_text_en',   None),
        ],
        'properties_property': [
            ('name',                     'name_en',                     None),
            ('slug',                     'slug_en',                     'slug_tr'),
            ('tagline',                  'tagline_en',                  None),
            ('description',              'description_en',              None),
            ('location',                 'location_en',                 None),
            ('neighborhood_description', 'neighborhood_description_en', None),
            ('feature_1',                'feature_1_en',                None),
            ('feature_2',                'feature_2_en',                None),
            ('feature_3',                'feature_3_en',                None),
            ('feature_4',                'feature_4_en',                None),
            ('area_highlight_1',         'area_highlight_1_en',         None),
            ('area_highlight_2',         'area_highlight_2_en',         None),
            ('area_highlight_3',         'area_highlight_3_en',         None),
            ('area_highlight_4',         'area_highlight_4_en',         None),
            ('area_highlight_5',         'area_highlight_5_en',         None),
            ('area_highlight_6',         'area_highlight_6_en',         None),
        ],
    }

    def _column_exists(self, cursor, table, col):
        cursor.execute(f'PRAGMA table_info("{table}")')
        return any(row[1] == col for row in cursor.fetchall())

    def handle(self, *args, **options):
        cursor = connection.cursor()
        total_updated = 0

        for table, fields in self.FIELD_MAP.items():
            self.stdout.write(f'\n{table}:')
            for orig, en_col, tr_col in fields:
                # Skip if the _en column doesn't exist (migration not run yet)
                if not self._column_exists(cursor, table, en_col):
                    self.stdout.write(f'  SKIP {en_col} — column not found')
                    continue

                # Copy original → _en where _en is NULL or empty
                cursor.execute(f"""
                    UPDATE "{table}"
                    SET "{en_col}" = "{orig}"
                    WHERE ("{en_col}" IS NULL OR "{en_col}" = '')
                      AND "{orig}" IS NOT NULL
                      AND "{orig}" != ''
                """)
                n = cursor.rowcount
                total_updated += n
                self.stdout.write(
                    self.style.SUCCESS(f'  {orig} → {en_col}: {n} row(s) updated')
                )

                # For slug fields also copy _en → _tr where _tr is NULL/empty
                if tr_col and self._column_exists(cursor, table, tr_col):
                    cursor.execute(f"""
                        UPDATE "{table}"
                        SET "{tr_col}" = "{en_col}"
                        WHERE ("{tr_col}" IS NULL OR "{tr_col}" = '')
                          AND "{en_col}" IS NOT NULL
                          AND "{en_col}" != ''
                    """)
                    n2 = cursor.rowcount
                    total_updated += n2
                    self.stdout.write(
                        self.style.SUCCESS(f'  {en_col} → {tr_col}: {n2} row(s) updated')
                    )

        connection.commit()
        self.stdout.write(
            self.style.SUCCESS(f'\nDone. Total rows updated across all fields: {total_updated}')
        )
