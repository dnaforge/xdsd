from DSDVis.elements.domain import Domain
from DSDVis.elements.species import Species
from DSDVis.elements.strand import Strand
from DSDVis.parsing.parsing_exception import ParsingException


def parse_output_text(text, init_species_no):
    """
    Parses the whole output file

    :param text: Content of the input file
    :return: Dictionary of parsed species and dictionary of kinetics values
    """
    species, ps_error = parse_species(text, init_species_no)

    errors = []
    if ps_error is not None:
        errors.append(ps_error)

    return species, errors


def parse_species(text, init_species_no):
    """
    Parses a list of species

    :param text:
    :return: Dictionary with names of species as keys and
    dictionaries with Species object and initial count as values
    """
    error = None
    species_list = {}
    try:
        start = text.find("-----Species-----") + len("-----Species-----") + 1
        end = text.find("-----Reactions-----", start) - 2

        unparsed_species = text[start:end].split("\n\n")
        for i, s in enumerate(unparsed_species, 1):
            id, strands = parse_strands(s)
            if i <= init_species_no:
                prefix = "ss"
            else:
                prefix = "sp_"
            species_list[prefix + str(id)] = Species(strands)

    except ParsingException as pe:
        error = pe

    return species_list, error


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
            strand = Strand()

            for idx in range(len(unparsed_domains)):
                bond = unparsed_domains[idx].find("!")
                toehold = unparsed_domains[idx].find("^")
                if idx == len(unparsed_domains) - 1:
                    last = True
                if toehold == -1:
                    toehold = False
                else:
                    toehold = True
                if bond == -1:
                    strand.add_domain(Domain(unparsed_domains[idx], strand.get_id(), bond, last, toehold))
                else:
                    strand.add_domain(
                        Domain(unparsed_domains[idx][:bond], strand.get_id(), unparsed_domains[idx][bond + 1:], last, toehold))

            strands.append(strand)
        else:
            raise ParsingException("Incorrect species definition!")
    return int(name), strands
