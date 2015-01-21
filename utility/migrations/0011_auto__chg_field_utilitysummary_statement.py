# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'UtilitySummary.statement'
        db.alter_column(u'utility_utilitysummary', 'statement_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['utility.Statement'], null=True))

    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'UtilitySummary.statement'
        raise RuntimeError("Cannot reverse this migration. 'UtilitySummary.statement' and its values cannot be restored.")

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
            'active_listings': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'air_conditioning': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'blank': 'True'}),
            'amenities': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'average_electricity': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'average_gas': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'average_sqft': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'average_trash': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'average_water': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'bike_friendly': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'bike_friendly_details': ('rentrocket.helpers.MultiSelectField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'bike_friendly_other': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'bike_score': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'built_year': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['city.City']"}),
            'composting': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'energy_average': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'energy_saving_details': ('rentrocket.helpers.MultiSelectField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'energy_saving_features': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'energy_saving_other': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'energy_score': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'estimated_total_max': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'estimated_total_min': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'game_room': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'garden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'garden_details': ('rentrocket.helpers.MultiSelectField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'garden_other': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'geocoder': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'gym': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'heat_source_details': ('django.db.models.fields.CharField', [], {'default': "'unknown'", 'max_length': '20', 'blank': 'True'}),
            'heat_source_other': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'laundry': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {}),
            'max_rent': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'max_rent_listing': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'min_rent': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'min_rent_listing': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '80', 'blank': 'True'}),
            'number_of_units': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'parcel': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['building.Parcel']"}),
            'parking_options': ('rentrocket.helpers.MultiSelectField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'pets': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'pets_options': ('rentrocket.helpers.MultiSelectField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'pets_other': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'pool': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'recycling': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'renewable_energy': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'renewable_energy_details': ('rentrocket.helpers.MultiSelectField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'renewable_energy_other': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'smart_living': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['source.Source']", 'null': 'True', 'blank': 'True'}),
            'sqft': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '2'}),
            'tag': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'total_average': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'transit_friendly': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'transit_friendly_details': ('rentrocket.helpers.MultiSelectField', [], {'default': "''", 'max_length': '100', 'blank': 'True'}),
            'transit_friendly_other': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'transit_score': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'utility_data_updated': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'walk_friendly': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'walk_friendly_details': ('rentrocket.helpers.MultiSelectField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'walk_friendly_other': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'walk_score': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'website': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'who_pays_cable': ('django.db.models.fields.CharField', [], {'default': "'unknown'", 'max_length': '20'}),
            'who_pays_electricity': ('django.db.models.fields.CharField', [], {'default': "'unknown'", 'max_length': '20'}),
            'who_pays_gas': ('django.db.models.fields.CharField', [], {'default': "'unknown'", 'max_length': '20'}),
            'who_pays_internet': ('django.db.models.fields.CharField', [], {'default': "'unknown'", 'max_length': '20'}),
            'who_pays_trash': ('django.db.models.fields.CharField', [], {'default': "'unknown'", 'max_length': '20'}),
            'who_pays_water': ('django.db.models.fields.CharField', [], {'default': "'unknown'", 'max_length': '20'})
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
            'Meta': {'ordering': "['number']", 'object_name': 'Unit'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'address': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'average_electricity': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'average_gas': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'average_trash': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'average_water': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'bathrooms': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'bedrooms': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'building': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'units'", 'to': u"orm['building.Building']"}),
            'deposit': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'electricity_max': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'electricity_min': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'energy_average': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'energy_score': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'floor': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'gas_max': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'gas_min': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_occupants': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'rent': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'sqft': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'unknown'", 'max_length': '20', 'blank': 'True'}),
            'tag': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'visible': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
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
            'phone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '20', 'blank': 'True'}),
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
        },
        u'utility.cityserviceprovider': {
            'Meta': {'object_name': 'CityServiceProvider'},
            'city': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['city.City']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'provider': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['utility.ServiceProvider']"}),
            'website': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'utility.serviceprovider': {
            'Meta': {'object_name': 'ServiceProvider'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instructions': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'website': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        u'utility.serviceutility': {
            'Meta': {'object_name': 'ServiceUtility'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'provider': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'utilities'", 'to': u"orm['utility.ServiceProvider']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'utility.statement': {
            'Meta': {'object_name': 'Statement'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'blob_key': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39'}),
            'processed': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'processed_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'processed_statements'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'electricity'", 'max_length': '12'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['building.Unit']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'vendor': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
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
            'person_email': ('django.db.models.fields.EmailField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'processed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'electricity'", 'max_length': '12'}),
            'unit_details': ('jsonfield.fields.JSONField', [], {'blank': 'True'}),
            'unit_number': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'vendor': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        },
        u'utility.utilitysummary': {
            'Meta': {'object_name': 'UtilitySummary'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'amount': ('django.db.models.fields.FloatField', [], {'blank': 'True'}),
            'building': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['building.Building']"}),
            'cost': ('django.db.models.fields.FloatField', [], {'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'provider': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['utility.ServiceProvider']", 'null': 'True', 'blank': 'True'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['source.Source']", 'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateTimeField', [], {}),
            'statement': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['utility.Statement']", 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'electricity'", 'max_length': '12'}),
            'unit': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['building.Unit']"}),
            'unit_of_measurement': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'vendor': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'})
        }
    }

    complete_apps = ['utility']