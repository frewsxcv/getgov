import logging

from django.db import models

from .utility.domain_helper import DomainHelper
from .utility.time_stamped_model import TimeStampedModel

logger = logging.getLogger(__name__)


class DraftDomain(TimeStampedModel, DomainHelper):
    """Store domain names which registrants have requested."""

    def __str__(self) -> str:
        return self.name

    name = models.CharField(
        max_length=253,
        blank=False,
        default=None,  # prevent saving without a value
        help_text="Fully qualified domain name",
    )
