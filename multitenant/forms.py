"""
For any model that subclasses TenantModel, you'll want to use a TenantModelForm instead of django's ModelForm.
The TenantModelForm has two useful features:
1. All ModelChoiceFields and ModelMultipleChoiceFields have their querysets filtered to show only the
   values for the current tenant.  This happens during form class instantiation.
2. The form's clean() method sets the instance's tenant field to that of the currently logged in user.

example:

    class CompanyForm(TenantModelForm):
        class Meta:
            model = Company

Note that we don't need to worry about filtering the options available for each form field.
"""

from django import forms

from middleware import get_current_tenant


class TenantModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TenantModelForm, self).__init__(*args, **kwargs)

        tenant = get_current_tenant()
        if tenant:
            for field in self.fields.values():
                if isinstance(field, (forms.ModelChoiceField, forms.ModelMultipleChoiceField,)):
                    # Check if the model being used for the ModelChoiceField has a tenant model field
                    if hasattr(field.queryset.model, 'tenant'):
                        # Add filter restricting queryset to values to this tenant only.
                        field.queryset = field.queryset.filter(tenant=tenant)
                
    def clean(self):
        cleaned_data = super(TenantModelForm, self).clean()
        
        if hasattr(self.instance, 'tenant_id'):
            self.instance.tenant = get_current_tenant()
        return cleaned_data


