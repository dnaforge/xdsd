from math import sin, cos, pi

from DSDVis.utils.config import DOMAIN_LEN, get_radius


def place_species(species):
    """
    Performs initial placement of the domains in all strands of given species on a circle

    :param species: Reference to the Species object to place
    :return: Lower bound of the placed species, necessary for placing next species under it
    """
    strands = species.get_strands()

    n = len(species.get_domains())
    r = get_radius(n, len(strands)) + DOMAIN_LEN

    center = (0, r)

    next_height = 0

    i = 0
    for strand in strands:
        x_start = r * sin(i / n * 2 * pi)
        y_start = r * cos(i / n * 2 * pi)
        x_end = r * sin((i + len(strand.domains)) / n * 2 * pi)
        y_end = r * cos((i + len(strand.domains)) / n * 2 * pi)

        direction = [x_end - x_start, y_end - y_start]

        if strand.flipped:
            direction = [-direction[0], -direction[1]]

        direction_len = (direction[0] ** 2 + direction[1] ** 2) ** 0.5
        direction = [direction[0] * DOMAIN_LEN / 2 / direction_len, direction[1] * DOMAIN_LEN / 2 / direction_len]

        x = x_start + (x_end - x_start) / 2 - direction[0] * (len(strand.domains))
        y = y_start + (y_end - y_start) / 2 - direction[1] * (len(strand.domains))

        if len(strands) == 2 and i != 0:
            x -= DOMAIN_LEN
            y -= DOMAIN_LEN

        for domain in strand.domains:
            domain_direction = [direction[0] * domain.domain_len / DOMAIN_LEN, direction[1] * domain.domain_len / DOMAIN_LEN]
            if domain.__class__.__name__ == 'Loop':
                domain.set_ends([center[0] + x, center[1] + y],
                                [center[0] + x + 2 * domain_direction[0], center[1] + y + 2 * domain_direction[1]])

                species_len = len(strand.domains) * DOMAIN_LEN
                if domain.loop_center[1] + species_len / 2 > next_height:
                    next_height = domain.loop_center[1] + species_len / 2
            else:
                domain.set_coordinates([center[0] + x + domain_direction[0], center[1] + y + domain_direction[1]], domain_direction)

                if max(center[1] + y + 2 * domain_direction[1], center[1] + y) + DOMAIN_LEN > next_height:
                    next_height = max(center[1] + y + 2 * domain_direction[1], center[1] + y) + DOMAIN_LEN

            x = x + 2 * domain_direction[0]
            y = y + 2 * domain_direction[1]
            i += 1

        strand.set_hinges()

    return next_height
