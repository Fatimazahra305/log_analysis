"""
    Pipeline d'analyse des logs SSH :
    raw (lecture) -> extract_transforme (extraction) -> dashboard (graphiques)
"""

import logging
import os

from ingestion import raw
from processing import extract_transforme
from serving import dashboard

LOG_DIR = 'storage'
LOG_FILE = os.path.join(LOG_DIR, 'app.log')
DATA_DIR = './data'

# Le dossier du log doit exister avant de configurer logging
os.makedirs(LOG_DIR, exist_ok=True)

# Tous les modules écrivent dans le même fichier : storage/app.log
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
)

logger = logging.getLogger(__name__)


def run_pipeline():
    logger.info("Demarrage du pipeline")

    # 1. Lecture des fichiers
    rows = raw.to_rows(DATA_DIR)
    if not rows:
        logger.error("Aucune ligne lue dans " + DATA_DIR)
        print("Aucune ligne lue, voir " + LOG_FILE)
        return

    # 2. Extraction des tentatives sshd
    records = extract_transforme.extract(rows)
    if not records:
        logger.error("Aucune tentative sshd trouvee")
        return

    # 3. Affichage des graphiques
    dashboard.build_dashboard(records)

    logger.info("Fin du pipeline")


if __name__ == '__main__':
    try:
        run_pipeline()
    except Exception as e:
        # Filet de sécurité : toute erreur imprévue est enregistrée
        logger.exception("Erreur inattendue : " + str(e))
        print("Erreur, voir " + LOG_FILE)
