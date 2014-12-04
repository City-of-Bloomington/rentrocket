# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'City.cutoffs'
        db.add_column(u'city_city', 'cutoffs',
                      self.gf('django.db.models.fields.CharField')(default='50,250,500,1000', max_length=200),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'City.cutoffs'
        db.delete_column(u'city_city', 'cutoffs')


    models = {
        u'city.city': {
            'Meta': {'object_name': 'City'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'cutoffs': ('django.db.models.fields.CharField', [], {'default': "'50,250,500,1000'", 'max_length': '200'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'longitude': ('django.db.models.fields.FloatField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'tag': ('django.db.models.fields.CharField', [], {'default': "'<django.db.models.fields.charfield>'", 'unique': 'True', 'max_length': '200'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'city'", 'max_length': '50'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        }
    }

    complete_apps = ['city']