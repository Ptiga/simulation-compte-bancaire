# __<u>PROJET FAST API : Simulation compte bancaire</u>__


## Présentation du projet

Ce projet a pour but de créer des APIs sur FastAPI qui simulent le fonctionnement d’un compte bancaire.


**Sommaire**
* I - Présentation du projet
* II - Installation et lancement de l'application
* III - fonctionnalités
* IV - Crédits



## <u>I - Présentation du projet</u>

Ce projet a pour but de créer des APIs sur FastAPI qui simulent le fonctionnement d’un compte bancaire.

Dans le cadre de ce projet, les données ne seront pas stockées dans une base de donnée mais dans un fichier Json.


## <u>II - Installation et lancement de l'application</u>

### 1) Téléchargement du projet

Les projet est téléchargeable via le lien suivant : [https://github.com/Ptiga/simulation-compte-bancaire.git](https://github.com/Ptiga/simulation-compte-bancaire.git)

Une fois téléchargé, décompressez-le dans le dossier de votre choix (que nous appellerons [Adresse]).


### 2) Composition du projet


L'arborescence du dossier décompressé est la suivante :
```jsx
sheldon-tournament (répertoire principal [main_folder])
    __pycache__
    .gitignore
    __init__.py
    account_utility.py
    app.py
    convert_utility.py
    database.py
    main.py
    README.md
```


### 3) Lancement de l'application


Une fois le projet décompressé, ouvrez une invite de commande puis rendez-vous dans le répertoire principal du projet :
```jsx
"cd [Adresse]\[main_folder]"
```

Dans la fenêtre d'invite de commande, saisissez la commande suivante pour lancer le serveur : 
```jsx
python -m uvicorn app:app --reload
```

une fois le serveur démarré, saisissez l'adresse suivante dans votre navigateur préféré pour accéder au Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Vous êtes désormais prêt à tester les différentes fonctionnalités de l'outil.


## <u>III - fonctionnalités utilisables</u>

Voici, pour l'instant, les différentes fonctionnalités présentes dans l'outil:
* Liste des clients
* Création d'un client
* Lister un seul client
* Mise à jour d'un client
* Suppression d'un client
* Obtenir tous les comptes d'un client
* Créer un compte à un client
* Obtenir un compte d'un client
* Suppression du compte d'un client
* Mise à jour du solde d'un client
* Obtenir le détail d'un transaction
* Création d'une transaction
* Mise à jour d'une transaction
* Annulation d'une transaction
* Transfert entre deux comptes d'un client


## <u>IV - Credits</u>

Projet scolaire effectué en mai 2022 dans le cadre d'un formation reskilling (module Python) avec l'EFREI.

**Auteur**: Aurélien
**Version**: 0

