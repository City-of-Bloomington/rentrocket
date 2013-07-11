# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Inspection'
        db.create_table(u'inspection_inspection', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['building.Unit'])),
            ('building', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['building.Building'])),
            ('agency', self.gf('django.db.models.fields.CharField')(default='hlth', max_length=4)),
            ('agency_jurisdiction', self.gf('django.db.models.fields.CharField')(default='ci', max_length=2)),
            ('type', self.gf('django.db.models.fields.CharField')(default='pe', max_length=2)),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('rating', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('notes', self.gf('django.db.models.fields.TextField')()),
            ('score', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('added', self.gf('django.db.models.fields.DateTimeField')()),
            ('updated', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'inspection', ['Inspection'])

        # Adding model 'Violation'
        db.create_table(u'inspection_violation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('inspection', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['inspection.Inspection'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('date_closed', self.gf('django.db.models.fields.DateTimeField')()),
            ('category', self.gf('django.db.models.fields.CharField')(default='other', max_length=4)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('severity', self.gf('django.db.models.fields.CharField')(max_length=12, blank=True)),
            ('legal_authority', self.gf('django.db.models.fields.CharField')(max_length=12, blank=True)),
        ))
        db.send_create_signal(u'inspection', ['Violation'])


    def backwards(self, orm):
        # Deleting model 'Inspection'
        db.delete_table(u'inspection_inspection')

        # Deleting model 'Violation'
        db.delete_table(u'inspection_violation')


    models = {
        u'building.building': {
            'Meta': {'object_name': 'Building'},
            'added': ('django.db.models.fields.DateTimeField', [], {}),
            'built_year': ('django.db.models.fields.IntegerField', [], {}),
            'from_st': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'longitude': ('django.db.models.fields.FloatField', [], {}),
            'number_of_units': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'parcel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['building.Parcel']"}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['source.Source']"}),
            'sqft': ('django.db.models.fields.IntegerField', [], {}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'street': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'street_type': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'to_st': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {}),
            'value': ('django.db.models.fields.FloatField', [], {})
        },
        u'building.parcel': {
            'Meta': {'object_name': 'Parcel'},
            'added': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'shape': ('django.db.models.fields.TextField', [], {}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['source.Source']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'building.unit': {
            'Meta': {'object_name': 'Unit'},
            'added': ('django.db.models.fields.DateTimeField', [], {}),
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'bathrooms': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'bedrooms': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'building': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['building.Building']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_occupants': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'square_feet': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'inspection.inspection': {
            'Meta': {'object_name': 'Inspection'},
            'added': ('django.db.models.fields.DateTimeField', [], {}),
            'agency': ('django.db.models.fields.CharField', [], {'default': "'hlth'", 'max_length': '4'}),
            'agency_jurisdiction': ('django.db.models.fields.CharField', [], {'default': "'ci'", 'max_length': '2'}),
            'building': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['building.Building']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {}),
            'rating': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'score': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'pe'", 'max_length': '2'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['building.Unit']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'inspection.violation': {
            'Meta': {'object_name': 'Violation'},
            'category': ('django.db.models.fields.CharField', [], {'default': "'other'", 'max_length': '4'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'date_closed': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inspection': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['inspection.Inspection']"}),
            'legal_authority': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'severity': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'})
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

    complete_apps = ['inspection']