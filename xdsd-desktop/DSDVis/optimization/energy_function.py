from math import exp

from DSDVis.utils.config import euclidean_dist, DOMAIN_LEN


def E(species):
    """
    Energy function for a single species. That is the sum of all bounded domains attracting and unbounded domain repulsing each other

    :param species: Species object
    :return:
    """
    sum_total = sum_attraction = sum_parallel = sum_angle = sum_repulsion = 0
    domain_pairs = species.get_domain_pairs()

    for bond_id, domains in domain_pairs.items():
        if bond_id != -1:
            attraction = attract_bounded(domains[0], domains[1])
            attraction += attract_bounded(domains[1], domains[0])
            sum_attraction += attraction
            sum_total += attraction

    for strand in species.get_strands():
        strand_domains = strand.get_domains()
        for i in range(len(strand_domains) - 1):
            repulsion = repulse_unbounded(strand_domains[i], species.get_domains())
            sum_total += repulsion
            sum_repulsion += repulsion

    return sum_total, (sum_total, sum_attraction, sum_parallel, sum_angle, sum_repulsion)


def attract_bounded(domain1, domain2):
    """
    Attraction term from the energy function

    :param domain1: First bounded Domain object
    :param domain2: Second bounded Domain object
    :return: The euclidean distance between the second domain's center and the where it should be in regards to the first domain
    """
    attraction = euclidean_dist(domain2.center, domain1.goal_bond)
    attraction *= attraction

    return attraction


def repulse_unbounded(domain, other_domains):
    """
    Repulsion term from the energy function

    :param domain: Domain object that repulses all other domains in the species, which are not bounded to this domain
    :param other_domains: Other domains that are being repulsed
    :return: Sum of repulsions of other_domains by domain
    """
    dist_sum = 0
    division_factor = 1

    if domain.__class__.__name__ == 'Loop':
        repulsion_center = domain.mass_center
    else:
        repulsion_center = domain.center

    for other_domain in other_domains:
        if other_domain is not domain:
            if other_domain.__class__.__name__ == 'Loop':
                other_domain_center = other_domain.mass_center
            else:
                other_domain_center = other_domain.center
            dist = euclidean_dist(repulsion_center, other_domain_center)
            if domain.__class__.__name__ == 'Loop' or other_domain.__class__.__name__ == 'Loop' or \
                    (domain.get_bond() == -1 or domain.get_bond() != other_domain.get_bond()) and dist != 0:
                # different repulsion equations
                # dist_sum += (DOMAIN_LEN ** 2)/(division_factor * dist)
                # dist_sum += 1.5*DOMAIN_LEN * exp(-dist/50)
                # dist_sum += 2*DOMAIN_LEN * exp(-dist/25) + 1
                # dist_sum += (DOMAIN_LEN * 25)/(12.5+dist)
                dist_sum += 2 * DOMAIN_LEN / division_factor * exp(-dist / DOMAIN_LEN) + 1

    return dist_sum
