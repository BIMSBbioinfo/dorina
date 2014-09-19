# vim: set fileencoding=utf-8 :

import unittest
from os import path
from argparse import Namespace
from dorina import config
from dorina import utils

datadir = path.join(path.dirname(path.abspath(__file__)), 'data')

class TestListDataWithoutOptions(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None


    def test_get_genomes(self):
        """Test utils.get_genomes()"""
        expected = {
            'h_sapiens': {
                'id': 'h_sapiens',
                'label': 'Human',
                'scientific': 'Homo sapiens',
                'weight': 10,
                'assemblies': {
                    'hg19': {
                        'all': True,
                        'cds': True,
                        '3_utr': True,
                        '5_utr': True,
                        'intron': True,
                        'intergenic': True
                    }
                }
            }
        }

        got = utils.get_genomes(datadir=datadir)
        self.assertEqual(expected, got)


    def test_get_regulators(self):
        """Test utils.get_regulators()"""
        basedir = path.join(datadir, 'regulators', 'h_sapiens', 'hg19')
        scifi_path = path.join(datadir, basedir, 'PARCLIP_scifi.json')
        scifi = utils.parse_experiment(scifi_path)[0]
        scifi['file'] = scifi_path
        fake_path = path.join(datadir, basedir, 'PICTAR_fake.json')
        experiments = utils.parse_experiment(fake_path)
        for exp in experiments:
            exp['file'] = fake_path

        expected = {
            'h_sapiens': {
                'hg19': {
                    'PARCLIP_scifi': scifi,
                    'PICTAR_fake01': experiments[0],
                    'PICTAR_fake02': experiments[1],
                    'PICTAR_fake023': experiments[2],
                    'fake024|Pictar': experiments[3]
                }
            }
        }

        got = utils.get_regulators(datadir=datadir)
        self.maxDiff = None
        self.assertEqual(expected, got)


    def test_parse_experiment(self):
        """Test utils.parse_experiment()"""
        expected = [{
            'id': 'PARCLIP_scifi',
            'experiment': 'PARCLIP',
            'summary': 'Experimental summary',
            'description': 'Long description here',
            'methods': 'Experimental methods section',
            'credits': 'Credits',
            'references': [
                { 'title': 'A very important publication',
                  'authors': ['Jules Verne', 'Orson Wells'],
                  'pages': '23-42', 'journal': 'Annals of Science Fiction',
                  'year': '1870',
                  'pubmed': 'http://www.ncbi.nlm.nih.gov/pubmed/12345678'
                }
            ]
        }]

        basedir = path.join(datadir, 'regulators', 'h_sapiens', 'hg19')
        got = utils.parse_experiment(path.join(datadir, basedir, 'PARCLIP_scifi.json'))
        self.assertEqual(expected, got)


    def test_get_genome_by_name(self):
        """Test utils.get_genome_by_name()"""
        got = utils.get_genome_by_name("invalid", datadir=datadir)
        self.assertIsNone(got)

        expected = path.join(datadir, 'genomes', 'h_sapiens', 'hg19')
        got = utils.get_genome_by_name("hg19", datadir=datadir)
        self.assertEqual(expected, got)


    def test_get_regulator_by_name(self):
        """Test utils.get_regulator_by_name()"""
        got = utils.get_regulator_by_name("invalid", datadir=datadir)
        self.assertIsNone(got)

        expected = path.join(datadir, 'regulators', 'h_sapiens', 'hg19', 'PARCLIP_scifi')
        got = utils.get_regulator_by_name("PARCLIP_scifi", datadir=datadir)
        self.assertEqual(expected, got)

        expected = path.join(datadir, 'regulators', 'h_sapiens', 'hg19', 'PICTAR_fake')
        got = utils.get_regulator_by_name("PICTAR_fake02", datadir=datadir)
        self.assertEqual(expected, got)

        expected = path.join(datadir, 'manual')
        got = utils.get_regulator_by_name(expected, datadir)
        self.assertEqual(expected, got)
