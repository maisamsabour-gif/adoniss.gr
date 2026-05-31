"""
Management command: python manage.py convert_brochure [slug|--all] [--force]

Examples:
    python manage.py convert_brochure my-brochure-slug
    python manage.py convert_brochure --all
    python manage.py convert_brochure --all --force
"""
from django.core.management.base import BaseCommand, CommandError

from brochures.conversion import run_conversion
from brochures.models import Brochure


class Command(BaseCommand):
    help = 'Convert brochure PDF(s) to WebP page images'

    def add_arguments(self, parser):
        parser.add_argument(
            'slug', nargs='?', type=str,
            help='Slug of the brochure to convert (omit to use --all)',
        )
        parser.add_argument(
            '--all', action='store_true',
            help='Convert every brochure that has a PDF',
        )
        parser.add_argument(
            '--force', action='store_true',
            help='Re-convert even brochures already marked "ready"',
        )

    def handle(self, *args, **options):
        slug    = options.get('slug')
        do_all  = options.get('all')
        force   = options.get('force')

        if not slug and not do_all:
            raise CommandError('Provide a slug or use --all')

        qs = Brochure.objects.exclude(pdf_file='').exclude(pdf_file__isnull=True)
        if slug:
            qs = qs.filter(slug=slug)
        if not force:
            qs = qs.exclude(conversion_status=Brochure.STATUS_READY)

        if not qs.exists():
            self.stdout.write(self.style.WARNING('No brochures to convert.'))
            return

        for b in qs:
            self.stdout.write(f'Converting: {b.title} ({b.slug})…')
            run_conversion(b.pk)
            b.refresh_from_db()
            if b.conversion_status == Brochure.STATUS_READY:
                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ {b.page_count} pages  ({b.page_width}×{b.page_height}px)')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'  ✗ Failed: {b.conversion_error[:200]}')
                )
