
try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

_thread_locals = local()


def get_current_user():
    """
    Despite arguments to the contrary, it is sometimes necessary to find out who is the current
    logged in user, even if the request object is not in scope.  The best way to do this is 
    by storing the user object in middleware while processing the request.
    """
    return getattr(_thread_locals, 'user', None)


def get_current_tenant():
    """
    To get the Tenant instance for the currently logged in tenant.
    example:
        tenant = get_current_tenant()
    """
    tenant = getattr(_thread_locals, 'tenant', None)

    # tenant may not be set yet, if request user is anonymous, or has no profile,
    if not tenant:
        set_tenant_to_default()
    
    return getattr(_thread_locals, 'tenant', None)


def set_tenant_to_default():
    """
    Sets the current tenant as per BASE_TENANT_ID.
    """
    # import is done from within the function, to avoid trouble 
    from models import Tenant, BASE_TENANT_ID
    set_current_tenant( Tenant.objects.get(id=BASE_TENANT_ID) )
    

def set_current_tenant(tenant):
    setattr(_thread_locals, 'tenant', tenant)


class ThreadLocals(object):
    """Middleware that gets various objects from the
    request object and saves them in thread local storage."""
    def process_request(self, request):
        _thread_locals.user = getattr(request, 'user', None)

        # Attempt to set tenant
        if _thread_locals.user and not _thread_locals.user.is_anonymous():
            try:
                profile = _thread_locals.user.get_profile()
                if profile:
                    _thread_locals.tenant = getattr(profile, 'tenant', None)
            except:
                # If the profile lookup failed, we're in deep doodoo.  It's not 
                # safe to set a default tenant for this User - it might give access
                # to the base tenant which is cloned to create all new tenants.
                raise ValueError(
                    """A User was created with no profile.  For security reasons, 
                    we cannot allow the request to be processed any further.
                    Try deleting this User and creating it again to ensure a 
                    UserProfile gets attached, or link a UserProfile 
                    to this User.""")
        else:
            # It's important that we hit the db once to set the tenant, even if 
            # it's an anonymous user.  That way we get fresh values from the db,
            # including the tenant options.
            #
            # An anonymous user, for example, still has access to the login page,
            # so he will see the primary navigation tabs.  To decide which primary
            # navigation tabs to show, we need the tenant to be set.
            #
            # Not: If we simply set the tenant once and left it in a module-level 
            # variable, it would stay latched between page requests which is NOT
            # what we want.
            set_tenant_to_default()


