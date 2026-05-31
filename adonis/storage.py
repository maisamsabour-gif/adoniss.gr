from urllib.parse import urljoin

from django.conf import settings
from whitenoise.storage import CompressedManifestStaticFilesStorage


class GracefulCompressedManifestStaticFilesStorage(CompressedManifestStaticFilesStorage):
    """WhiteNoise manifest storage that never 500s a page over a missing asset.

    If a referenced static file is absent from both the manifest and disk
    (e.g. an image that was not shipped with the project), ``url()`` falls back
    to the plain, unhashed STATIC_URL path. The asset simply renders as a broken
    image instead of taking the whole page down with an HTTP 500.
    """

    manifest_strict = False

    def url(self, name, force=False):
        try:
            return super().url(name, force=force)
        except ValueError:
            return urljoin(settings.STATIC_URL, name)
