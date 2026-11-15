import gzip
import logging
from pathlib import Path

"""
Read from data all files
in: data [directory]
out: list of rows
"""
logger = logging.getLogger(__name__)

def to_rows(path: str):
    rows = []
    data_dir = Path(path)

    try:
        files = sorted(data_dir.iterdir())
    except FileNotFoundError:
        logger.error(f"{path} : dossier introuvable")
        return rows
    except PermissionError:
        logger.error(f"{path} : permission refusée")
        return rows
    except NotADirectoryError:
        logger.error(f"{path} : ce n'est pas un dossier")
        return rows

    for file_path in files:

        if not file_path.is_file():
            continue

        try:
           
            if file_path.suffix == '.gz':
                with gzip.open(file_path, mode='rt', encoding='utf-8', errors='replace') as f:
                    lines = f.readlines()
            else:
                with open(file_path, mode='r', encoding='utf-8', errors='replace') as f:
                    lines = f.readlines()

            rows.extend(lines)
            logger.info(f"{file_path.name} : {len(lines)} lignes lues")

        except PermissionError:
            logger.error(f"{file_path.name} : permission refusée")
        except gzip.BadGzipFile:
            logger.error(f"{file_path.name} : fichier gzip corrompu")
        except EOFError:
            logger.error(f"{file_path.name} : fichier gzip incomplet")
        except OSError as e:
            logger.error(f"{file_path.name} : erreur de lecture ({e})")

    return rows


if __name__ == '__main__':
    data = to_rows('./data')
    print(len(data))