import logging
import re


class PiiRedactionFilter(logging.Filter):
    EMAIL_PATTERN = re.compile(r"([a-zA-Z0-9_.+-]+)@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)")
    PHONE_PATTERN = re.compile(r"(\+?\d[\d\-\s\(\)]{6,}\d)")

    def filter(self, record):
        message = record.getMessage()
        message = self.EMAIL_PATTERN.sub("[redacted-email]", message)
        message = self.PHONE_PATTERN.sub("[redacted-phone]", message)
        record.msg = message
        record.args = ()
        return True
