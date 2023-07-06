from matplotlib import pyplot as plt

from src.parsing.dsd_input_parser import parse_input_text
from src.parsing.dsd_output_parser import parse_output_text
from src.utils.config import get_next_color


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
        self.colors = {}

    def read_file(self, file_dir):
        log = ""
        error = ""
        text = ""
        self.file_dir = file_dir
        try:
            with open(self.file_dir, 'r') as f:
                text = f.read()
                log = "File is read"
        except OSError:
            error = "Bad file format!"
        except UnicodeDecodeError:
            error = "Bad file format!"

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
        self.colors = {}

    def parse_input_species(self, text, progress_window):
        self.input_species_dict, self.kinetics_dict, errors, graph_errors = parse_input_text(text, progress_window)
        self.species_names = list(self.input_species_dict.keys())
        log = []
        if len(errors) == 0:
            for specie in self.input_species_dict.values():
                for domain in specie.get_domains():
                    # color the species
                    if domain.__class__.__name__ != 'Loop' and domain.__class__.__name__ != 'Overhang':
                        if domain.get_name_stem() not in self.colors:
                            self.colors[domain.get_name_stem()] = get_next_color()

        return log, errors, graph_errors

    def parse_output_species(self, text, init_species_no, progress_window):
        self.output_species_dict, errors, graph_errors = parse_output_text(text, init_species_no, progress_window)
        self.species_names = list(self.output_species_dict.keys())
        log = []
        # if len(errors) == 0:
        #     for specie in self.output_species_dict.values():
        #         if len(specie.get_strands()) > 7 and flip_strands:
        #             flip_strands = False
        #             log.append('Too many strands to flip! Aborting flipping strands')
        #         if not get_permutation(specie, permute, flip_strands, flip_domains):
        #             log.append("Pseudoknot")
        if len(errors) == 0:
            for specie in self.output_species_dict.values():
                for domain in specie.get_domains():
                    # color the species
                    if domain.__class__.__name__ != 'Loop' and domain.__class__.__name__ != 'Overhang':
                        if domain.get_name_stem() not in self.colors:
                            self.colors[domain.get_name_stem()] = get_next_color()

        return log, errors, graph_errors

    # def place_species(self, species_list):
    #     species_list = species_list.values()
    #     height = 0
    #     for species in species_list:
    #         next_height = place_species(species)
    #         species.render_height = height
    #         species.height_inc = next_height
    #         height += next_height
    #
    # def recalculate_render_height(self, species_list):
    #     species_list = species_list.values()
    #     new_height = 0
    #     for species in species_list:
    #         species.render_height = new_height
    #         new_height += species.height_inc
