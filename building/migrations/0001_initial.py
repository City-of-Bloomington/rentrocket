# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Parcel'
        db.create_table(u'building_parcel', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('custom_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('shape', self.gf('django.db.models.fields.TextField')()),
            ('from_st', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('to_st', self.gf('django.db.models.fields.CharField')(max_length=12, blank=True)),
            ('street', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('street_type', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['source.Source'])),
            ('added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'building', ['Parcel'])

        # Adding model 'Building'
        db.create_table(u'building_building', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('parcel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['building.Parcel'])),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('postal_code', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('latitude', self.gf('django.db.models.fields.FloatField')()),
            ('longitude', self.gf('django.db.models.fields.FloatField')()),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=12, blank=True)),
            ('number_of_units', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('built_year', self.gf('django.db.models.fields.IntegerField')()),
            ('sqft', self.gf('django.db.models.fields.IntegerField')()),
            ('value', self.gf('django.db.models.fields.FloatField')(blank=True)),
            ('city', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['city.City'])),
            ('source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['source.Source'])),
            ('added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'building', ['Building'])

        # Adding model 'Unit'
        db.create_table(u'building_unit', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('building', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['building.Building'])),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('bedrooms', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('bathrooms', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('square_feet', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('max_occupants', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'building', ['Unit'])

        # Adding model 'Listing'
        db.create_table(u'building_listing', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['building.Unit'])),
            ('lease_type', self.gf('django.db.models.fields.CharField')(default='Standard', max_length=200)),
            ('lease_term', self.gf('django.db.models.fields.CharField')(default='12 Months', max_length=200)),
            ('available_start', self.gf('django.db.models.fields.DateTimeField')()),
            ('available_end', self.gf('django.db.models.fields.DateTimeField')()),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('cost', self.gf('django.db.models.fields.FloatField')()),
            ('cost_cycle', self.gf('django.db.models.fields.CharField')(default='month', max_length=10)),
            ('deposit', self.gf('django.db.models.fields.FloatField')()),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('pets', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal(u'building', ['Listing'])

        # Adding model 'Permit'
        db.create_table(u'building_permit', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'building', ['Permit'])


    def backwards(self, orm):
        # Deleting model 'Parcel'
        db.delete_table(u'building_parcel')

        # Deleting model 'Building'
        db.delete_table(u'building_building')

        # Deleting model 'Unit'
        db.delete_table(u'building_unit')

        # Deleting model 'Listing'
        db.delete_table(u'building_listing')

        # Deleting model 'Permit'
        db.delete_table(u'building_permit')


    models = {
        u'building.building': {
            'Meta': {'object_name': 'Building'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'built_year': ('django.db.models.fields.IntegerField', [], {}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['city.City']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'longitude': ('django.db.models.fields.FloatField', [], {}),
            'number_of_units': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'parcel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['building.Parcel']"}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['source.Source']"}),
            'sqft': ('django.db.models.fields.IntegerField', [], {}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.FloatField', [], {'blank': 'True'})
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
            'custom_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'}),
            'from_st': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'shape': ('django.db.models.fields.TextField', [], {}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['source.Source']"}),
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
            'square_feet': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'city.city': {
            'Meta': {'object_name': 'City'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'tag': ('django.db.models.fields.CharField', [], {'default': "'<django.db.models.fields.charfield>'", 'unique': 'True', 'max_length': '200'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'person.person': {
            'Meta': {'object_name': 'Person'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'source.feedinfo': {
            'Meta': {'object_name': 'FeedInfo'},
            'added': ('django.db.models.fields.DateTimeField', [], {}),
            'building_id_definition': ('django.db.models.fields.TextField', [], {}),
            'contact_email': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'municipality_name': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'municipality_url': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
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