# Log Analysis

Un  projet Python pour analyser des logs SSH (auth.log). Le programme lit les fichiers, trouve les tentatives de connexion, cherche le pays des adresses IP et affiche trois graphiques.

## Les graphiques

1. Tentatives echouees par pays
2. Connexions reussies par utilisateur
3. Tentatives avec Invalid user


Le dossier data n'est pas sur GitHub. Il faut le creer et y mettre les fichiers de logs (auth.log.1, auth.log.2, auth.log.3.gz et auth.log..4.gz).

## Organisation

- main.py : lance tout le programme et prépare les logs
- ingestion/raw.py : lit les fichiers, y compris les .gz
- processing/extract_transforme.py : garde les lignes sshd et les classe en Success, Failed ou Invalid
- processing/geo_location.py : trouve le pays d'une IP avec ipinfo.io
- serving/dashboard.py : dessine les graphiques avec matplotlib
- storage/app.log : fichier ou sont ecrites les erreurs et les infos

## Ce que j'ai trouvé

Sur mes 4 fichiers : 65 565 lignes lues, dont 14 129 tentatives sshd (10 962 échouées, 3 166 avec un utilisateur invalide et 1 seule réussie).

Les attaques viennent surtout de Roumanie et des Pays-Bas. Les robots essaient des noms comme admin, user, ubuntu ou test.

## Mes choix

- J'ai limite la recherche de pays aux 100 IP les plus actives, parce que ipinfo limite les requêtes gratuites. Les autres IP sont dans Autres.
- Une seule connexion a reussi, donc le deuxieme graphique n'a qu'une barre.
- Le programme met environ 40 secondes à cause des requêtes reseau.

## Les erreurs

Chaque module écrit ses erreurs dans storage/app.log (dossier introuvable, fichier gzip abîme, probleme reseau...). J'ai teste le cas du dossier introuvable en renommant le dossier data.