# vim: set fileencoding=utf-8 :

import logging
from os import path
from cStringIO import StringIO
from pybedtools import BedTool
from dorina import utils


def analyse(genome, set_a, match_a='any', region_a='any',
            set_b=None, match_b='any', region_b='any',
            combine='or', datadir=None):
    """Run doRiNA analysis"""
    logging.debug("analyse(%r, %r(%s))" % (genome, set_a, match_a))

    return _parse_results(_analyse(genome, set_a, match_a, region_a,
                                   set_b, match_b, region_b, combine, datadir))


def _analyse(genome, set_a, match_a='any', region_a='any',
             set_b=None, match_b='any', region_b='any', combine='or', datadir=None):
    """Run doRiNA analysis, internal logic"""
    logging.debug("analyse(%r, %r(%s))" % (genome, set_a, match_a))

    genome_bed_a = _get_genome_bedtool(genome, region_a, datadir)
    regulators_a = map(lambda x: _get_regulator_bedtool(x, datadir), set_a)

    if match_a == 'any':
        regulator = _merge_regulators(regulators_a)
    elif match_a == 'all':
        regulator = _intersect_regulators(regulators_a)

    result_a = _cleanup_intersect_gff(genome_bed_a.intersect(regulator, wa=True, wb=True))

    if set_b is not None:
        genome_bed_b = _get_genome_bedtool(genome, region_b, datadir)
        regulators_b = map(lambda x: _get_regulator_bedtool(x, datadir), set_b)

        if match_b == 'any':
            regulator = _merge_regulators(regulators_b)
        elif match_b == 'all':
            regulator = _intersect_regulators(regulators_b)

        result_b = _cleanup_intersect_gff(genome_bed_b.intersect(regulator, wa=True, wb=True))

        if combine == 'or':
            final_results = _merge_regulators([result_a, result_b])
        elif combine == 'and':
            final_results = _cleanup_intersect_gff_gff(result_a.intersect(result_b, wa=True, wb=True))
        elif combine == 'xor':
            not_in_b = result_a.intersect(result_b, v=True, wa=True)
            not_in_a = result_b.intersect(result_a, v=True, wa=True)
            final_results = _merge_regulators([not_in_b, not_in_a])
        elif combine == 'not':
            final_results = result_a.intersect(result_b, v=True, wa=True)

    else:
        final_results = result_a

    return final_results

def _merge_regulators(regulators):
    """Merge a list of regulators using BedTool.cat"""
    regulator = regulators[0]
    for i in range(1, len(regulators)):
        logging.debug('merging regulator %r' % regulators[i])
        regulator = regulator.cat(regulators[i], postmerge=False)

    return regulator


def _intersect_regulators(regulators):
    """Intersect a list of regulators using BedTool.intersect"""
    regulator = regulators[0]
    for i in range(1, len(regulators)):
        logging.debug('intersect regulator %r' % regulators[i])
        dirty_reg = regulator.intersect(regulators[i], wa=True, wb=True)
        regulator = _cleanup_intersect_bed(dirty_reg)

    return regulator


def _cleanup_intersect_bed(dirty):
    clean_string = ''
    for row in dirty:
        try:
            # Bed9 format?
            new_start = "%s" % max(int(row[1]), int(row[9]))
            new_end = "%s" % min(int(row[2]), int(row[10]))
            new_name = "~".join([row[3], row[11]])
            new_score = "%s" % ((int(row[4]) + int(row[12])) // 2)
            new_strand = row[5] if row[5] == row[13] else '.'
        except ValueError:
            # Try bed6 instead
            new_start = "%s" % max(int(row[1]), int(row[7]))
            new_end = "%s" % min(int(row[2]), int(row[8]))
            new_name = "~".join([row[3], row[9]])
            new_score = "%s" % ((int(row[4]) + int(row[10])) // 2)
            new_strand = row[5] if row[5] == row[11] else '.'

        new_row = "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{1}\t{2}\n".format(
            row[0], new_start, new_end, new_name, new_score, new_strand)
        clean_string += new_row

    return BedTool(clean_string, from_string=True)


def _cleanup_intersect_gff(dirty):
    clean_string = ''
    for row in dirty:
        new_row = "\t".join(row[:8])
        new_row += "\t{0};regulator={1};score={2};start={3};end={4}\n".format(row[8],
            row[12], row[13], row[10], row[11])
        clean_string += new_row

    return BedTool(clean_string, from_string=True)

def _cleanup_intersect_gff_gff(dirty):
    clean_string = ''
    for row in dirty:
        new_row = "\t".join(row[:8])
        ann_a = _parse_annotations(row[8])
        ann_b = _parse_annotations(row[17])
        new_annotations = {}
        new_annotations['regulator'] = "{0}~{1}".format(ann_a['regulator'], ann_b['regulator'])
        new_annotations['score'] = "%s" % ((int(ann_a['score']) + int(ann_b['score'])) // 2)
        new_annotations['start'] = "%s" % max(int(ann_a['start']), int(ann_b['start']))
        new_annotations['end'] = "%s" % min(int(ann_a['end']), int(ann_b['end']))
        new_row += "\tID={0};regulator={1};score={2};start={3};end={4}\n".format(ann_a['ID'],
            new_annotations['regulator'], new_annotations['score'],
            new_annotations['start'], new_annotations['end'])
        clean_string += new_row

    return BedTool(clean_string, from_string=True)

def _get_genome_bedtool(genome_name, region, datadir=None):
    """get the bedtool object for a genome depending on the name and the region"""
    genome = utils.get_genome_by_name(genome_name, datadir)
    if region == "any":
        filename = path.join(genome, 'all.gff')
    elif region == "CDS":
        filename = path.join(genome, 'cds.gff')
    elif region == "3prime":
        filename = path.join(genome, '3_utr.gff')
    elif region == "5prime":
        filename = path.join(genome, '5_utr.gff')
    elif region == "intron":
        filename = path.join(genome, 'intron.gff')
    elif region == "intergenic":
        filename = path.join(genome, 'intergenic.gff')
    else:
        raise ValueError("Invalid region: %r" % region)

    return BedTool(filename)


def _get_regulator_bedtool(regulator_name, datadir=None):
    """get the bedtool object for a regulator"""
    return BedTool('%s.bed' % utils.get_regulator_by_name(regulator_name, datadir))


def _parse_results(bedtool_results):
    """parse a bedtool result data structure"""
    results = []

    for res in bedtool_results:
        annotations = _parse_annotations(res[8])
        gene = annotations['ID']
        tracks, data_sources, sites = _parse_tracks_sources_regulators(annotations['regulator'])
        for i in range(len(tracks)):
            track = tracks[i]
            score = int(annotations['score'])
            strand = res[6]
            start = annotations['start']
            end = annotations['end']
            location = "%s:%s-%s" % (res.chrom, start, end)
            data_source = data_sources[i]
            site = sites[i]
            results.append(dict(track=track, gene=gene, data_source=data_source,
                            score=score, site=site, location=location, strand=strand))

    return results


def _parse_annotations(string):
    annotation_dict = {}
    annotation_list = string.split(';')
    for ann in annotation_list:
        key, val = ann.split('=')
        annotation_dict[key] = val

    return annotation_dict


def _parse_tracks_sources_regulators(string):
    raw = string.split('~')
    tracks = []
    sources = []
    regulators = []
    for r in raw:
        source, rest = r.split('#')
        track, regulator = rest.split('*')
        tracks.append(track)
        sources.append(source)
        regulators.append(regulator)

    return tracks, sources, regulators
