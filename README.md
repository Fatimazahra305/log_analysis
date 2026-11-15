# Log Analysis

Un  projet Python pour analyser des logs SSH (auth.log). Le programme lit les fichiers, trouve les tentatives de connexion, cherche le pays des adresses IP et affiche trois graphiques.

# Les graphiques

1. Tentatives echouees par pays
2. Connexions reussies par utilisateur
3. Tentatives avec Invalid user


Le dossier data n'est pas sur GitHub. Il faut le creer et y mettre les fichiers de logs (auth.log.1, auth.log.2, auth.log.3.gz et auth.log..4.gz).

# organisation

- main.py : lance tout le programme et prépare les logs
- ingestion/raw.py : lit les fichiers, y compris les .gz
- processing/extract_transforme.py : garde les lignes sshd et les classe en Success, Failed ou Invalid
- processing/geo_location.py : trouve le pays d'une IP avec ipinfo.io
- serving/dashboard.py : dessine les graphiques avec matplotlib
- storage/app.log : fichier ou sont ecrites les erreurs et les infos

# Ce que j'ai trouve
Tentatives sshd : 14129
Success : 1
Failed : 10962
Invalid : 3166
Succès par utilisateur : {'adminesisa': 1}
Invalid par utilisateur (top 5) : [('admin', 407), ('esisa', 193), ('ubuntu', 144), ('user', 109), ('test', 82)]
Noms invalides différents : 959
IP différentes (Failed) : 1852

Sur mes 4 fichiers : 65 565 lignes lues, dont 14 129 tentatives sshd (10 962 échouées,959 un utilisateur invalide et 1 seule réussie).

« 3 166 tentatives avec un utilisateur invalide, venant de 959 noms différents »

Les attaques viennent surtout de Roumanie et des Pays-Bas. Les robots essaient souvent des noms comme admin ou ubuntu, et parfois aucun nom du tout (notevide dans le programme).

# Mes choix

- J'ai limite la recherche de pays aux 100 IP les plus actives, parce que ipinfo limite les requêtes gratuites. Les autres IP sont dans Autres.
- Une seule connexion a reussi, donc le deuxieme graphique n'a qu'une barre.
- Le programme met environ 40 secondes à cause des requêtes reseau.

# les erreurs

Chaque module écrit ses erreurs dans storage/app.log (dossier introuvable, fichier gzip abîme, probleme reseau...). J'ai teste le cas du dossier introuvable en renommant le dossier data.

# En resume voici ce que fait le projet:

Il lit tous les fichiers de logs du dossier data (auth.log.1, auth.log.2 et les fichiers compressés .gz).
Il regroupe toutes les lignes en une seule liste : 65 565 lignes au total.
Il ne garde que celles du service sshd, qui concernent les tentatives de connexion SSH.
Il classe chaque tentative en trois types : Success (connexion réussie), Failed (mot de passe échoué) ou Invalid (utilisateur inexistant).
Pour chaque tentative, il retient la date, l’heure, l’adresse IP, l’utilisateur et le statut : 14 129 tentatives en tout.
Il interroge ipinfo.io pour trouver le pays des 100 IP les plus actives, et regroupe les autres dans « Autres ».
Il affiche trois graphiques : échecs par pays, connexions réussies par utilisateur et tentatives avec Invalid user.
Il enregistre toutes les infos et les erreurs de chaque module dans le fichier storage/app.log