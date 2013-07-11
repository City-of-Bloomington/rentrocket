# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FeedInfo'
        db.create_table(u'source_feedinfo', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('added', self.gf('django.db.models.fields.DateTimeField')()),
            ('version', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('municipality_name', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('building_id_definition', self.gf('django.db.models.fields.TextField')()),
            ('parcel_id_definition', self.gf('django.db.models.fields.TextField')()),
            ('municipality_url', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('contact_email', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
        ))
        db.send_create_signal(u'source', ['FeedInfo'])

        # Adding model 'Source'
        db.create_table(u'source_source', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('feed', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['source.FeedInfo'], blank=True)),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['person.Person'], blank=True)),
        ))
        db.send_create_signal(u'source', ['Source'])


    def backwards(self, orm):
        # Deleting model 'FeedInfo'
        db.delete_table(u'source_feedinfo')

        # Deleting model 'Source'
        db.delete_table(u'source_source')


    models = {
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

    complete_apps = ['source']