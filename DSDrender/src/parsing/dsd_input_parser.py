from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QApplication

import src.utils.config
from src.elements.domain import Domain
from src.elements.species import Species
from src.elements.strand import Strand
from src.interface.progress_window import ProgressWindow
from src.parsing.parsing_signals import ParsingSignals
from src.parsing.parsing_exception import ParsingException


def parse_input_text(text, progress_window):
    """
    Parses the whole input file

    :param text: Content of the input file
    :return: Dictionary of parsed species and dictionary of kinetics values
    """
    species, ps_error, g_errors = parse_species(text, progress_window)
    kinetics, k_errors = parse_kinetics(text)

    errors = []
    if ps_error is not None:
        errors.append(ps_error)
    if k_errors[0] is not None:
        errors.append(k_errors[0])
    if k_errors[1] is not None:
        errors.append(k_errors[1])

    return species, kinetics, errors, g_errors


def parse_species(text, progress_window):
    """
    Parses a list of species

    :param text:
    :return: Dictionary with names of species as keys and dictionaries with Species object and initial count as values
    """
    error = None
    g_errors = []
    species_list = {}
    signals = ParsingSignals()

    try:
        names_list = parse_names(text)

        start = 0
        end = text.find("//", start) - 1

        parsed_strands = []
        i = 0

        stop = [False]

        def stop_graph():
            stop[0] = True

        progress_window[0] = ProgressWindow(src.utils.config.get_id(), signals.finished,signals.update, src.utils.config.START_TEMP_CONST, len(names_list), stop_graph, "Rendering species...")
        progress_window[0].show()
        QApplication.processEvents()

        while end != -2:  # while there are species left to read
            unparsed_strands = text[start:end].split("\n")
            for s in unparsed_strands:
                parsed_strands.append(parse_strand(s))
            if i < len(names_list):
                species_list[names_list[i][0]] = Species(names_list[i][0], parsed_strands)
                species_list[names_list[i][0]].create_graph(signals, i, stop)
                for ge in species_list[names_list[i][0]].graph.errors:
                    g_errors.append(ge)
            else:
                raise ParsingException("Unnamed species!")
            parsed_strands.clear()

            start = end + 4  # omit "\n//\n"
            end = text.find("//", start) - 1
            i += 1

        last_end = text.find("--", start) - 1  # last line (not separated by //)
        unparsed_strands = text[start:last_end].split("\n")
        for s in unparsed_strands:
            parsed_strands.append(parse_strand(s))
        if i < len(names_list):
            species_list[names_list[i][0]] = Species(names_list[i][0], parsed_strands)
            species_list[names_list[i][0]].create_graph(signals, i, stop)
            for ge in species_list[names_list[i][0]].graph.errors:
                g_errors.append(ge)
        else:
            raise ParsingException("Unnamed species!")
    except ParsingException as pe:
        error = pe

    signals.finished.emit()
    return species_list, error, g_errors

def parse_names(text):
    """
    Parses the names and initial counts of the species

    :param text:
    :return: A list with the lists of names and counts
    """
    start = text.find("--") + 3
    end = text.find("--", start) - 1

    if start < end:
        unparsed_names = text[start:end].split("\n")
        names = []
        for name in unparsed_names:
            names.append(name.split(" "))
    else:
        raise ParsingException("No names for the species!")

    return names


def parse_strand(text):
    """
    Parses a single strand

    :param text: Full strand string
    :return: Strand object
    """
    if text[0] == "<" and text[len(text) - 1] == ">":
        cut_str = text[1:len(text) - 1]
        unparsed_domains = cut_str.split(" ")
        first = True
        strand = Strand()

        for idx in range(len(unparsed_domains)):
            bond = unparsed_domains[idx].find("!")
            toehold = unparsed_domains[idx].find("^")
            last = idx == len(unparsed_domains) - 1
            toehold = toehold != -1
            if bond == -1:
                strand.add_domain(Domain(unparsed_domains[idx], strand.get_id(), bond, first, last, toehold))
            else:
                strand.add_domain(
                    Domain(unparsed_domains[idx][:bond], strand.get_id(), unparsed_domains[idx][bond + 1:], first, last,
                           toehold))
            first = False

    else:
        raise ParsingException("Incorrect species definition!")
    return strand


def parse_kinetics(text):
    """
    Parses the kinetics of the system

    :param text:
    :return: Dictionary with reaction names as keys and reaction rates as values
    """
    error = [None, None]
    kinetics = {}
    kinetics_names = {'RB', 'RU', 'R3', 'R4'}
    try:
        start = text.find("--", text.find("--") + 3) + 3
        end = text.find("--", start)
        if end == -1:
            end = len(text)

        unparsed_kinetics = text[start:end].split("\n")
        unparsed_kinetics = [uk for uk in unparsed_kinetics if uk != '']
        if len(unparsed_kinetics) == 4:
            for kinetic in unparsed_kinetics:
                kinetic_list = kinetic.split(" ")
                try:
                    float(kinetic_list[1])
                except ValueError:
                    raise ParsingException("Invalid kinetics value!")
                if kinetic_list[0] not in kinetics_names:
                    raise ParsingException("Invalid kinetics name!")
                kinetics[kinetic_list[0]] = kinetic_list[1]
        else:
            raise ParsingException("No kinetics defined!")
    except ParsingException as pe:
        error[0] = pe
    except IndexError as ie:
        error[1] = ie

    return kinetics, error
