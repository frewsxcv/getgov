import csv
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.contenttypes.models import ContentType
from django.http.response import HttpResponseRedirect
from django.urls import reverse
from django.http import HttpResponse

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
    search_fields = ["requested_domain__name"]
    fieldsets = [
        (None, {"fields": ["status", "creator", "submitter", "is_policy_acknowledged"]}),
        ("Organization", {"fields": ["organization_type", "federally_recognized_tribe", "state_recognized_tribe", "tribe_name", "federal_agency", "federal_type", "is_election_board", "organization_name", "type_of_work", "more_organization_information"]}),
        ("Organization address", {"fields": ["address_line1", "address_line2", "city", "state_territory", "zipcode", "urbanization"]}),
        ("Authorizing official", {"fields": ["authorizing_official"]}),
        ("Current websites", {"fields": ["current_websites"]}),
        ("Domains", {"fields": ["requested_domain", "alternative_domains", "purpose"]}),
        ("Other", {"fields": ["other_contacts", "no_other_contacts_rationale", "anything_else"]}),
    ]
    actions = [export_report]


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
