"""
A collection of useful tools related to the multitenant app.
See the functions' docstrings for details and examples.
"""

from django.shortcuts import get_object_or_404
from django.http import Http404

from middleware import get_current_tenant


def current_tenant_owns_object(obj):
    """
    To verify that the current logged in tenant owns a particular instance.
    example:
        if current_tenant_owns_object(obj):
            do_something()
    """
    if hasattr(obj, 'tenant'):
        t = get_current_tenant()
        if t != obj.tenant:
            return False
    return True


def tenant_get_object_or_404(klass, *args, **kwargs):
    """
    A tenant-aware version of django's get_object_or_404 shortcut.
    example:
        tenant_get_object_or_404(BugReport, id=1)
    """
    obj = get_object_or_404(klass, *args, **kwargs)
    
    if obj and hasattr(obj, 'tenant'):
        t = get_current_tenant()
        if t != obj.tenant:
            raise Http404
    
    return obj
        
        
def tenant_filter(queryset):
    """
    To filter a queryset so that all instances belong to the currently logged in tenant.
    example:
        bugs = BugReport.objects.all()
        bugs = tenant_filter(bugs)
    """
    if hasattr(queryset.model, 'tenant'):
        t = get_current_tenant()
        return queryset.filter(tenant=t)   
    return queryset 
