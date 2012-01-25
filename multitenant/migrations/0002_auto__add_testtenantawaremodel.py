# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'TestTenantAwareModel'
        db.create_table('multitenant_testtenantawaremodel', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tenant', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['multitenant.Tenant'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal('multitenant', ['TestTenantAwareModel'])


    def backwards(self, orm):
        
        # Deleting model 'TestTenantAwareModel'
        db.delete_table('multitenant_testtenantawaremodel')


    models = {
        'multitenant.tenant': {
            'Meta': {'object_name': 'Tenant'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'})
        },
        'multitenant.testtenantawaremodel': {
            'Meta': {'object_name': 'TestTenantAwareModel'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'tenant': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['multitenant.Tenant']"})
        }
    }

    complete_apps = ['multitenant']
