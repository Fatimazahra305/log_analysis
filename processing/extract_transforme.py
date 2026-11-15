"""
    in : list of rows
    out : month, day, time, ip, user, status for sshd service
"""

import logging
import re

logger = logging.getLogger(__name__)

# Votre pattern : découpe une ligne de log en mois, jour, heure, serveur, service, message
pattern = re.compile(
    r'(?P<month>\w{3})\s+(?P<day>\d{1,2})\s+(?P<time>\d{2}:\d{2}:\d{2})'
    r'\s+(?P<server>\w+)\s+(?P<service>\w+)\[\d+\]:\s+(?P<message>.+)'
)

# Adresse IP : le mot qui suit "from"
ip_pattern = re.compile(r'from\s+(?P<ip>\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})')

# Utilisateur : le mot juste avant "from"
user_pattern = re.compile(r'(?P<user>\S+)\s+from')


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
    if user_match:
        user = user_match['user']
    else:
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


if __name__ == "__main__":
    tests = [
        "May 24 00:04:36 ns sshd[1350968]: Connection closed by 127.0.0.1 port 40940 [preauth]",
        "May 24 00:09:01 ns CRON[1351002]: pam_unix(cron:session): session opened for user root(uid=0) by (uid=0)",
        "May 24 00:26:59 ns sshd[1351208]: Connection closed by invalid user  45.156.87.204 port 35940 [preauth]",
        "May 24 00:27:57 ns sshd[1351222]: Invalid user test from 45.156.87.204 port 41740",
        "May 24 00:28:00 ns sshd[1351222]: Failed password for invalid user test from 45.156.87.204 port 41740 ssh2",
    ]
    for t in tests:
        print(extract_from_row(t))