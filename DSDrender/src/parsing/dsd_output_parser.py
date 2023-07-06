from PyQt5.QtWidgets import QApplication

import src.utils.config
from src.elements.domain import Domain
from src.elements.species import Species
from src.elements.strand import Strand
from src.interface.progress_window import ProgressWindow
from src.parsing.parsing_signals import ParsingSignals
from src.parsing.parsing_exception import ParsingException


def parse_output_text(text, init_species_no, progress_window):
    """
    Parses the whole output file

    :param text: Content of the input file
    :return: Dictionary of parsed species and dictionary of kinetics values
    """
    species, ps_error, g_errors = parse_species(text, init_species_no, progress_window)

    errors = []
    if ps_error is not None:
        errors.append(ps_error)

    return species, errors, g_errors


def parse_species(text, init_species_no, progress_window):
    """
    Parses a list of species

    :param text:
    :return: Dictionary with names of species as keys and dictionaries with Species object and initial count as values
    """
    error = None
    g_errors = []
    species_list = {}
    signals = ParsingSignals()
    stop = [False]

    def stop_graph():
        stop[0] = True

    try:
        start = text.find("-----Species-----") + len("-----Species-----") + 1
        end = text.find("-----Reactions-----", start) - 2

        unparsed_species = text[start:end].split("\n\n")
        progress_window[0] = ProgressWindow(src.utils.config.get_id(), signals.finished,signals.update, src.utils.config.START_TEMP_CONST, len(unparsed_species), stop_graph, "Rendering species...")
        progress_window[0].show()
        QApplication.processEvents()
        for i, s in enumerate(unparsed_species, 1):
            id, strands = parse_strands(s)
            if i <= init_species_no:
                prefix = "ss"
            else:
                prefix = "sp_"
            species_list[prefix + str(id)] = Species(prefix + str(id), strands)
            species_list[prefix + str(id)].create_graph(signals, i-1, stop)
            for ge in species_list[prefix + str(id)].graph.errors:
                g_errors.append(ge)

    except ParsingException as pe:
        error = pe

    signals.finished.emit()
    return species_list, error, g_errors

def parse_strands(text):
    """
    Parses a single strand

    :param text: Full strand string
    :return: Strand object
    """
    strand = None
    strands = []

    unparsed_strands = text.split("\n")
    name = unparsed_strands[0]

    for i in range(1, len(unparsed_strands)):
        if unparsed_strands[i][0] == "<" and unparsed_strands[i][len(unparsed_strands[i]) - 1] == ">":
            cut_str = unparsed_strands[i][1:len(unparsed_strands[i]) - 1]
            unparsed_domains = cut_str.split(" ")
            last = False
            first = True
            strand = Strand()

            for idx in range(len(unparsed_domains)):
                bond = unparsed_domains[idx].find("!")
                toehold = unparsed_domains[idx].find("^")
                if idx == len(unparsed_domains) - 1:
                    last = True
                toehold = toehold != -1
                if bond == -1:
                    strand.add_domain(Domain(unparsed_domains[idx], strand.get_id(), bond, first, last, toehold))
                else:
                    strand.add_domain(
                        Domain(unparsed_domains[idx][:bond], strand.get_id(), unparsed_domains[idx][bond + 1:], first,
                               last, toehold))
                first = False

            strands.append(strand)
        else:
            raise ParsingException("Incorrect species definition!")
    return int(name), strands
