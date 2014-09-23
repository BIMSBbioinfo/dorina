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
        bed_str = """chr1   doRiNA2 gene    1   1000    .   +   .   ID=gene01.01    chr1    250 260 PARCLIP#scifi*scifi_cds 5   +
        chr1    doRiNA2 gene    2001    3000    .   +   .   ID=gene01.02    chr1    2350    2360    PARCLIP#scifi*scifi_intron  5   +"""
        expected = BedTool(bed_str, from_string=True)
        got = run.analyse('hg19', set_a=['PARCLIP_scifi'], match_a='any', region_a='any', datadir=datadir)
        self.assertEqual(expected, got)

        got = run.analyse('hg19', set_a=['PARCLIP_scifi'], datadir=datadir)
        self.assertEqual(expected, got)

    def test_analyse_CDS_seta_single(self):
        """Test run.analyse() on CDS regions with a single regulator"""
        bed_str = """chr1   doRiNA2 CDS 201 300 .   +   0   ID=gene01.01    chr1    250 260 PARCLIP#scifi*scifi_cds 5   +"""
        expected = BedTool(bed_str, from_string=True)
        got = run.analyse('hg19', set_a=['PARCLIP_scifi'], match_a='any', region_a='CDS', datadir=datadir)
        self.assertEqual(expected, got)

        got = run.analyse('hg19', set_a=['PARCLIP_scifi'], region_a='CDS', datadir=datadir)
        self.assertEqual(expected, got)

    def test_analyse_intergenic_seta_single(self):
        """Test run.analyse() on intergenic regions with a single regulator"""
        bed_str = """chr1   doRiNA2 intergenic  1001    2000    .   .   .   ID=intergenic01.01  chr1    1250    1260    PARCLIP#scifi*scifi_intergenic  5   ."""
        expected = BedTool(bed_str, from_string=True)
        got = run.analyse('hg19', set_a=['PARCLIP_scifi'], match_a='any', region_a='intergenic', datadir=datadir)
        self.assertEqual(expected, got)

        got = run.analyse('hg19', set_a=['PARCLIP_scifi'], region_a='intergenic', datadir=datadir)
        self.assertEqual(expected, got)

    def test_analyse_all_regions_seta_any(self):
        """Test run.analyse() on all regions with two regulators with match to any regulator"""
        bed_str = """chr1   doRiNA2 gene    1   1000    .   +   .   ID=gene01.01    chr1    255 265 PICTAR#fake01*fake01_cds    5   +
        chr1    doRiNA2 gene    2001    3000    .   +   .   ID=gene01.02    chr1    2450    2460    PICTAR#fake02*fake02_intron 5   +"""
        expected = BedTool(bed_str, from_string=True)
        got = run.analyse('hg19', set_a=['PICTAR_fake01', 'PICTAR_fake02'], match_a='any', region_a='any', datadir=datadir)
        self.assertMultiLineEqual(str(expected), str(got))

        got = run.analyse('hg19', set_a=['PICTAR_fake01', 'PICTAR_fake02'], datadir=datadir)
        self.assertEqual(expected, got)

    def test_analyse_all_regions_seta_all(self):
        """Test run.analyse() on all regions with two regulators with match to all regulators"""
        bed_str = """chr1   doRiNA2 gene    1   1000    .   +   .   ID=gene01.01    chr1    250 260 PARCLIP#scifi*scifi_cds 5   +
        chr1    doRiNA2 gene    1   1000    .   +   .   ID=gene01.01    chr1    255 265 PICTAR#fake01*fake01_cds    5   +"""
        expected = BedTool(bed_str, from_string=True)
        got = run.analyse('hg19', set_a=['PARCLIP_scifi', 'PICTAR_fake01'], match_a='all', region_a='any', datadir=datadir)
        self.assertMultiLineEqual(str(expected), str(got))

        got = run.analyse('hg19', set_a=['PARCLIP_scifi', 'PICTAR_fake01'], match_a='all', datadir=datadir)
        self.assertEqual(expected, got)

    def test_analyse_all_regions_seta_and_setb(self):
        """Test run.analyse() on all regions with any regulator from set A and any regulator from set B matching"""
        bed_str = """chr1   doRiNA2 gene    1   1000    .   +   .   ID=gene01.01    chr1    250 260 PARCLIP#scifi*scifi_cds 5   +
        chr1    doRiNA2 gene    1   1000    .   +   .   ID=gene01.01    chr1    255 265 PICTAR#fake01*fake01_cds    5   +"""
        expected = BedTool(bed_str, from_string=True)
        got = run.analyse('hg19', set_a=['PARCLIP_scifi'], match_a='any', region_a='any',
                          set_b=['PICTAR_fake01'], match_b='any', region_b='any',
                          combine='and', datadir=datadir)
        self.assertMultiLineEqual(str(expected), str(got))

    def test_analyse_all_regions_seta_or_setb(self):
        """Test run.analyse() on all regions with any regulator from set A or any regulator from set B matching"""
        bed_str = """chr1   doRiNA2 gene    1   1000    .   +   .   ID=gene01.01    chr1    250 260 PARCLIP#scifi*scifi_cds 5   +
        chr1    doRiNA2 gene    1   1000    .   +   .   ID=gene01.01    chr1    255 265 PICTAR#fake01*fake01_cds    5   +
        chr1    doRiNA2 gene    2001    3000    .   +   .   ID=gene01.02    chr1    2350    2360    PARCLIP#scifi*scifi_intron  5   +
        chr1    doRiNA2 gene    1   1000    .   +   .   ID=gene01.01    chr1    250 260 PARCLIP#scifi*scifi_cds 5   +
        chr1    doRiNA2 gene    1   1000    .   +   .   ID=gene01.01    chr1    255 265 PICTAR#fake01*fake01_cds    5   +"""
        expected = BedTool(bed_str, from_string=True)
        got = run.analyse('hg19', set_a=['PARCLIP_scifi'], match_a='any', region_a='any',
                          set_b=['PICTAR_fake01'], match_b='any', region_b='any',
                          combine='or', datadir=datadir)
        self.assertMultiLineEqual(str(expected), str(got))

    def test_analyse_all_regions_seta_xor_setb(self):
        """Test run.analyse() on all regions with any regulator from set A XOR any regulator from set B matching"""
        bed_str = """chr1   doRiNA2 gene    2001    3000    .   +   .   ID=gene01.02    chr1    2350    2360    PARCLIP#scifi*scifi_intron  5   +"""
        expected = BedTool(bed_str, from_string=True)
        got = run.analyse('hg19', set_a=['PARCLIP_scifi'], match_a='any', region_a='any',
                          set_b=['PICTAR_fake01'], match_b='any', region_b='any',
                          combine='xor', datadir=datadir)
        self.assertMultiLineEqual(str(expected), str(got))

    def test_analyse_all_regions_seta_not_setb(self):
        """Test run.analyse() on all regions with any regulator from set A but no regulator from set B matching"""
        bed_str = """chr1   doRiNA2 gene    2001    3000    .   +   .   ID=gene01.02    chr1    2350    2360    PARCLIP#scifi*scifi_intron  5   +"""
        expected = BedTool(bed_str, from_string=True)
        got = run.analyse('hg19', set_a=['PARCLIP_scifi'], match_a='any', region_a='any',
                          set_b=['PICTAR_fake01'], match_b='any', region_b='any',
                          combine='not', datadir=datadir)
        self.assertMultiLineEqual(str(expected), str(got))


    def test_analyse_all_regions_seta_windowed(self):
        """Test run.analyse() on all regions with all regulators from set A matching in an overlapping window"""
        bed_str = """chr1	doRiNA2	gene	250	260 .	+	.	ID=gene01.01	chr1	250	260	PARCLIP#scifi*scifi_cds	5	+
chr1	doRiNA2	gene	250	260	.	+	.	ID=gene01.01	chr1	255	265	PICTAR#fake01*fake01_cds	5	+"""
        expected = BedTool(bed_str, from_string=True)
        got = run.analyse('hg19', set_a=['PARCLIP_scifi', 'PICTAR_fake01'], match_a='all', region_a='any',
                          window_a=0, datadir=datadir)
        self.assertMultiLineEqual(str(expected), str(got))


    def test_analyse_all_regions_seta_windowed_slop(self):
        """Test run.analyse() on all regions with all regulators from set A matching in an overlapping window with slop"""
        bed_str = """chr1	doRiNA2	gene    1	1260	.	+	.	ID=gene01.01	chr1	250	260	PARCLIP#scifi*scifi_cds	5	+
chr1	doRiNA2	gene	1	1260	.	+	.	ID=gene01.01	chr1	1250	1260	PARCLIP#scifi*scifi_intergenic	5	.
chr1	doRiNA2	gene	1	1260	.	+	.	ID=gene01.01	chr1	255	265	PICTAR#fake01*fake01_cds	5	+
chr1	doRiNA2	gene	1350	3360	.	+	.	ID=gene01.02	chr1	2350	2360	PARCLIP#scifi*scifi_intron	5	+
chr1	doRiNA2	gene	1350	3360	.	+	.	ID=gene01.02	chr1	1350	1360	PICTAR#fake01*fake01_intergenic	5	."""
        expected = BedTool(bed_str, from_string=True)
        got = run.analyse('hg19', set_a=['PARCLIP_scifi', 'PICTAR_fake01'], match_a='all', region_a='any',
                          window_a=1000, datadir=datadir)
        self.assertMultiLineEqual(str(expected), str(got))


    def test_add_slop(self):
        """Test run._add_slop()"""
        slop_string = """chr1   0   560 PARCLIP#scifi*scifi_cds 5   +
        chr1    950 1560    PARCLIP#scifi*scifi_intergenic  5   .
        chr1    2050    2660    PARCLIP#scifi*scifi_intron  5   +
"""
        expected = BedTool(slop_string, from_string=True)
        got = run._add_slop(BedTool(run._get_regulator_bedtool('PARCLIP_scifi', datadir)),
                            'hg19', 300, datadir)
        self.assertEqual(expected, got)

    def test_get_genome_chromfile(self):
        """Test run._get_genome_chromfile()"""
        expected = path.join(utils.get_genome_by_name('hg19', datadir=datadir), 'hg19.genome')
        got = run._get_genome_chromfile('hg19', datadir=datadir)
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

        expected = BedTool(path.join(utils.get_genome_by_name('hg19', datadir), 'all.gff')).filter(
                lambda x: x.name == "gene01.02").saveas()
        got = run._get_genome_bedtool('hg19', 'any', datadir, genes=['gene01.02'])
        self.assertEqual(expected, got)


    def test_get_regulator_bedtool(self):
        """Test run._get_regulator_bedtool()"""
        expected = BedTool('%s.bed' % utils.get_regulator_by_name('PARCLIP_scifi', datadir)).bed6()
        got = run._get_regulator_bedtool('PARCLIP_scifi', datadir)
        self.assertEqual(expected, got)

        manual = path.join(datadir, 'manual.bed')
        expected = BedTool(manual).bed6()
        got = run._get_regulator_bedtool(manual, datadir)
        self.assertEqual(expected, got)
