import multiprocessing

from matplotlib import pyplot as plt

from DSDVis.optimization.simulated_annealing import E, decrease_temperature, optimize_one_iteration
from DSDVis.parsing.dsd_input_parser import parse_input_text
from DSDVis.parsing.dsd_output_parser import parse_output_text
from DSDVis.utils.config import INITIAL_ITER_NO, get_next_color
from DSDVis.utils.species_placement import place_species
from DSDVis.utils.strand_permutation import get_permutation


class UiModel:
    """
    Class for holding current species data for the controller and view of the ui
    """
    def __init__(self):
        self.file_dir = ""
        self.input_species_dict = {}
        self.output_species_dict = {}
        self.species_names = []
        self.kinetics_dict = {}
        self.fig, self.ax = plt.subplots()

    def read_file(self, file_dir):
        log = ""
        error = ""
        self.file_dir = file_dir
        try:
            with open(self.file_dir, 'r') as f:
                text = f.read()
                log = "File is read"
        except OSError as e:
            error = e

        return text, log, error

    def reset_species(self, i=None):
        if i is None:
            self.input_species_dict = {}
            self.output_species_dict = {}
        elif i == 0:
            self.input_species_dict = {}
        else:
            self.output_species_dict = {}
        self.species_names = []
        self.kinetics_dict = {}

    def parse_input_species(self, text, permute, flip_strands, flip_domains, bond_colors):
        self.input_species_dict, self.kinetics_dict, errors = parse_input_text(text)
        self.species_names = list(self.input_species_dict.keys())
        log = []
        if len(errors) == 0:
            for specie in self.input_species_dict.values():
                if len(specie.get_strands()) > 7 and flip_strands:
                    flip_strands = False
                    log.append('Too many strands to flip! Aborting flipping strands')

                if not get_permutation(specie, permute, flip_strands, flip_domains):
                    log.append("Pseudoknot")

                for domain in specie.get_domains():
                    if domain.__class__.__name__ == 'Loop':
                        for inside_domain in domain.get_domains():
                            name_key = inside_domain.name
                            idx = inside_domain.name.find('*')
                            if idx != -1:
                                name_key = name_key[:idx]
                            if name_key not in bond_colors:
                                bond_colors[name_key] = get_next_color()
                    else:
                        name_key = domain.name
                        idx = domain.name.find('*')
                        if idx != -1:
                            name_key = name_key[:idx]
                        if name_key not in bond_colors:
                            bond_colors[name_key] = get_next_color()

        return log, errors

    def parse_output_species(self, text, permute, flip_strands, flip_domains, init_species_no):
        self.output_species_dict, errors = parse_output_text(text, init_species_no)
        self.species_names = list(self.output_species_dict.keys())
        log = []
        if len(errors) == 0:
            for specie in self.output_species_dict.values():
                if len(specie.get_strands()) > 7 and flip_strands:
                    flip_strands = False
                    log.append('Too many strands to flip! Aborting flipping strands')
                if not get_permutation(specie, permute, flip_strands, flip_domains):
                    log.append("Pseudoknot")

        return log, errors

    def place_species(self, species_list):
        species_list = species_list.values()
        height = 0
        for species in species_list:
            next_height = place_species(species)
            species.render_height = height
            species.height_inc = next_height
            height += next_height

    def recalculate_render_height(self, species_list):
        species_list = species_list.values()
        new_height = 0
        for species in species_list:
            species.render_height = new_height
            new_height += species.height_inc
