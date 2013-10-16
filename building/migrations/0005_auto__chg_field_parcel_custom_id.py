# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Parcel.custom_id'
        db.alter_column(u'building_parcel', 'custom_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50))

    def backwards(self, orm):

        # Changing field 'Parcel.custom_id'
        db.alter_column(u'building_parcel', 'custom_id', self.gf('django.db.models.fields.CharField')(max_length=30, unique=True))

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
        u'building.buildingperson': {
            'Meta': {'object_name': 'BuildingPerson'},
            'building': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['building.Building']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['person.Person']"}),
            'relation': ('django.db.models.fields.CharField', [], {'default': "'Unknown'", 'max_length': '50'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['building.Unit']", 'null': 'True', 'blank': 'True'})
        },
        u'building.listing': {
            'Meta': {'object_name': 'Listing'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'available_end': ('django.db.models.fields.DateTimeField', [], {}),
            'available_start': ('django.db.models.fields.DateTimeField', [], {}),
            'cost': ('django.db.models.fields.FloatField', [], {}),
            'cost_cycle': ('django.db.models.fields.CharField', [], {'default': "'month'", 'max_length': '10'}),
            'deposit': ('django.db.models.fields.FloatField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lease_term': ('django.db.models.fields.CharField', [], {'default': "'12 Months'", 'max_length': '200'}),
            'lease_type': ('django.db.models.fields.CharField', [], {'default': "'Standard'", 'max_length': '200'}),
            'pets': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['building.Unit']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
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
        u'building.permit': {
            'Meta': {'object_name': 'Permit'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'building.unit': {
            'Meta': {'object_name': 'Unit'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'bathrooms': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'bedrooms': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'building': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['building.Building']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_occupants': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
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
        }
    }

    complete_apps = ['building']