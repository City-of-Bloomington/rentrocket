# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'StatementUpload.vendor'
        db.add_column(u'utility_statementupload', 'vendor',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=200, blank=True),
                      keep_default=False)

        # Adding field 'StatementUpload.type'
        db.add_column(u'utility_statementupload', 'type',
                      self.gf('django.db.models.fields.CharField')(default='electricity', max_length=12),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'StatementUpload.vendor'
        db.delete_column(u'utility_statementupload', 'vendor')

        # Deleting field 'StatementUpload.type'
        db.delete_column(u'utility_statementupload', 'type')


    models = {
        u'building.building': {
            'Meta': {'object_name': 'Building'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'built_year': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['city.City']"}),
            'energy_score': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'geocoder': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'longitude': ('django.db.models.fields.FloatField', [], {}),
            'number_of_units': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'parcel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['building.Parcel']"}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['source.Source']"}),
            'sqft': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'walk_score': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'building.parcel': {
            'Meta': {'object_name': 'Parcel'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'custom_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'from_st': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'shape': ('django.db.models.fields.TextField', [], {}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'street_type': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'to_st': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'building.unit': {
            'Meta': {'object_name': 'Unit'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'bathrooms': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'bedrooms': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'building': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'units'", 'to': u"orm['building.Building']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_occupants': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'sqft': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'city.city': {
            'Meta': {'object_name': 'City'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'longitude': ('django.db.models.fields.FloatField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'tag': ('django.db.models.fields.CharField', [], {'default': "'<django.db.models.fields.charfield>'", 'unique': 'True', 'max_length': '200'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'city'", 'max_length': '50'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        u'person.person': {
            'Meta': {'object_name': 'Person'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['city.City']", 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        u'source.feedinfo': {
            'Meta': {'object_name': 'FeedInfo'},
            'added': ('django.db.models.fields.DateTimeField', [], {}),
            'building_id_definition': ('django.db.models.fields.TextField', [], {}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['city.City']"}),
            'contact_email': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parcel_id_definition': ('django.db.models.fields.TextField', [], {}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '12'})
        },
        u'source.source': {
            'Meta': {'object_name': 'Source'},
            'feed': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['source.FeedInfo']", 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['person.Person']", 'blank': 'True'})
        },
        u'utility.statementupload': {
            'Meta': {'object_name': 'StatementUpload'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'blob_key': ('django.db.models.fields.TextField', [], {}),
            'building_address': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'city_tag': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'energy_sources': ('jsonfield.fields.JSONField', [], {'null': 'True', 'blank': 'True'}),
            'energy_strategy': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39'}),
            'move_in': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['person.Person']", 'null': 'True', 'blank': 'True'}),
            'person_email': ('django.db.models.fields.EmailField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'processed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'electricity'", 'max_length': '12'}),
            'unit_details': ('jsonfield.fields.JSONField', [], {'blank': 'True'}),
            'unit_number': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'vendor': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'utility.utilitysummary': {
            'Meta': {'object_name': 'UtilitySummary'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'amount': ('django.db.models.fields.FloatField', [], {}),
            'building': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['building.Building']"}),
            'cost': ('django.db.models.fields.FloatField', [], {'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['source.Source']"}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {}),
            'statement': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['utility.StatementUpload']", 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'electricity'", 'max_length': '12'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['building.Unit']"}),
            'unit_of_measurement': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'vendor': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        }
    }

    complete_apps = ['utility']