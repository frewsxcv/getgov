"""Test our email templates and sending."""

from unittest.mock import MagicMock

from django.contrib.auth import get_user_model
from django.test import TestCase

from registrar.models import Contact, DraftDomain, Website, DomainApplication

import boto3_mocking  # type: ignore


class TestEmails(TestCase):
    def _completed_application(
        self,
        has_other_contacts=True,
        has_current_website=True,
        has_alternative_gov_domain=True,
        has_type_of_work=True,
        has_anything_else=True,
    ):
        """A completed domain application."""
        user = get_user_model().objects.create(username="username")
        ao, _ = Contact.objects.get_or_create(
            first_name="Testy",
            last_name="Tester",
            title="Chief Tester",
            email="testy@town.com",
            phone="(555) 555 5555",
        )
        domain, _ = DraftDomain.objects.get_or_create(name="city.gov")
        alt, _ = Website.objects.get_or_create(website="city1.gov")
        current, _ = Website.objects.get_or_create(website="city.com")
        you, _ = Contact.objects.get_or_create(
            first_name="Testy you",
            last_name="Tester you",
            title="Admin Tester",
            email="testy-admin@town.com",
            phone="(555) 555 5556",
        )
        other, _ = Contact.objects.get_or_create(
            first_name="Testy2",
            last_name="Tester2",
            title="Another Tester",
            email="testy2@town.com",
            phone="(555) 555 5557",
        )
        domain_application_kwargs = dict(
            organization_type="federal",
            federal_type="executive",
            purpose="Purpose of the site",
            is_policy_acknowledged=True,
            organization_name="Testorg",
            address_line1="address 1",
            address_line2="address 2",
            state_territory="NY",
            zipcode="10002",
            authorizing_official=ao,
            requested_domain=domain,
            submitter=you,
            creator=user,
        )
        if has_type_of_work:
            domain_application_kwargs["type_of_work"] = "e-Government"
        if has_anything_else:
            domain_application_kwargs["anything_else"] = "There is more"

        application, _ = DomainApplication.objects.get_or_create(
            **domain_application_kwargs
        )

        if has_other_contacts:
            application.other_contacts.add(other)
        if has_current_website:
            application.current_websites.add(current)
        if has_alternative_gov_domain:
            application.alternative_domains.add(alt)

        return application

    def setUp(self):
        self.mock_client_class = MagicMock()
        self.mock_client = self.mock_client_class.return_value

    @boto3_mocking.patching
    def test_submission_confirmation(self):
        """Submission confirmation email works."""
        application = self._completed_application()

        with boto3_mocking.clients.handler_for("sesv2", self.mock_client_class):
            application.submit()

        # check that an email was sent
        self.assertTrue(self.mock_client.send_email.called)

        # check the call sequence for the email
        args, kwargs = self.mock_client.send_email.call_args
        self.assertIn("Content", kwargs)
        self.assertIn("Simple", kwargs["Content"])
        self.assertIn("Subject", kwargs["Content"]["Simple"])
        self.assertIn("Body", kwargs["Content"]["Simple"])

        # check for things in the email content (not an exhaustive list)
        body = kwargs["Content"]["Simple"]["Body"]["Text"]["Data"]

        self.assertIn("Type of organization:", body)
        self.assertIn("Federal", body)
        self.assertIn("Authorizing official:", body)
        self.assertIn("Testy Tester", body)
        self.assertIn(".gov domain:", body)
        self.assertIn("city.gov", body)
        self.assertIn("city1.gov", body)

        # check for optional things
        self.assertIn("Other employees from your organization:", body)
        self.assertIn("Testy2 Tester2", body)
        self.assertIn("Current website for your organization:", body)
        self.assertIn("city.com", body)
        self.assertIn("Type of work:", body)
        self.assertIn("Anything else", body)

    @boto3_mocking.patching
    def test_submission_confirmation_no_current_website_spacing(self):
        """Test line spacing without current_website."""
        application = self._completed_application(has_current_website=False)
        with boto3_mocking.clients.handler_for("sesv2", self.mock_client_class):
            application.submit()
        _, kwargs = self.mock_client.send_email.call_args
        body = kwargs["Content"]["Simple"]["Body"]["Text"]["Data"]
        self.assertNotIn("Current website for your organization:", body)
        # spacing should be right between adjacent elements
        self.assertRegex(body, r"5555\n\n.gov domain:")

    @boto3_mocking.patching
    def test_submission_confirmation_current_website_spacing(self):
        """Test line spacing with current_website."""
        application = self._completed_application(has_current_website=True)
        with boto3_mocking.clients.handler_for("sesv2", self.mock_client_class):
            application.submit()
        _, kwargs = self.mock_client.send_email.call_args
        body = kwargs["Content"]["Simple"]["Body"]["Text"]["Data"]
        self.assertIn("Current website for your organization:", body)
        # spacing should be right between adjacent elements
        self.assertRegex(body, r"5555\n\nCurrent website for")
        self.assertRegex(body, r"city.com\n\n.gov domain:")

    @boto3_mocking.patching
    def test_submission_confirmation_other_contacts_spacing(self):
        """Test line spacing with other contacts."""
        application = self._completed_application(has_other_contacts=True)
        with boto3_mocking.clients.handler_for("sesv2", self.mock_client_class):
            application.submit()
        _, kwargs = self.mock_client.send_email.call_args
        body = kwargs["Content"]["Simple"]["Body"]["Text"]["Data"]
        self.assertIn("Other employees from your organization:", body)
        # spacing should be right between adjacent elements
        self.assertRegex(body, r"5556\n\nOther employees")
        self.assertRegex(body, r"5557\n\nAnything else")

    @boto3_mocking.patching
    def test_submission_confirmation_no_other_contacts_spacing(self):
        """Test line spacing without other contacts."""
        application = self._completed_application(has_other_contacts=False)
        with boto3_mocking.clients.handler_for("sesv2", self.mock_client_class):
            application.submit()
        _, kwargs = self.mock_client.send_email.call_args
        body = kwargs["Content"]["Simple"]["Body"]["Text"]["Data"]
        self.assertNotIn("Other employees from your organization:", body)
        # spacing should be right between adjacent elements
        self.assertRegex(body, r"5556\n\nAnything else")

    @boto3_mocking.patching
    def test_submission_confirmation_alternative_govdomain_spacing(self):
        """Test line spacing with alternative .gov domain."""
        application = self._completed_application(has_alternative_gov_domain=True)
        with boto3_mocking.clients.handler_for("sesv2", self.mock_client_class):
            application.submit()
        _, kwargs = self.mock_client.send_email.call_args
        body = kwargs["Content"]["Simple"]["Body"]["Text"]["Data"]
        self.assertIn("city1.gov", body)
        # spacing should be right between adjacent elements
        self.assertRegex(body, r"city.gov\ncity1.gov\n\nPurpose of your domain:")

    @boto3_mocking.patching
    def test_submission_confirmation_no_alternative_govdomain_spacing(self):
        """Test line spacing without alternative .gov domain."""
        application = self._completed_application(has_alternative_gov_domain=False)
        with boto3_mocking.clients.handler_for("sesv2", self.mock_client_class):
            application.submit()
        _, kwargs = self.mock_client.send_email.call_args
        body = kwargs["Content"]["Simple"]["Body"]["Text"]["Data"]
        self.assertNotIn("city1.gov", body)
        # spacing should be right between adjacent elements
        self.assertRegex(body, r"city.gov\n\nPurpose of your domain:")

    @boto3_mocking.patching
    def test_submission_confirmation_type_of_work_spacing(self):
        """Test line spacing with type of work."""
        application = self._completed_application(has_type_of_work=True)
        with boto3_mocking.clients.handler_for("sesv2", self.mock_client_class):
            application.submit()
        _, kwargs = self.mock_client.send_email.call_args
        body = kwargs["Content"]["Simple"]["Body"]["Text"]["Data"]
        self.assertIn("Type of work:", body)
        # spacing should be right between adjacent elements
        self.assertRegex(body, r"10002\n\nType of work:")

    @boto3_mocking.patching
    def test_submission_confirmation_no_type_of_work_spacing(self):
        """Test line spacing without type of work."""
        application = self._completed_application(has_type_of_work=False)
        with boto3_mocking.clients.handler_for("sesv2", self.mock_client_class):
            application.submit()
        _, kwargs = self.mock_client.send_email.call_args
        body = kwargs["Content"]["Simple"]["Body"]["Text"]["Data"]
        self.assertNotIn("Type of work:", body)
        # spacing should be right between adjacent elements
        self.assertRegex(body, r"10002\n\nAuthorizing official:")

    @boto3_mocking.patching
    def test_submission_confirmation_anything_else_spacing(self):
        """Test line spacing with anything else."""
        application = self._completed_application(has_anything_else=True)
        with boto3_mocking.clients.handler_for("sesv2", self.mock_client_class):
            application.submit()
        _, kwargs = self.mock_client.send_email.call_args
        body = kwargs["Content"]["Simple"]["Body"]["Text"]["Data"]
        # spacing should be right between adjacent elements
        self.assertRegex(body, r"5557\n\nAnything else we should know?")

    @boto3_mocking.patching
    def test_submission_confirmation_no_anything_else_spacing(self):
        """Test line spacing without anything else."""
        application = self._completed_application(has_anything_else=False)
        with boto3_mocking.clients.handler_for("sesv2", self.mock_client_class):
            application.submit()
        _, kwargs = self.mock_client.send_email.call_args
        body = kwargs["Content"]["Simple"]["Body"]["Text"]["Data"]
        self.assertNotIn("Anything else we should know", body)
        # spacing should be right between adjacent elements
        self.assertRegex(body, r"5557\n\n----")
