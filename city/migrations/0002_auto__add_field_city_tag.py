# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'City.tag'
        db.add_column(u'city_city', 'tag',
                      self.gf('django.db.models.fields.CharField')(default='<django.db.models.fields.charfield>', unique=True, max_length=200),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'City.tag'
        db.delete_column(u'city_city', 'tag')


    models = {
        u'city.city': {
            'Meta': {'object_name': 'City'},
            'added': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'tag': ('django.db.models.fields.CharField', [], {'default': "'<django.db.models.fields.charfield>'", 'unique': 'True', 'max_length': '200'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {})
        }
    }

    complete_apps = ['city']