# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ChangeDetails'
        db.create_table(u'building_changedetails', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('original_values', self.gf('jsonfield.fields.JSONField')()),
            ('new_values', self.gf('jsonfield.fields.JSONField')()),
            ('building', self.gf('django.db.models.fields.related.ForeignKey')(related_name='changes', to=orm['building.Building'])),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='changes', null=True, to=orm['building.Unit'])),
            ('added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'building', ['ChangeDetails'])

        # Adding model 'BuildingComment'
        db.create_table(u'building_buildingcomment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('building', self.gf('django.db.models.fields.related.ForeignKey')(related_name='comments', to=orm['building.Building'])),
            ('message', self.gf('django.db.models.fields.TextField')()),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'building', ['BuildingComment'])

        # Adding model 'BuildingDocument'
        db.create_table(u'building_buildingdocument', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('blob_key', self.gf('django.db.models.fields.TextField')()),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('building', self.gf('django.db.models.fields.related.ForeignKey')(related_name='documents', to=orm['building.Building'])),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='documents', null=True, to=orm['building.Unit'])),
            ('added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'building', ['BuildingDocument'])

        # Adding model 'UnitType'
        db.create_table(u'building_unittype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'building', ['UnitType'])

        # Adding model 'BuildingPhoto'
        db.create_table(u'building_buildingphoto', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('blob_key', self.gf('django.db.models.fields.TextField')()),
            ('filename', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('building', self.gf('django.db.models.fields.related.ForeignKey')(related_name='photos', to=orm['building.Building'])),
            ('unit', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='photos', null=True, to=orm['building.Unit'])),
            ('added', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'building', ['BuildingPhoto'])

        # Adding field 'Unit.floor'
        db.add_column(u'building_unit', 'floor',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Unit.tag'
        db.add_column(u'building_unit', 'tag',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=20),
                      keep_default=False)


        # Changing field 'Unit.number'
        db.alter_column(u'building_unit', 'number', self.gf('django.db.models.fields.CharField')(max_length=20))
        # Adding field 'Building.website'
        db.add_column(u'building_building', 'website',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=200, blank=True),
                      keep_default=False)

        # Adding field 'Building.energy_improvements'
        db.add_column(u'building_building', 'energy_improvements',
                      self.gf('jsonfield.fields.JSONField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Building.renewable_energy'
        db.add_column(u'building_building', 'renewable_energy',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Building.renewable_energy_detials'
        db.add_column(u'building_building', 'renewable_energy_detials',
                      self.gf('jsonfield.fields.JSONField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Building.composting'
        db.add_column(u'building_building', 'composting',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Building.recycling'
        db.add_column(u'building_building', 'recycling',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Building.garden'
        db.add_column(u'building_building', 'garden',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Building.garden_detials'
        db.add_column(u'building_building', 'garden_detials',
                      self.gf('jsonfield.fields.JSONField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Building.bike_friendly'
        db.add_column(u'building_building', 'bike_friendly',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Building.bike_friendly_detials'
        db.add_column(u'building_building', 'bike_friendly_detials',
                      self.gf('jsonfield.fields.JSONField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Building.walk_friendly'
        db.add_column(u'building_building', 'walk_friendly',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Building.walk_friendly_detials'
        db.add_column(u'building_building', 'walk_friendly_detials',
                      self.gf('jsonfield.fields.JSONField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Building.transit_friendly'
        db.add_column(u'building_building', 'transit_friendly',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Building.transit_friendly_detials'
        db.add_column(u'building_building', 'transit_friendly_detials',
                      self.gf('jsonfield.fields.JSONField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Building.bike_score'
        db.add_column(u'building_building', 'bike_score',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Building.transit_score'
        db.add_column(u'building_building', 'transit_score',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'Building.smart_living'
        db.add_column(u'building_building', 'smart_living',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Building.air_conditioning'
        db.add_column(u'building_building', 'air_conditioning',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Building.laundry'
        db.add_column(u'building_building', 'laundry',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50),
                      keep_default=False)

        # Adding field 'Building.parking'
        db.add_column(u'building_building', 'parking',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50),
                      keep_default=False)

        # Adding field 'Building.pets'
        db.add_column(u'building_building', 'pets',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=50),
                      keep_default=False)

        # Adding field 'Building.gym'
        db.add_column(u'building_building', 'gym',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Building.pool'
        db.add_column(u'building_building', 'pool',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Building.game_room'
        db.add_column(u'building_building', 'game_room',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Building.amenities'
        db.add_column(u'building_building', 'amenities',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'Building.visible'
        db.add_column(u'building_building', 'visible',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'Building.tag'
        db.add_column(u'building_building', 'tag',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=200),
                      keep_default=False)

        # Adding field 'Listing.user'
        db.add_column(u'building_listing', 'user',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, blank=True),
                      keep_default=False)

        # Adding field 'Listing.building'
        db.add_column(u'building_listing', 'building',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='listings', null=True, to=orm['building.Building']),
                      keep_default=False)

        # Adding field 'BuildingPerson.visible'
        db.add_column(u'building_buildingperson', 'visible',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'ChangeDetails'
        db.delete_table(u'building_changedetails')

        # Deleting model 'BuildingComment'
        db.delete_table(u'building_buildingcomment')

        # Deleting model 'BuildingDocument'
        db.delete_table(u'building_buildingdocument')

        # Deleting model 'UnitType'
        db.delete_table(u'building_unittype')

        # Deleting model 'BuildingPhoto'
        db.delete_table(u'building_buildingphoto')

        # Deleting field 'Unit.floor'
        db.delete_column(u'building_unit', 'floor')

        # Deleting field 'Unit.tag'
        db.delete_column(u'building_unit', 'tag')


        # Changing field 'Unit.number'
        db.alter_column(u'building_unit', 'number', self.gf('django.db.models.fields.CharField')(max_length=10))
        # Deleting field 'Building.website'
        db.delete_column(u'building_building', 'website')

        # Deleting field 'Building.energy_improvements'
        db.delete_column(u'building_building', 'energy_improvements')

        # Deleting field 'Building.renewable_energy'
        db.delete_column(u'building_building', 'renewable_energy')

        # Deleting field 'Building.renewable_energy_detials'
        db.delete_column(u'building_building', 'renewable_energy_detials')

        # Deleting field 'Building.composting'
        db.delete_column(u'building_building', 'composting')

        # Deleting field 'Building.recycling'
        db.delete_column(u'building_building', 'recycling')

        # Deleting field 'Building.garden'
        db.delete_column(u'building_building', 'garden')

        # Deleting field 'Building.garden_detials'
        db.delete_column(u'building_building', 'garden_detials')

        # Deleting field 'Building.bike_friendly'
        db.delete_column(u'building_building', 'bike_friendly')

        # Deleting field 'Building.bike_friendly_detials'
        db.delete_column(u'building_building', 'bike_friendly_detials')

        # Deleting field 'Building.walk_friendly'
        db.delete_column(u'building_building', 'walk_friendly')

        # Deleting field 'Building.walk_friendly_detials'
        db.delete_column(u'building_building', 'walk_friendly_detials')

        # Deleting field 'Building.transit_friendly'
        db.delete_column(u'building_building', 'transit_friendly')

        # Deleting field 'Building.transit_friendly_detials'
        db.delete_column(u'building_building', 'transit_friendly_detials')

        # Deleting field 'Building.bike_score'
        db.delete_column(u'building_building', 'bike_score')

        # Deleting field 'Building.transit_score'
        db.delete_column(u'building_building', 'transit_score')

        # Deleting field 'Building.smart_living'
        db.delete_column(u'building_building', 'smart_living')

        # Deleting field 'Building.air_conditioning'
        db.delete_column(u'building_building', 'air_conditioning')

        # Deleting field 'Building.laundry'
        db.delete_column(u'building_building', 'laundry')

        # Deleting field 'Building.parking'
        db.delete_column(u'building_building', 'parking')

        # Deleting field 'Building.pets'
        db.delete_column(u'building_building', 'pets')

        # Deleting field 'Building.gym'
        db.delete_column(u'building_building', 'gym')

        # Deleting field 'Building.pool'
        db.delete_column(u'building_building', 'pool')

        # Deleting field 'Building.game_room'
        db.delete_column(u'building_building', 'game_room')

        # Deleting field 'Building.amenities'
        db.delete_column(u'building_building', 'amenities')

        # Deleting field 'Building.visible'
        db.delete_column(u'building_building', 'visible')

        # Deleting field 'Building.tag'
        db.delete_column(u'building_building', 'tag')

        # Deleting field 'Listing.user'
        db.delete_column(u'building_listing', 'user_id')

        # Deleting field 'Listing.building'
        db.delete_column(u'building_listing', 'building_id')

        # Deleting field 'BuildingPerson.visible'
        db.delete_column(u'building_buildingperson', 'visible')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'building.building': {
            'Meta': {'object_name': 'Building'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'air_conditioning': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'amenities': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'bike_friendly': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'bike_friendly_detials': ('jsonfield.fields.JSONField', [], {'blank': 'True'}),
            'bike_score': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'built_year': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['city.City']"}),
            'composting': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'energy_improvements': ('jsonfield.fields.JSONField', [], {'blank': 'True'}),
            'energy_score': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'game_room': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'garden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'garden_detials': ('jsonfield.fields.JSONField', [], {'blank': 'True'}),
            'geocoder': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'gym': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'laundry': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50'}),
            'longitude': ('django.db.models.fields.FloatField', [], {}),
            'number_of_units': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'parcel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['building.Parcel']"}),
            'parking': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50'}),
            'pets': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50'}),
            'pool': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'recycling': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'renewable_energy': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'renewable_energy_detials': ('jsonfield.fields.JSONField', [], {'blank': 'True'}),
            'smart_living': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['source.Source']"}),
            'sqft': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'tag': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'transit_friendly': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'transit_friendly_detials': ('jsonfield.fields.JSONField', [], {'blank': 'True'}),
            'transit_score': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'walk_friendly': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'walk_friendly_detials': ('jsonfield.fields.JSONField', [], {'blank': 'True'}),
            'walk_score': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'website': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'building.buildingcomment': {
            'Meta': {'object_name': 'BuildingComment'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'building': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comments'", 'to': u"orm['building.Building']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'building.buildingdocument': {
            'Meta': {'object_name': 'BuildingDocument'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'blob_key': ('django.db.models.fields.TextField', [], {}),
            'building': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'documents'", 'to': u"orm['building.Building']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'documents'", 'null': 'True', 'to': u"orm['building.Unit']"})
        },
        u'building.buildingperson': {
            'Meta': {'object_name': 'BuildingPerson'},
            'building': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'people'", 'to': u"orm['building.Building']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['person.Person']"}),
            'relation': ('django.db.models.fields.CharField', [], {'default': "'Unknown'", 'max_length': '50'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['building.Unit']", 'null': 'True', 'blank': 'True'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'building.buildingphoto': {
            'Meta': {'object_name': 'BuildingPhoto'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'blob_key': ('django.db.models.fields.TextField', [], {}),
            'building': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'photos'", 'to': u"orm['building.Building']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'filename': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'photos'", 'null': 'True', 'to': u"orm['building.Unit']"})
        },
        u'building.changedetails': {
            'Meta': {'object_name': 'ChangeDetails'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'building': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'changes'", 'to': u"orm['building.Building']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'new_values': ('jsonfield.fields.JSONField', [], {}),
            'original_values': ('jsonfield.fields.JSONField', [], {}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'changes'", 'null': 'True', 'to': u"orm['building.Unit']"})
        },
        u'building.listing': {
            'Meta': {'object_name': 'Listing'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'available_end': ('django.db.models.fields.DateTimeField', [], {}),
            'available_start': ('django.db.models.fields.DateTimeField', [], {}),
            'building': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'listings'", 'null': 'True', 'to': u"orm['building.Building']"}),
            'cost': ('django.db.models.fields.FloatField', [], {}),
            'cost_cycle': ('django.db.models.fields.CharField', [], {'default': "'month'", 'max_length': '10'}),
            'deposit': ('django.db.models.fields.FloatField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lease_term': ('django.db.models.fields.CharField', [], {'default': "'12 Months'", 'max_length': '200'}),
            'lease_type': ('django.db.models.fields.CharField', [], {'default': "'Standard'", 'max_length': '200'}),
            'pets': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'listings'", 'to': u"orm['building.Unit']"}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
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
            'Meta': {'ordering': "['number']", 'object_name': 'Unit'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'bathrooms': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'bedrooms': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'building': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'units'", 'to': u"orm['building.Building']"}),
            'floor': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_occupants': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'sqft': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'tag': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'building.unittype': {
            'Meta': {'object_name': 'UnitType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
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
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'person.person': {
            'Meta': {'object_name': 'Person'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['city.City']", 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'website': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
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