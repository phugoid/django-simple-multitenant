from django.test import TestCase
from django.test.client import Client
from django.http import Http404

from django.db import models
from django.conf import settings

from multitenant.models import *
from multitenant.utils import *
from multitenant.middleware import set_current_tenant



class TenantUtilsTests(TestCase):
 
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

    
    def test_current_tenant_owns_object(self):
        set_current_tenant(self.tenant1)
        obj1 = TestTenantAwareModel.objects.create(name='obj1', tenant=self.tenant1)
        obj2 = TestTenantAwareModel.objects.create(name='obj2', tenant=self.tenant2)
        self.assertTrue( current_tenant_owns_object(obj1) )
        self.assertFalse( current_tenant_owns_object(obj2) )

    def test_tenant_get_object_or_404(self):
        set_current_tenant(self.tenant1)
        obj1 = TestTenantAwareModel.objects.create(name='obj1', tenant=self.tenant1)
        obj2 = TestTenantAwareModel.objects.create(name='obj2', tenant=self.tenant2)

        self.assertEqual(tenant_get_object_or_404(TestTenantAwareModel, id=obj1.id), obj1)
        self.failUnlessRaises(Http404, lambda : tenant_get_object_or_404(TestTenantAwareModel, id=obj2.id))
        
    def test_tenant_filter(self):
        set_current_tenant(self.tenant1)
        obj1 = TestTenantAwareModel.objects.create(name='obj1', tenant=self.tenant1)
        obj2 = TestTenantAwareModel.objects.create(name='obj2', tenant=self.tenant2)

        objects = TestTenantAwareModel.objects.all()
        self.assertEqual( len(objects), 2, 'Incorrect number of objects in queryset.' )
        objects = tenant_filter(objects)
        self.assertEqual( len(objects), 1, 'Incorrect number of objects in tenant-filtered queryset.' )
        self.assertEqual( objects[0].name, 'obj1', 'Wrong object shows up in tenant-filtered queryset')
