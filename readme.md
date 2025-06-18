Application de Gestion des Emplois du Temps
Cette application web, développée avec Flask, permet de gérer les emplois du temps académiques. Les administrateurs peuvent ajouter, modifier et supprimer des créneaux horaires pour les cours, enseignants, salles et groupes, tandis que les enseignants et les étudiants ont accès à des tableaux de bord spécifiques.
Table des matières

Prérequis
Installation
Exécution du projet
Comptes par défaut
Structure du projet
Dépannage

Prérequis
Assurez-vous d'avoir installé :

Python (version 3.8 ou supérieure)
pip (gestionnaire de paquets Python)
Virtualenv (recommandé pour des environnements isolés)
MySQL (serveur de base de données, version 8.0 ou supérieure)
Git (pour cloner le dépôt)

Les dépendances du projet sont listées dans requirements.txt :
Flask
Flask-Login
Flask-SQLAlchemy
pandas
reportlab
matplotlib

Installation

Cloner le dépôt
git clone https://github.com/votre-nom-utilisateur/gestion-emplois-temps.git
cd gestion-emplois-temps


Configurer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sous Windows : venv\Scripts\activate


Installer les dépendances
pip install -r requirements.txt

Installez également le pilote MySQL pour Python :
pip install pymysql

Cela permet à Flask-SQLAlchemy de se connecter à MySQL.

Configurer MySQL

Assurez-vous que le serveur MySQL est en cours d'exécution.
Créez la base de données emploi_temps_db dans MySQL :mysql -u votre-utilisateur -p
CREATE DATABASE emploi_temps_db;

Remplacez votre-utilisateur par votre nom d'utilisateur MySQL et entrez votre mot de passe lorsque demandé.


Configurer les variables d'environnementCréez un fichier .env à la racine du projet avec le contenu suivant :
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=votre-clé-secrète
DATABASE_URL=mysql+pymysql://votre-utilisateur:votre-mot-de-passe@localhost/emploi_temps_db


Remplacez votre-clé-secrète par une chaîne aléatoire sécurisée.
Remplacez votre-utilisateur et votre-mot-de-passe par vos identifiants MySQL.


Configurer la base de donnéesInitialisez la base de données avec les commandes suivantes :
python -m flask db init
python -m flask db migrate
python -m flask db upgrade

Si un script de remplissage (seed.py) est disponible pour ajouter des données initiales (filières, cours, enseignants, utilisateurs), exécutez :
python seed.py



Exécution du projet

Activer l'environnement virtuel (si ce n'est pas déjà fait)
source venv/bin/activate  # Sous Windows : venv\Scripts\activate


Démarrer le serveur de développement Flask
python -m flask run

Alternativement, exécutez directement :
python app.py


Accéder à l'applicationOuvrez votre navigateur et allez à :
http://localhost:5000


Interface de connexion : /auth/login
Tableau de bord administrateur : /admin/dashboard
Gestion des emplois du temps : /admin/schedule



Comptes par défaut
Lors de la première configuration, l'application crée des comptes par défaut pour permettre un accès initial. Utilisez les identifiants suivants pour vous connecter :

Administrateur
Nom d'utilisateur : admin
Mot de passe : admin


Enseignant
Nom d'utilisateur : abdelkhalk
Mot de passe : password


Étudiant
Nom d'utilisateur : khalid
Mot de passe : khalid



Important : Après la première connexion, modifiez les mots de passe par défaut via les paramètres du profil utilisateur pour des raisons de sécurité.
Si les comptes ne sont pas créés ou si la connexion échoue, exécutez le script de remplissage (s'il existe) :


devloper par abdelkhalk essaid