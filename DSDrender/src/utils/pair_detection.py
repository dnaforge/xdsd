from src.parsing.parsing_exception import ParsingException


def set_domain_pairs(species):
    """
    Puts all the pairs that are in this species into a dictionary with bond_id as keys and domains lists as values

    :return:
    """
    domains = [domain for domain in species.get_domains() if
               domain.__class__.__name__ != 'Loop' and domain.get_bond()[:2] != "-1"]
    for idx in range(len(domains)):
        species.domain_pairs[domains[idx].bond].append(domains[idx])

    for domains_list in species.domain_pairs.values():
        if len(domains_list) != 2:
            raise ParsingException("Unpaired domains!")
