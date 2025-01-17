"""People are invited by email to administer domains."""

import logging

from django.contrib.auth import get_user_model
from django.db import models

from django_fsm import FSMField, transition  # type: ignore

from .utility.time_stamped_model import TimeStampedModel
from .user_domain_role import UserDomainRole


logger = logging.getLogger(__name__)


class DomainInvitation(TimeStampedModel):
    INVITED = "invited"
    RETRIEVED = "retrieved"

    email = models.EmailField(
        null=False,
        blank=False,
    )

    domain = models.ForeignKey(
        "registrar.Domain",
        on_delete=models.CASCADE,  # delete domain, then get rid of invitations
        null=False,
        related_name="invitations",
    )

    status = FSMField(
        choices=[
            (INVITED, INVITED),
            (RETRIEVED, RETRIEVED),
        ],
        default=INVITED,
        protected=True,  # can't alter state except through transition methods!
    )

    def __str__(self):
        return f"Invitation for {self.email} on {self.domain} is {self.status}"

    @transition(field="status", source=INVITED, target=RETRIEVED)
    def retrieve(self):
        """When an invitation is retrieved, create the corresponding permission.

        Raises:
            RuntimeError if no matching user can be found.
        """

        # get a user with this email address
        User = get_user_model()
        try:
            user = User.objects.get(email=self.email)
        except User.DoesNotExist:
            # should not happen because a matching user should exist before
            # we retrieve this invitation
            raise RuntimeError(
                "Cannot find the user to retrieve this domain invitation."
            )

        # and create a role for that user on this domain
        _, created = UserDomainRole.objects.get_or_create(
            user=user, domain=self.domain, role=UserDomainRole.Roles.ADMIN
        )
        if not created:
            # something strange happened and this role already existed when
            # the invitation was retrieved. Log that this occurred.
            logger.warn(
                "Invitation %s was retrieved for a role that already exists.", self
            )
