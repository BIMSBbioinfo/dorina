# vim: set fileencoding=utf-8 :

import unittest
from os import path
from argparse import Namespace
from pybedtools import BedTool
from dorina import config
from dorina import utils
from dorina import run

datadir = path.join(path.dirname(path.abspath(__file__)), 'data')

class TestAnalyseWithoutOptions(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_analyse_all_regions_seta_single(self):
        """Test run.analyse() on all regions with a single regulator"""
        expected = [
            dict(track="scifi", gene="gene01.01", data_source='PARCLIP', score=5, site="scifi_cds",
                 location="chr1:250-260", strand="+"),
            dict(track="scifi", gene="gene01.02", data_source='PARCLIP', score=5, site="scifi_intron",
                 location="chr1:2350-2360", strand="+")
        ]
        got = run.analyse('hg19', set_a=['PARCLIP_scifi'], match_a='any', region_a='any', datadir=datadir)
        self.assertEqual(expected, got)

        got = run.analyse('hg19', set_a=['PARCLIP_scifi'], datadir=datadir)
        self.assertEqual(expected, got)

    def test_analyse_CDS_seta_single(self):
        """Test run.analyse() on CDS regions with a single regulator"""
        expected = [
            dict(track="scifi", gene="gene01.01", data_source='PARCLIP', score=5, site="scifi_cds",
                 location="chr1:250-260", strand="+")
        ]
        got = run.analyse('hg19', set_a=['PARCLIP_scifi'], match_a='any', region_a='CDS', datadir=datadir)
        self.assertEqual(expected, got)

        got = run.analyse('hg19', set_a=['PARCLIP_scifi'], region_a='CDS', datadir=datadir)
        self.assertEqual(expected, got)

    def test_analyse_intergenic_seta_single(self):
        """Test run.analyse() on intergenic regions with a single regulator"""
        expected = [
            dict(track="scifi", gene="intergenic01.01", data_source='PARCLIP', score=5, site="scifi_intergenic",
                 location="chr1:1250-1260", strand=".")
        ]
        got = run.analyse('hg19', set_a=['PARCLIP_scifi'], match_a='any', region_a='intergenic', datadir=datadir)
        self.assertEqual(expected, got)

        got = run.analyse('hg19', set_a=['PARCLIP_scifi'], region_a='intergenic', datadir=datadir)
        self.assertEqual(expected, got)

    def test_analyse_all_regions_seta_any(self):
        """Test run.analyse() on all regions with two regulators with match to any regulator"""
        expected = [
            dict(track="fake01", gene="gene01.01", data_source='miRNA', score=5, site="fake01_cds",
                 location="chr1:255-265", strand="+"),
            dict(track="fake02", gene="gene01.02", data_source='miRNA', score=5, site="fake02_intron",
                 location="chr1:2450-2460", strand="+")
        ]
        got = run.analyse('hg19', set_a=['miRNA_fake01', 'miRNA_fake02'], match_a='any', region_a='any', datadir=datadir)
        self.assertEqual(expected, got)

        got = run.analyse('hg19', set_a=['miRNA_fake01', 'miRNA_fake02'], datadir=datadir)
        self.assertEqual(expected, got)

    def test_analyse_all_regions_seta_all(self):
        """Test run.analyse() on all regions with two regulators with match to all regulators"""
        expected = [
            dict(track="scifi", gene="gene01.01", data_source='PARCLIP', score=5, site="scifi_cds",
                 location="chr1:250-260", strand="+"),
            dict(track="fake01", gene="gene01.01", data_source='miRNA', score=5, site="fake01_cds",
                 location="chr1:255-265", strand="+")
        ]
        got = run.analyse('hg19', set_a=['PARCLIP_scifi', 'miRNA_fake01'], match_a='all', region_a='any', datadir=datadir)
        self.assertEqual(expected, got)

        got = run.analyse('hg19', set_a=['PARCLIP_scifi', 'miRNA_fake01'], match_a='all', datadir=datadir)
        self.assertEqual(expected, got)

    def test_analyse_all_regions_seta_and_setb(self):
        """Test run.analyse() on all regions with any regulator from set A and any regulator from set B matching"""
        expected = [
            dict(track="scifi", gene="gene01.01", data_source='PARCLIP', score=5, site="scifi_cds",
                 location="chr1:250-260", strand="+"),
            dict(track="fake01", gene="gene01.01", data_source='miRNA', score=5, site="fake01_cds",
                 location="chr1:255-265", strand="+")
        ]
        got = run.analyse('hg19', set_a=['PARCLIP_scifi'], match_a='any', region_a='any',
                          set_b=['miRNA_fake01'], match_b='any', region_b='any',
                          combine='and', datadir=datadir)
        self.assertEqual(expected, got)

    def test_analyse_all_regions_seta_or_setb(self):
        """Test run.analyse() on all regions with any regulator from set A or any regulator from set B matching"""
        expected = [
            {'data_source': 'PARCLIP',
             'gene': 'gene01.01',
             'location': 'chr1:250-260',
             'score': 5,
             'site': 'scifi_cds',
             'strand': '+',
             'track': 'scifi'},
            {'data_source': 'PARCLIP',
             'gene': 'gene01.02',
             'location': 'chr1:2350-2360',
             'score': 5,
             'site': 'scifi_intron',
             'strand': '+',
             'track': 'scifi'},
            {'data_source': 'miRNA',
             'gene': 'gene01.01',
             'location': 'chr1:255-265',
             'score': 5,
             'site': 'fake01_cds',
             'strand': '+',
             'track': 'fake01'}
     ]
        got = run.analyse('hg19', set_a=['PARCLIP_scifi'], match_a='any', region_a='any',
                          set_b=['miRNA_fake01'], match_b='any', region_b='any',
                          combine='or', datadir=datadir)
        self.assertEqual(expected, got)

    def test_analyse_all_regions_seta_xor_setb(self):
        """Test run.analyse() on all regions with any regulator from set A XOR any regulator from set B matching"""
        expected = [
            {'data_source': 'PARCLIP',
             'gene': 'gene01.02',
             'location': 'chr1:2350-2360',
             'score': 5,
             'site': 'scifi_intron',
             'strand': '+',
             'track': 'scifi'}
        ]
        got = run.analyse('hg19', set_a=['PARCLIP_scifi'], match_a='any', region_a='any',
                          set_b=['miRNA_fake01'], match_b='any', region_b='any',
                          combine='xor', datadir=datadir)
        self.assertEqual(expected, got)

    def test_analyse_all_regions_seta_not_setb(self):
        """Test run.analyse() on all regions with any regulator from set A but no regulator from set B matching"""
        expected = [
            {'data_source': 'PARCLIP',
             'gene': 'gene01.02',
             'location': 'chr1:2350-2360',
             'score': 5,
             'site': 'scifi_intron',
             'strand': '+',
             'track': 'scifi'}
        ]
        got = run.analyse('hg19', set_a=['PARCLIP_scifi'], match_a='any', region_a='any',
                          set_b=['miRNA_fake01'], match_b='any', region_b='any',
                          combine='not', datadir=datadir)
        self.assertEqual(expected, got)

    def test_get_genome_bedtool(self):
        """Test run._get_genome_bedtool()"""
        # should raise a ValueError for an invalid region
        self.assertRaises(ValueError, run._get_genome_bedtool, 'hg19', 'invalid', datadir)

        expected = BedTool(path.join(utils.get_genome_by_name('hg19', datadir), 'all.gff'))
        got = run._get_genome_bedtool('hg19', 'any', datadir)
        self.assertEqual(expected, got)

        expected = BedTool(path.join(utils.get_genome_by_name('hg19', datadir), 'cds.gff'))
        got = run._get_genome_bedtool('hg19', 'CDS', datadir)
        self.assertEqual(expected, got)

        expected = BedTool(path.join(utils.get_genome_by_name('hg19', datadir), '3_utr.gff'))
        got = run._get_genome_bedtool('hg19', '3prime', datadir)
        self.assertEqual(expected, got)

        expected = BedTool(path.join(utils.get_genome_by_name('hg19', datadir), '5_utr.gff'))
        got = run._get_genome_bedtool('hg19', '5prime', datadir)
        self.assertEqual(expected, got)

        expected = BedTool(path.join(utils.get_genome_by_name('hg19', datadir), 'intron.gff'))
        got = run._get_genome_bedtool('hg19', 'intron', datadir)
        self.assertEqual(expected, got)

        expected = BedTool(path.join(utils.get_genome_by_name('hg19', datadir), 'intergenic.gff'))
        got = run._get_genome_bedtool('hg19', 'intergenic', datadir)
        self.assertEqual(expected, got)


    def test_get_regulator_bedtool(self):
        """Test run._get_regulator_bedtool()"""
        expected = BedTool('%s.bed' % utils.get_regulator_by_name('PARCLIP_scifi', datadir))
        got = run._get_regulator_bedtool('PARCLIP_scifi', datadir)
        self.assertEqual(expected, got)


    def test_cleanup_intersect_bed(self):
        """Test run._cleanup_intersect_bed()"""
        dirty_string = '''chr1	250	260	PARCLIP#scifi*scifi_cds	23	+	250	260	chr1	255	265	miRNA#fake01*fake01_cds	42	-	255	265'''
        dirty = BedTool(dirty_string, from_string=True)

        expected_string = '''chr1	255	260	PARCLIP#scifi*scifi_cds~miRNA#fake01*fake01_cds	23~42	.	250~255	260~265'''
        expected = BedTool(expected_string, from_string=True)

        got = run._cleanup_intersect_bed(dirty)
        self.assertEqual(expected, got)


    def test_cleanup_intersect_bed6(self):
        """Test run._cleanup_intersect_bed() with bed6 format files"""
        dirty_string = '''chr1	250	260	PARCLIP#scifi*scifi_cds	23	+	chr1	255	265	miRNA#fake01*fake01_cds	42	-'''
        dirty = BedTool(dirty_string, from_string=True)

        expected_string = '''chr1	255	260	PARCLIP#scifi*scifi_cds~miRNA#fake01*fake01_cds	23~42	.	250~255	260~265'''
        expected = BedTool(expected_string, from_string=True)

        got = run._cleanup_intersect_bed(dirty)
        self.assertEqual(str(expected), str(got))


    def test_cleanup_intersect_gff(self):
        """Test run._cleanup_intersect_gff()"""
        dirty_string = '''chr1	doRiNA2	gene	1	1000	.	+	.	ID=gene01.01 	chr1	255	260	PARCLIP#scifi*scifi_cds~miRNA#fake01*fake01_cds	23	.	250~255	260~265'''
        dirty = BedTool(dirty_string, from_string=True)

        expected_string = '''chr1	doRiNA2	gene	1	1000    .	+	.	ID=gene01.01;regulator=PARCLIP#scifi*scifi_cds~miRNA#fake01*fake01_cds;score=23;start=250~255;end=260~265'''
        expected = BedTool(expected_string, from_string=True)

        got = run._cleanup_intersect_gff(dirty)
        self.assertEqual(str(expected), str(got))


    def test_cleanup_intersect_gff_no_merged_bed6(self):
        """Test run._cleanup_intersect_gff()"""
        dirty_string = '''chr1	doRiNA2	gene	1	1000	.	+	.	ID=gene01.01 	chr1	250	260	PARCLIP#scifi*scifi_cds	23	.'''
        dirty = BedTool(dirty_string, from_string=True)

        expected_string = '''chr1	doRiNA2	gene	1	1000    .	+	.	ID=gene01.01;regulator=PARCLIP#scifi*scifi_cds;score=23;start=250;end=260'''
        expected = BedTool(expected_string, from_string=True)

        got = run._cleanup_intersect_gff(dirty)
        self.assertEqual(str(expected), str(got))


    def test_parse_results(self):
        """Test run._parse_results()"""
        given_string = '''chr1	doRiNA2	gene	1	1000    .	+	.	ID=gene01.01;regulator=PARCLIP#scifi*scifi_cds~miRNA#fake01*fake01_cds;score=23~42;start=250~255;end=260~265'''
        given = BedTool(given_string, from_string=True)

        expected = [
            dict(track="scifi", gene="gene01.01", data_source='PARCLIP', score=23, site="scifi_cds",
                 location="chr1:250-260", strand="+"),
            dict(track="fake01", gene="gene01.01", data_source='miRNA', score=42, site="fake01_cds",
                 location="chr1:255-265", strand="+")
        ]

        got = run._parse_results(given)

        self.assertEqual(expected, got)
