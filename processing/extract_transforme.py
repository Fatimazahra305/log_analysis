"""
    in : list of rows
    out : month, day, time, ip, user, status for sshd service
"""

import logging
import re

logger = logging.getLogger(__name__)

# Découpe une ligne de log en mois, jour, heure, serveur, service, message
pattern = re.compile(
    r'(?P<month>\w{3})\s+(?P<day>\d{1,2})\s+(?P<time>\d{2}:\d{2}:\d{2})'
    r'\s+(?P<server>\w+)\s+(?P<service>\w+)\[\d+\]:\s+(?P<message>.+)'
)

# Adresse IP : le mot qui suit "from"
ip_pattern = re.compile(r'from\s+(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')

# Utilisateur : le mot entre "for" ou "user" et "from" (peut être vide)
user_pattern = re.compile(r'(?:for|user) (?P<user>\S*) from')


def classify_event(message):
    """Renvoie 'Success', 'Failed', 'Invalid' ou None."""
    lowered = message.lower()

    if 'accepted password' in lowered or 'accepted publickey' in lowered:
        return 'Success'
    if 'failed password' in lowered:
        return 'Failed'
    # startswith : "Connection closed by invalid user ..." ne doit pas compter
    if lowered.startswith('invalid user'):
        return 'Invalid'
    return None


def extract_from_row(row):
    """Analyse une ligne : renvoie un dict, ou None si ce n'est pas une tentative sshd."""
    match = re.search(pattern, row)
    if not match:
        return None

    if match['service'] != 'sshd':
        return None

    message = match['message']
    status = classify_event(message)
    if status is None:
        return None

    ip_match = re.search(ip_pattern, message)
    if not ip_match:
        logger.warning("IP introuvable : " + message)
        return None

    user_match = re.search(user_pattern, message)
    user = user_match['user'] if user_match else ''
    if user == '':
        user = '(vide)'

    return {
        'month': match['month'],
        'day': match['day'],
        'time': match['time'],
        'ip': ip_match['ip'],
        'user': user,
        'status': status,
    }


def extract(rows):
    """Analyse toutes les lignes et garde seulement les tentatives sshd."""
    records = []
    for row in rows:
        parsed = extract_from_row(row)
        if parsed is not None:
            records.append(parsed)

    logger.info(str(len(records)) + " tentatives sshd extraites")
    return records


def count_by_user(records, status):
    """Pour un statut donne renvoie {utilisateur: nombre d'evnements}."""
    result = {}
    for record in records:
        if record['status'] == status:
            name = record['user']
            result[name] = result.get(name, 0) + 1
    return result


def count_by_ip(records, status):
    """Pour un statut donne, renvoie {ip: nombre d'evenements}."""
    result = {}
    for record in records:
        if record['status'] == status:
            address = record['ip']
            result[address] = result.get(address, 0) + 1
    return result


if __name__ == "__main__":
    from ingestion import raw

    # Le programme lit tout seul les fichiers de ./data
    records = extract(raw.to_rows('./data'))
    print("Tentatives sshd :", len(records))

    # Nombre d'événements par statut
    for status in ('Success', 'Failed', 'Invalid'):
        total = len([r for r in records if r['status'] == status])
        print(status, ":", total)

    print("Succes par utilisateur :", count_by_user(records, 'Success'))
    print("Invalid par utilisateur (top 5) :",
          sorted(count_by_user(records, 'Invalid').items(),
                 key=lambda x: x[1], reverse=True)[:5])
    print("Noms invalides differents :", len(count_by_user(records, 'Invalid')))
    print("IP differentes (Failed) :", len(count_by_ip(records, 'Failed')))