from django.test import TestCase
from django.test.client import Client

from django.db import models
from django.conf import settings

from multitenant.models import *
from multitenant.settings import BASE_TENANT_ID
from multitenant.middleware import set_current_tenant



class TenantModelTests(TestCase):
 
    def setUp(self):
        # Tenant and logged in user setup
        self.tenant1 = Tenant.objects.create(name='Tenant1', email='tenant1@example.com')
        self.tenant2 = Tenant.objects.create(name='Tenant2', email='tenant2@example.com')
        self.user = User.objects.create_user(username='user1', email='user1@example.com', password='123')
        user_profile_class = get_profile_class()

        # Thanks to django's metaclass setup for Models, you can't directly check for a model's base
        # classes this way, so instead we just check if the user profile has a field named tenant.
#        if not isinstance(user_profile_class, TenantModel):
        if not getattr(user_profile_class, 'tenant'):
            raise TypeError('The User profile class for this project MUST be derived from TenantModel.')

        user_profile_class.objects.create(user=self.user, tenant=self.tenant1)    # This will fail if any of the fields other than user are required fields
        self.client = Client()
        self.client.login(username=self.user.username, password='123')

    
    def tearDown(self):
        pass

    
    def test_tenant_set_while_saving(self):
        # Tenant aware objects setup
        set_current_tenant(self.tenant1)
        obj1 = TestTenantAwareModel(name='obj1')
        obj1.clean()    # This is where the tenant gets set automatically
        obj1.save()
        self.assertEqual(obj1.tenant, get_current_tenant())
        
    def test_custom_manager(self):
        # Verify that the custom manager filters the queryset as per the currently logged in user
        set_current_tenant(self.tenant1)
        obj1 = TestTenantAwareModel(name='obj1')
        obj1.clean()    # This is where the tenant gets set automatically
        obj1.save()
        obj2 = TestTenantAwareModel.objects.create(name='obj2', tenant=self.tenant2)
        tenant_objects = TestTenantAwareModel.tenant_objects.all()
        self.assertEqual(len(tenant_objects), 1,  "While using custom manager: Expected just one object in tenant-filtered queryset.")
        self.assertEqual(tenant_objects[0], obj1,  "While using custom manager: Object in tenant-filtered queryset is not the right one." )

    def test_cloning(self):
        base, created = Tenant.objects.get_or_create(id=BASE_TENANT_ID, defaults={ 'name':'Base Tenant', 'email':'base@example.com' })
        obj = TestTenantAwareModel.objects.create(name='be_cloned', tenant=base)
        new_tenant = Tenant.objects.create(name='new', email='new@example.com')
        cloned_objects = TestTenantAwareModel.objects.filter(tenant=new_tenant)
        self.assertEqual(len(cloned_objects), 1, "While creating new tenant: Expected to clone just one object from base tenant.")
        self.assertEqual(cloned_objects[0].name, 'be_cloned', "While creating new tenant: Cloned object is not the right one.")



