# vim: set fileencoding=utf-8 :

import logging
import os
import json
from os import path
import re

from dorina.genome    import Genome
from dorina.regulator import Regulator

gene_name = re.compile(r'.*ID=(.*?)($|;\w+)')

class DorinaUtils:
    def __init__(self, datadir):
        self.datadir = datadir
        self.genomes = self._genomes()
        self.regulators = self._regulators()

    def _genomes(self):
        return self.walk_assembly_tree('genomes', Genome.parse_func)

    def _regulators(self):
        return self.walk_assembly_tree('regulators', Regulator.parse_func)

    def walk_assembly_tree(self, root_dir, parse_func):
        """Walk a directory structure containg clade, species, assembly

        Call parse_func() for every assembly directory"""
        genomes = {}

        root = path.join(self.datadir, root_dir)

        for species in os.listdir(root):
            species_path = path.join(root, species)
            if not path.isdir(species_path):
                #logging.debug("skipping non-directory %r" % species_path)
                continue

            description_file = path.join(species_path, 'description.json')
            species_dict = {}
            try:
                with open(description_file, 'r') as fh:
                    genomes[species] = json.load(fh)
                    genomes[species]['assemblies'] = species_dict
            except IOError:
                genomes[species] = species_dict

            for assembly in os.listdir(species_path):
                assembly_path = path.join(species_path, assembly)
                if not path.isdir(assembly_path):
                    #logging.debug("skipping non-directory %r" % assembly_path)
                    continue

                assembly_dict = {}
                species_dict[assembly] = assembly_dict

                parse_func(assembly_path, assembly_dict)

        return genomes

    def get_genome_by_name(self, name):
        """Take a genome name and return the path to the genome directory"""
        for species, species_dir in self.genomes.items():
            if name in species_dir['assemblies']:
                return path.join(self.datadir, 'genomes', species, name)

        # TODO: never return None!
        return None

    def get_genes(self, name):
        """Get a list of genes from genome <name>"""
        genes = []

        genome_dir = self.get_genome_by_name(name)
        if genome_dir is None:
            return genes

        genome = path.join(genome_dir, 'all.gff')
        if not path.exists(genome):
            return genes

        for line in open(genome, 'r'):
            match = gene_name.match(line)
            if match is not None:
                genes.append(match.group(1))

        return genes
