# -*- coding: utf-8 -*-

from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Indexadores'
        db.create_table('modelagem_indexadores', (
            ('id', self.gf('django.db.models.fields.AutoField')(
                primary_key=True)),
            ('party_term', self.gf('django.db.models.fields.CharField')(
                max_length=120)),
            ('principa_party_term', self.gf('django.db.models.fields.BooleanField')(
                default=False)),
        ))
        db.send_create_signal('modelagem', ['Indexadores'])

        # Adding model 'Partido'
        db.create_table('modelagem_partido', (
            ('id', self.gf('django.db.models.fields.AutoField')(
                primary_key=True)),
            ('party_name', self.gf('django.db.models.fields.CharField')(
                max_length=12)),
            ('party_number', self.gf('django.db.models.fields.IntegerField')()),
            ('party_color', self.gf('django.db.models.fields.CharField')(
                max_length=7)),
        ))
        db.send_create_signal('modelagem', ['Partido'])

        # Adding model 'CasaLegislativa'
        db.create_table('modelagem_casalegislativa', (
            ('id', self.gf('django.db.models.fields.AutoField')(
                primary_key=True)),
            ('legislative_house_name', self.gf('django.db.models.fields.CharField')(
                max_length=100)),
            ('acronym_legislative_house', self.gf('django.db.models.fields.CharField')
             (unique=True, max_length=50)),
            ('sphere', self.gf('django.db.models.fields.CharField')
                (max_length=10)),
            ('legislative_house_place', self.gf('django.db.models.fields.CharField')
                (max_length=100)),
            ('db_atualization_date', self.gf('django.db.models.fields.DateField')
             (null=True, blank=True)),
        ))
        db.send_create_signal('modelagem', ['CasaLegislativa'])

        # Adding model 'Parlamentar'
        db.create_table('modelagem_parlamentar', (
            ('id', self.gf('django.db.models.fields.AutoField')
                (primary_key=True)),
            ('parliamentary_id', self.gf('django.db.models.fields.CharField')
             (max_length=100, blank=True)),
            ('parliamentary_name', self.gf('django.db.models.fields.CharField')
                (max_length=100)),
            ('parliamentary_gender', self.gf('django.db.models.fields.CharField')
             (max_length=10, blank=True)),
        ))
        db.send_create_signal('modelagem', ['Parlamentar'])

        # Adding model 'Legislatura'
        db.create_table('modelagem_legislatura', (
            ('id', self.gf('django.db.models.fields.AutoField')
                (primary_key=True)),
            ('parliamentary', self.gf(
                'django.db.models.fields.related.ForeignKey')
             (to=orm['modelagem.Parlamentar'])),
            ('lesgilative_house', self.gf(
                'django.db.models.fields.related.ForeignKey')
             (to=orm['modelagem.CasaLegislativa'], null=True)),
            ('lesgilature_initial_date', self.gf('django.db.models.fields.DateField')
                (null=True)),
            ('lesgilature_final_date', self.gf('django.db.models.fields.DateField')(null=True)),
            ('party', self.gf('django.db.models.fields.related.ForeignKey')
             (to=orm['modelagem.Partido'])),
            ('legislature_place', self.gf('django.db.models.fields.CharField')
             (max_length=100, blank=True)),
        ))
        db.send_create_signal('modelagem', ['Legislatura'])

        # Adding model 'Proposicao'
        db.create_table('modelagem_proposicao', (
            ('id', self.gf('django.db.models.fields.AutoField')
                (primary_key=True)),
            ('proposition_id', self.gf('django.db.models.fields.CharField')
             (max_length=100, blank=True)),
            ('proposition_acronym', self.gf('django.db.models.fields.CharField')
                (max_length=10)),
            ('proposition_number', self.gf('django.db.models.fields.CharField')
                (max_length=10)),
            ('proposition_year', self.gf('django.db.models.fields.CharField')
                (max_length=4)),
            ('proposition_menu', self.gf('django.db.models.fields.TextField')
                (blank=True)),
            ('proposition_description', self.gf('django.db.models.fields.TextField')
                (blank=True)),
            ('proposition_index', self.gf('django.db.models.fields.TextField')
                (blank=True)),
            ('proposition_date', self.gf(
                'django.db.models.fields.DateField')(null=True)),
            ('proposition_status', self.gf('django.db.models.fields.TextField')
                (blank=True)),
            ('lesgilative_house', self.gf(
                'django.db.models.fields.related.ForeignKey')
             (to=orm['modelagem.CasaLegislativa'], null=True)),
            ('principal_author', self.gf(
                'django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('modelagem', ['Proposicao'])

        # Adding M2M table for field autores on 'Proposicao'
        m2m_table_name = db.shorten_name('modelagem_proposicao_autores')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True,
                                    auto_created=True)),
            ('proposicao', models.ForeignKey(
                orm['modelagem.proposicao'], null=False)),
            ('parlamentar', models.ForeignKey(
                orm['modelagem.parlamentar'], null=False))
        ))
        db.create_unique(m2m_table_name, ['proposition_id', 'parliamentary_id'])

        # Adding model 'Votacao'
        db.create_table('modelagem_votacao', (
            ('id', self.gf('django.db.models.fields.AutoField')
                (primary_key=True)),
            ('voting_id', self.gf('django.db.models.fields.CharField')
             (max_length=100, blank=True)),
            ('voting_description', self.gf('django.db.models.fields.TextField')
                (blank=True)),
            ('voting_date', self.gf('django.db.models.fields.DateField')
             (null=True, blank=True)),
            ('voting_result', self.gf('django.db.models.fields.TextField')
                (blank=True)),
            ('propositon_voted', self.gf(
                'django.db.models.fields.related.ForeignKey')
             (to=orm['modelagem.Proposicao'], null=True)),
        ))
        db.send_create_signal('modelagem', ['Votacao'])

        # Adding model 'Voto'
        db.create_table('modelagem_voto', (
            ('id', self.gf('django.db.models.fields.AutoField')
                (primary_key=True)),
            ('voting', self.gf('django.db.models.fields.related.ForeignKey')
             (to=orm['modelagem.Votacao'])),
            ('legislature', self.gf(
                'django.db.models.fields.related.ForeignKey')
             (to=orm['modelagem.Legislatura'])),
            ('vote_option', self.gf('django.db.models.fields.CharField')
                (max_length=10)),
        ))
        db.send_create_signal('modelagem', ['Voto'])

    def backwards(self, orm):
        # Deleting model 'Indexadores'
        db.delete_table('modelagem_indexadores')

        # Deleting model 'Partido'
        db.delete_table('modelagem_partido')

        # Deleting model 'CasaLegislativa'
        db.delete_table('modelagem_casalegislativa')

        # Deleting model 'Parlamentar'
        db.delete_table('modelagem_parlamentar')

        # Deleting model 'Legislatura'
        db.delete_table('modelagem_legislatura')

        # Deleting model 'Proposicao'
        db.delete_table('modelagem_proposicao')

        # Removing M2M table for field autores on 'Proposicao'
        db.delete_table(db.shorten_name('modelagem_proposicao_autores'))

        # Deleting model 'Votacao'
        db.delete_table('modelagem_votacao')

        # Deleting model 'Voto'
        db.delete_table('modelagem_voto')

    models = {
        'modelagem.casalegislativa': {
            'Meta': {'object_name': 'CasaLegislativa'},
            'db_atualization_date': ('django.db.models.fields.DateField', [],
             {'null': 'True', 'blank': 'True'}),
            'sphere': ('django.db.models.fields.CharField', [],
                       {'max_length': '10'}),
            'id': ('django.db.models.fields.AutoField', [],
                   {'primary_key': 'True'}),
            'legislative_house_place': ('django.db.models.fields.CharField', [],
                      {'max_length': '100'}),
            'legislative_house_name': ('django.db.models.fields.CharField', [],
                     {'max_length': '100'}),
            'acronym_legislative_house': ('django.db.models.fields.CharField', [],
                           {'unique': 'True', 'max_length': '50'})
        },
        'modelagem.indexadores': {
            'Meta': {'object_name': 'Indexadores'},
            'id': ('django.db.models.fields.AutoField', [],
                   {'primary_key': 'True'}),
            'principa_party_term': ('django.db.models.fields.BooleanField', [],
                          {'default': 'False'}),
            'party_term': ('django.db.models.fields.CharField', [],
                      {'max_length': '120'})
        },
        'modelagem.legislatura': {
            'Meta': {'object_name': 'Legislatura'},
            'lesgilative_house': ('django.db.models.fields.related.ForeignKey',
                                 [],
                                 {'to': "orm['modelagem.CasaLegislativa']",
                                  'null': 'True'}),
            'lesgilature_final_date': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [],
                   {'primary_key': 'True'}),
            'lesgilature_initial_date': ('django.db.models.fields.DateField', [],
                       {'null': 'True'}),
            'legislature_place': ('django.db.models.fields.CharField', [],
                           {'max_length': '100', 'blank': 'True'}),
            'parliamentary': ('django.db.models.fields.related.ForeignKey', [],
                            {'to': "orm['modelagem.Parlamentar']"}),
            'party': ('django.db.models.fields.related.ForeignKey', [],
                        {'to': "orm['modelagem.Partido']"})
        },
        'modelagem.parlamentar': {
            'Meta': {'object_name': 'Parlamentar'},
            'parliamentary_gender': ('django.db.models.fields.CharField', [],
                       {'max_length': '10', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [],
                   {'primary_key': 'True'}),
            'parliamentary_id': ('django.db.models.fields.CharField', [],
                               {'max_length': '100', 'blank': 'True'}),
            'parliamentary_name': ('django.db.models.fields.CharField', [],
                     {'max_length': '100'})
        },
        'modelagem.partido': {
            'Meta': {'object_name': 'Partido'},
            'party_color': ('django.db.models.fields.CharField', [],
                    {'max_length': '7'}),
            'id': ('django.db.models.fields.AutoField', [],
                   {'primary_key': 'True'}),
            'party_name': ('django.db.models.fields.CharField', [],
                     {'max_length': '12'}),
            'party_number': ('django.db.models.fields.IntegerField', [], {})
        },
        'modelagem.proposicao': {
            'Meta': {'object_name': 'Proposicao'},
            'proposition_year': ('django.db.models.fields.CharField', [],
                    {'max_length': '4'}),
            'principal_author': ('django.db.models.fields.TextField', [],
                                {'blank': 'True'}),
            'authors': ('django.db.models.fields.related.ManyToManyField', [],
                        {'symmetrical': 'False',
                         'related_name': "u'demais_autores'",
                         'null': 'True',
                         'to': "orm['modelagem.Parlamentar']"}),
            'lesgilative_house': ('django.db.models.fields.related.ForeignKey',
                                 [], {'to': "orm['modelagem.CasaLegislativa']",
                                      'null': 'True'}),
            'proposition_date': ('django.db.models.fields.DateField', [],
                                  {'null': 'True'}),
            'proposition_description': ('django.db.models.fields.TextField', [],
                          {'blank': 'True'}),
            'proposition_menu': ('django.db.models.fields.TextField', [],
                       {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [],
                   {'primary_key': 'True'}),
            'proposition_id': ('django.db.models.fields.CharField', [],
                        {'max_length': '100', 'blank': 'True'}),
            'proposition_index': ('django.db.models.fields.TextField', [],
                          {'blank': 'True'}),
            'proposition_number': ('django.db.models.fields.CharField', [],
                       {'max_length': '10'}),
            'proposition_acronym': ('django.db.models.fields.CharField', [],
                      {'max_length': '10'}),
            'proposition_status': ('django.db.models.fields.TextField', [],
                         {'blank': 'True'})
        },
        'modelagem.votacao': {
            'Meta': {'object_name': 'Votacao'},
            'voting_date': ('django.db.models.fields.DateField', [],
                     {'null': 'True', 'blank': 'True'}),
            'voting_description': ('django.db.models.fields.TextField', [],
                          {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [],
                   {'primary_key': 'True'}),
            'voting_id': ('django.db.models.fields.CharField', [],
                       {'max_length': '100', 'blank': 'True'}),
            'propositon_voted': ('django.db.models.fields.related.ForeignKey', [],
                           {'to': "orm['modelagem.Proposicao']",
                            'null': 'True'}),
            'voting_result': ('django.db.models.fields.TextField', [],
                          {'blank': 'True'})
        },
        'modelagem.voto': {
            'Meta': {'object_name': 'Voto'},
            'id': ('django.db.models.fields.AutoField', [],
                   {'primary_key': 'True'}),
            'legislature': ('django.db.models.fields.related.ForeignKey', [],
                            {'to': "orm['modelagem.Legislatura']"}),
            'voting_option': ('django.db.models.fields.CharField', [],
                      {'max_length': '10'}),
            'voting': ('django.db.models.fields.related.ForeignKey', [],
                        {'to': "orm['modelagem.Votacao']"})
        }
    }

    complete_apps = ['modelagem']
