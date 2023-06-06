import csv
import logging
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.contenttypes.models import ContentType
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.http import HttpResponse
from django.core.mail import send_mail
from .utility.email import send_templated_email, EmailSendingError

logger = logging.getLogger(__name__)

from . import models

def export_report(modeladmin, request, queryset):
    report_data = models.DomainApplication.objects.all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Field 1', 'Field 2'])
    for item in report_data:
        writer.writerow([item.requested_domain.name, item.submitter])

    return response

export_report.short_description = "Export report"

class AuditedAdmin(admin.ModelAdmin):

    """Custom admin to make auditing easier."""
    
    def history_view(self, request, object_id, extra_context=None):
        """On clicking 'History', take admin to the auditlog view for an object."""
        return HttpResponseRedirect(
            "{url}?resource_type={content_type}&object_id={object_id}".format(
                url=reverse("admin:auditlog_logentry_changelist", args=()),
                content_type=ContentType.objects.get_for_model(self.model).pk,
                object_id=object_id,
            )
        )


class UserContactInline(admin.StackedInline):

    """Edit a user's profile on the user page."""

    model = models.Contact


class MyUserAdmin(UserAdmin):

    """Custom user admin class to use our inlines."""

    inlines = [UserContactInline]


class HostIPInline(admin.StackedInline):

    """Edit an ip address on the host page."""

    model = models.HostIP


class MyHostAdmin(AuditedAdmin):

    """Custom host admin class to use our inlines."""

    inlines = [HostIPInline]
    

class DomainAdmin(AuditedAdmin):
    
    """Customize the domain search."""
    
    search_fields = ["name"]
    

class DomainApplicationAdmin(AuditedAdmin):
    
    """Customize the applications listing view."""
    
    list_display = ["requested_domain", "status", "creator", "created_at"]  
    
    list_filter = ('status', "created_at")  
    
    search_fields = ["requested_domain__name", "status"]

    # Filter the list
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        
        # Check if the user has the 'view_yourmodel' permission and filter out some objects from the query
        if not request.user.has_perm('registrar.domain_application'):
            return queryset.exclude(submitter__first_name='Michael')
            
        return queryset
    
    actions = [export_report]
    
    fieldsets = [
        (None, {"fields": ["status", "investigator", ("creator", "submitter"), "is_policy_acknowledged"]}),
        ("Organization", {"fields": ["organization_type", "federally_recognized_tribe", "state_recognized_tribe", "tribe_name", "federal_agency", "federal_type", "is_election_board", "organization_name", "type_of_work", "more_organization_information"]}),
        ("Organization address", {"fields": ["address_line1", "address_line2", "city", "state_territory", "zipcode", "urbanization"]}),
        ("Authorizing official", {"fields": ["authorizing_official"]}),
        ("Current websites", {"fields": ["current_websites"]}),
        ("Domains", {"fields": ["requested_domain", "alternative_domains", "purpose"]}),
        ("Other", {"fields": ["other_contacts", "no_other_contacts_rationale", "anything_else"]}),
    ]
    
    # Make some fields read only
    def get_readonly_fields(self, request, obj=None):
        # Specify the fields that should be read-only
        if obj:
            # Fields to be read-only for existing instances
            return ('creator', 'is_policy_acknowledged',)
        else:
            # Fields to be read-only for new instances
            pass
    
    # Hide some fileds completely based on permissions
    def get_fieldsets(self, request, obj=None):
        if not request.user.has_perm('registrar.domain_application'):
            # If the user doesn't have permission to change the model, show a read-only fieldset
            return (
                (None, {"fields": ["status", "creator", "submitter", "is_policy_acknowledged"]}),
            )

        # If the user has permission to change the model, show all fields
        return super().get_fieldsets(request, obj)
    
    # Trigger action when a fieldset is changed
    def save_model(self, request, obj, form, change):
        if change:  # Check if the object is being edited
            # Get the original object from the database
            original_obj = models.DomainApplication.objects.get(pk=obj.pk)
            
            if obj.status != original_obj.status:
                
                # Field has changed, trigger an action (e.g., send an email)
                
                # send_mail(
                #     'Status changed',
                #     f'The status for {obj.requested_domain} has been changed from {original_obj.status} to {obj.status}.',
                #     'from@example.com',
                #     ['rachid.mrad@gmail.com'],
                #     fail_silently=False,
                # )
                
                if original_obj.submitter is None or original_obj.submitter.email is None:
                    logger.warning(
                        "Cannot send confirmation email, no submitter email address."
                    )
                    return
                try:
                    print(f"original_obj.submitter.email {original_obj.submitter.email}")
                    send_templated_email(
                        "emails/submission_confirmation.txt",
                        "emails/submission_confirmation_subject.txt",
                        original_obj.submitter.email,
                        context={"application": self},
                    )
                except EmailSendingError:
                    logger.warning("Failed to send confirmation email", exc_info=True)

        super().save_model(request, obj, form, change)


admin.site.register(models.User, MyUserAdmin)
admin.site.register(models.UserDomainRole, AuditedAdmin)
admin.site.register(models.Contact, AuditedAdmin)
admin.site.register(models.DomainInvitation, AuditedAdmin)
admin.site.register(models.DomainInformation, AuditedAdmin)
admin.site.register(models.Host, MyHostAdmin)
admin.site.register(models.Nameserver, MyHostAdmin)
admin.site.register(models.Website, AuditedAdmin)

admin.site.register(models.Domain, DomainAdmin)
admin.site.register(models.DomainApplication, DomainApplicationAdmin)
