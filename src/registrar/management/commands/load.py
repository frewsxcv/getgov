import logging

from django.core.management.base import BaseCommand
from auditlog.context import disable_auditlog  # type: ignore

from registrar.fixtures import UserFixture, DomainApplicationFixture, DomainFixture

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        # django-auditlog has some bugs with fixtures
        # https://github.com/jazzband/django-auditlog/issues/17
        with disable_auditlog():
            UserFixture.load()
            DomainApplicationFixture.load()
            DomainFixture.load()
            logger.info("All fixtures loaded.")
