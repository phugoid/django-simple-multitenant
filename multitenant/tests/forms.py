from django.test import TestCase
from django.test.client import Client

from django.db import models
from django.conf import settings

from multitenant.models import *
from multitenant.forms import *
from multitenant.settings import BASE_TENANT_ID
from multitenant.middleware import set_current_tenant



class TenantFormTests(TestCase):
 
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
    
    def test_tenant_model_form(self):
        set_current_tenant(self.tenant1)
        obj1 = TestTenantAwareModel.objects.create(name='obj1', tenant=self.tenant1)
        obj2 = TestTenantAwareModel.objects.create(name='obj2', tenant=self.tenant2)

        class TestForm(TenantModelForm):
            class Meta:
                model = TestTenantAwareModel
                exclude = ['tenant']
                

        form = TestForm({ 'name': 'blah', 'm2mfield': [ obj1.id ] })
        fk_options = form.fields['fkfield'].queryset
        self.assertEqual(len(fk_options), 1, 'Wrong number of options in form queryset for foreign key field.')
        self.assertEqual(fk_options[0].name, 'obj1', 'Wrong object in foreign key queryset.')

        m2m_options = form.fields['m2mfield'].queryset
        self.assertEqual(len(m2m_options), 1, 'Wrong number of options in form queryset for many-to-many field.')
        self.assertEqual(m2m_options[0].name, 'obj1', 'Wrong object in many-to-many queryset.')

        self.assertEqual(form.is_valid(), True, 'Form is not valid')
        instance = form.save()
        self.assertEqual(instance.tenant, self.tenant1)
        