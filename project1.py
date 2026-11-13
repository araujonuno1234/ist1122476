"""Projeto 1 de FP - Campanha de observação de exoplanetas."""

from dataclasses import dataclass


@dataclass
class Star:
    """Estrela; priority é a prioridade científica global."""
    name: str
    distance: int
    radius: int
    magnitude: int
    priority: int


@dataclass
class Planet:
    """Exoplaneta; priority é a prioridade local no sistema da estrela."""
    name: str
    host_star: Star
    planet_radius: int
    period: int
    first_transit_start: int
    duration: int
    method: str
    year: int
    priority: int


@dataclass
class System:
    """Estrela e os seus planetas, por prioridade local crescente."""
    star: Star
    planets: list[Planet]


@dataclass
class Catalog:
    """Associa o nome de cada estrela ao seu sistema."""
    systems: dict[str, System]


@dataclass
class Transit:
    """Observação de planet no intervalo [start, end[."""
    planet: Planet
    start: int
    end: int


# Funções auxiliares

def scientific_priority(planet: Planet) -> tuple[int, int]:
    """Ordem composta: prioridade da estrela e depois prioridade local."""
    return (planet.host_star.priority, planet.priority)


def plan_key(transit: Transit) -> tuple[int, int, int]:
    """Ordem do build_plan: fim crescente e, em empate, prioridade."""
    return (transit.end, transit.planet.host_star.priority,
            transit.planet.priority)


def is_transit_start(planet: Planet, start: int) -> bool:
    """Verifica se start é o início de um trânsito previsto de planet."""
    return (start >= planet.first_transit_start
            and (start - planet.first_transit_start) % planet.period == 0)


# 4.1 Ler e construir o catálogo

def valid_star(star: Star) -> bool:
    """Verifica os invariantes de uma estrela."""
    return (star.name != "" and star.distance > 0 and star.radius > 0
            and star.priority > 0)


def create_star(name: str, distance: int, radius: int, magnitude: int,
                priority: int) -> Star:
    """Cria uma estrela; gera ValueError se os argumentos forem inválidos."""
    star: Star = Star(name, distance, radius, magnitude, priority)
    if not valid_star(star):
        raise ValueError("create_star: invalid arguments")
    return star


def valid_planet(planet: Planet) -> bool:
    """Verifica os invariantes de um planeta."""
    return (planet.name != "" and planet.method != ""
            and valid_star(planet.host_star)
            and planet.planet_radius > 0 and planet.period > 0
            and planet.duration > 0 and planet.year > 0
            and planet.priority > 0
            and 0 <= planet.first_transit_start < planet.period)


def create_planet(name: str, host_star: Star, planet_radius: int, period: int,
                  first_transit_start: int, duration: int, method: str,
                  year: int, priority: int) -> Planet:
    """Cria um planeta; gera ValueError se os argumentos forem inválidos."""
    planet: Planet = Planet(name, host_star, planet_radius, period,
                            first_transit_start, duration, method, year,
                            priority)
    if not valid_planet(planet):
        raise ValueError("create_planet: invalid arguments")
    return planet


def valid_system(system: System) -> bool:
    """Verifica os invariantes de um sistema."""
    if not valid_star(system.star) or len(system.planets) == 0:
        return False
    i: int
    for i in range(len(system.planets)):
        planet: Planet = system.planets[i]
        if not valid_planet(planet) or planet.host_star != system.star:
            return False
        if i > 0 and system.planets[i - 1].priority >= planet.priority:
            return False
    return True


def create_system(star: Star, planets: list[Planet]) -> System:
    """Cria um sistema; gera ValueError se for inválido."""
    # Copia a lista para que mudanças na lista original não afetem o sistema.
    system: System = System(star, list(planets))
    if not valid_system(system):
        raise ValueError("create_system: invalid arguments")
    return system


def valid_catalog(catalog: Catalog) -> bool:
    """Verifica os invariantes de um catálogo."""
    priorities: list[int] = []
    name: str
    system: System
    for name, system in catalog.systems.items():
        # Uma chave vazia falha aqui, porque o nome da estrela não é vazio.
        if not valid_system(system) or name != system.star.name:
            return False
        if system.star.priority in priorities:
            return False
        priorities.append(system.star.priority)
    return True


def create_catalog(systems: dict[str, System]) -> Catalog:
    """Cria um catálogo; gera ValueError se for inválido."""
    catalog: Catalog = Catalog(dict(systems))
    if not valid_catalog(catalog):
        raise ValueError("create_catalog: invalid arguments")
    return catalog


def read_catalog(filename: str) -> Catalog:
    """Lê o catálogo do ficheiro; gera ValueError se houver dados inválidos."""
    stars: dict[str, Star] = {}
    planets: dict[str, list[Planet]] = {}
    with open(filename, encoding="utf-8") as file:
        lines: list[str] = file.read().splitlines()[1:]
    try:
        line: str
        for line in lines:
            if line.strip() == "":
                continue
            # name;star;star_priority;distance;planet_radius;star_radius;
            # magnitude;period;first_transit_start;duration;method;year;
            # planet_priority
            fields: list[str] = line.split(";")
            star: Star = create_star(fields[1], int(fields[3]),
                                     int(fields[5]), int(fields[6]),
                                     int(fields[2]))
            if star.name not in stars:
                stars[star.name] = star
                planets[star.name] = []
            elif stars[star.name] != star:
                raise ValueError  # a mesma estrela com dados diferentes
            planets[star.name].append(create_planet(
                fields[0], stars[star.name], int(fields[4]), int(fields[7]),
                int(fields[8]), int(fields[9]), fields[10], int(fields[11]),
                int(fields[12])))
        systems: dict[str, System] = {}
        name: str
        for name in stars:
            systems[name] = create_system(stars[name], planets[name])
        return create_catalog(systems)
    except ValueError:
        raise ValueError("read_catalog: invalid data")


def number_of_systems(catalog: Catalog) -> int:
    """Devolve o número de sistemas do catálogo."""
    return len(catalog.systems)


def planets_of_star(catalog: Catalog, star_name: str) -> list[Planet]:
    """Devolve (uma cópia d)os planetas de star_name, ou [] se não existir."""
    if star_name in catalog.systems:
        return list(catalog.systems[star_name].planets)
    return []


# 4.2 Medir o sinal e qualificar alvos

def transit_depth(planet: Planet) -> int:
    """Profundidade do trânsito em ppm, só com inteiros."""
    p: int = planet.planet_radius
    s: int = planet.host_star.radius
    return (10 ** 10 * p * p) // (1091 ** 2 * s * s)


def is_observable(planet: Planet, max_magnitude: int,
                  min_duration: int) -> bool:
    """Verifica os limites de magnitude e de duração."""
    return (planet.host_star.magnitude <= max_magnitude
            and planet.duration >= min_duration)


# 4.3 Eliminar alvos redundantes

def is_better_target(first: Planet, second: Planet) -> bool:
    """Verifica se first é melhor alvo do que second."""
    d1: int = transit_depth(first)
    d2: int = transit_depth(second)
    m1: int = first.host_star.magnitude
    m2: int = second.host_star.magnitude
    # Se first for pior em algum critério, não é melhor.
    if d1 < d2 or m1 > m2 or first.duration < second.duration:
        return False
    # Tem de ser estritamente melhor em pelo menos um critério.
    return d1 > d2 or m1 < m2 or first.duration > second.duration


def observable_frontier(catalog: Catalog, max_magnitude: int,
                        min_duration: int) -> list[Planet]:
    """Planetas observáveis e não redundantes, por prioridade científica."""
    eligible: list[Planet] = []
    system: System
    planet: Planet
    for system in catalog.systems.values():
        for planet in system.planets:
            if is_observable(planet, max_magnitude, min_duration):
                eligible.append(planet)
    frontier: list[Planet] = []
    other: Planet
    for planet in eligible:
        redundant: bool = False
        for other in eligible:
            if is_better_target(other, planet):
                redundant = True
                break
        if not redundant:
            frontier.append(planet)
    return sorted(frontier, key=scientific_priority)


# 4.4 Prever oportunidades de trânsito

def valid_transit(transit: Transit) -> bool:
    """Verifica os invariantes de um trânsito."""
    return (valid_planet(transit.planet)
            and is_transit_start(transit.planet, transit.start)
            and transit.end == transit.start + transit.planet.duration)


def create_transit(planet: Planet, start: int) -> Transit:
    """Cria um trânsito; gera ValueError se for inválido."""
    transit: Transit = Transit(planet, start, start + planet.duration)
    if not valid_transit(transit):
        raise ValueError("create_transit: invalid arguments")
    return transit


def generate_transits(planet: Planet, campaign_duration: int) -> list[Transit]:
    """Trânsitos de planet que terminam até campaign_duration, por ordem."""
    transits: list[Transit] = []
    start: int = planet.first_transit_start
    while start + planet.duration <= campaign_duration:
        transits.append(create_transit(planet, start))
        start += planet.period
    return transits


def generate_campaign(catalog: Catalog, max_magnitude: int, min_duration: int,
                      campaign_duration: int) -> list[Transit]:
    """Trânsitos dos planetas da fronteira, por prioridade e início."""
    campaign: list[Transit] = []
    planet: Planet
    for planet in observable_frontier(catalog, max_magnitude, min_duration):
        campaign.extend(generate_transits(planet, campaign_duration))
    return campaign


# 4.5 Construir o plano de um telescópio

def compatible_transits(first: Transit, second: Transit) -> bool:
    """Verifica se os dois trânsitos não se sobrepõem."""
    return first.end <= second.start or second.end <= first.start


def build_plan(candidates: list[Transit]) -> list[Transit]:
    """Maior plano possível de trânsitos compatíveis, por fim crescente.

    Escolhe sempre o trânsito que acaba mais cedo e é compatível com o plano:
    deixa o máximo de tempo livre para os outros, por isso o plano fica com
    o maior número possível de trânsitos. Em empates de fim ganha o planeta
    com maior prioridade científica.
    """
    plan: list[Transit] = []
    transit: Transit
    for transit in sorted(candidates, key=plan_key):
        # Estão ordenados por fim, basta comparar com o último aceite.
        if len(plan) == 0 or compatible_transits(plan[-1], transit):
            plan.append(transit)
    return plan


def build_plan_from_series(series: list[list[Transit]]) -> list[Transit]:
    """Junta todas as séries e constrói o maior plano possível."""
    candidates: list[Transit] = []
    transits: list[Transit]
    for transits in series:
        candidates.extend(transits)
    return build_plan(candidates)