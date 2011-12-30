"""
By default, django-admin will show you all model instances.  In a multitenant project, you might want to 
"visit" a tenant's account, and see just the instances that belong to them.  If you use TenantAdmin as your
ModelAdmin class, you will see only the instances for the currently logged-in user (yourself).

You can then visit any tenant you please, by changing the Tenant linked to your own user profile.

example:

    from django.contrib import admin
    from multitenant.admin import TenantAdmin
    from myapp.models import *
    
    admin.site.register(BugReport, TenantAdmin) 
"""

from django.contrib import admin

from models import *
from forms import TenantModelForm
from middleware import get_current_tenant

admin.site.register(Tenant)


class TenantAdmin(admin.ModelAdmin):
    exclude = ('tenant',)
    
    # Filter all relation fields' querysets by tenant
    form = TenantModelForm
    
    def queryset(self, request):
        qs = super(TenantAdmin, self).queryset(request)
        return qs.filter(tenant = get_current_tenant() )
    