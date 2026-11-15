"""
    in : records (liste de dictionnaires venant de extract_transforme)
    out :  graphiques affiches à l'ecran
"""

import logging

import matplotlib.pyplot as plt

from processing import extract_transforme, geo_location

logger = logging.getLogger(__name__)

TOP_N = 10  # nombre de barres affichées par graphique


def draw_bar(counts, title, xlabel, ylabel):
    """Prepare un graphique en barres avec les TOP_N plus grandes valeurs."""
    if not counts:
        logger.warning(title + " : aucune donnée, graphique non créé")
        return

    # On trie du plus grand au plus petit et on garde les TOP_N premiers
    top = sorted(counts.items(), key=lambda item: item[1], reverse=True)[:TOP_N]
    names = [item[0] for item in top]
    values = [item[1] for item in top]

    plt.figure(figsize=(10, 6))
    plt.bar(names, values)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45)
    plt.tight_layout()
    logger.info(title + " : graphique prepare")


def build_dashboard(records):
    """Prepare les trois graphiques demandes, puis les affiche."""
    # 1. Tentatives echouees par pays
    draw_bar(geo_location.count_by_country(records, 'Failed'),
             'Tentatives échouées par pays',
             'Pays', 'Nombre de tentatives')

    # 2. Connexions reussies par utilisateur
    draw_bar(extract_transforme.count_by_user(records, 'Success'),
             'Connexions reussies par utilisateur',
             'Utilisateur', 'Nombre de connexions')

    # 3. Tentatives avec "Invalid user"
    draw_bar(extract_transforme.count_by_user(records, 'Invalid'),
             'Tentatives avec Invalid user',
             'Utilisateur', 'Nombre de tentatives')

    # Affiche les trois fenetres en meme temps
    try:
        plt.show()
    except Exception as e:
        logger.error("Affichage impossible (" + str(e) + ")")


if __name__ == '__main__':
    from ingestion import raw

    records = extract_transforme.extract(raw.to_rows('./data'))
    build_dashboard(records)