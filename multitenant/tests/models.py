from django.test import TestCase
from django.test.client import Client

from django.db import models
from django.conf import settings

from multitenant.models import *


class TenantAwareModel(TenantModel):
    name = models.CharField(max_length=10)


class TenantModelTests(TestCase):
 
    def setUp(self):
        # Tenant and logged in user setup
        self.tenant1 = Tenant.objects.create(name='Tenant1', email='tenant1@example.com')
        self.tenant2 = Tenant.objects.create(name='Tenant2', email='tenant2@example.com')
        self.user = User.objects.create_user(username='user1', email='user1@example.com', password='123')
        user_profile_class = get_profile_class()
        
        if not isinstance(user_profile_class, TenantModel):
            raise TypeError('The User profile class MUST be derived from TenantModel.')

        user_profile_class.objects.create(user=self.user, tenant=self.tenant1)    # This will fail if any of the fields other than user are required fields
        self.client = Client()
        self.client.login(username=self.user.username, password='123')

    
    def tearDown(self):
        pass

    
    def tenant_set_while_saving(self):
        # Tenant aware objects setup
        obj1 = TenantAwareModel(name='obj1')
        obj1.clean()    # This is where the tenant gets set automatically
        obj1.save()
        self.assetEqual(obj1.tenant, get_current_tenant())
        
    def custom_manager(self):
        # Verify that the custom manager filters the queryset as per the currently logged in user
        obj1 = TenantAwareModel.objects(name='obj1')
        obj1.clean()    # This is where the tenant gets set automatically
        obj1.save()
        obj2 = TenantAwareModel.objects.create(name='obj2', tenant=self.tenant2)
        tenant_objects = TenantAwareModel.tenant_objects.all()
        self.assertEqual(len(tenant_objects), 1)
        self.assertEqual(tenant_objects[0], obj1)

    def cloning(self):
        