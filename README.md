# SAE_Projet_etudiant
**Contributeurs :** Yassine Belaarous, Ilane Riotte, Corentin Lacoume et Clément Vignon Chaudey

## Présentation
Cette application a été développée dans le cadre de la SAE Étudiant. Elle permet pour l'instant de créer des profils d'assuré, ajouter des logements, pièces et biens.
Certaines fonctionnalités sont encore en développement et arriverons dans les prochaines releases.

## Identifiants de tests pour l'application

- paul.martin@example.com / hashed_pwd6
- marie.durand@example.com / hashed_pwd3
- luc.lefebvre@example.com / hashed_pwd4

## Installation et lancement
Suivez ces étapes pour exécuter l'application sur votre machine :

1. **Cloner le dépôt**  
   `git clone <URL_DU_REPO>`  
   Remplacez `<URL_DU_REPO>` par l’URL du dépôt Git.

2. **Préparer l'environnement**  
   - Rendez-vous dans le dossier de l’application : `cd monApp`  
   - Créez un environnement virtuel : `python -m venv venv`  
   - Activez l’environnement :  
     - Windows : `venv\Scripts\activate`  
     - macOS/Linux : `source venv/bin/activate`  
   - Installez les dépendances : `pip install -r requirements.txt`
   - Chargez la base de données : `flask loaddb data/data.yml`

3. **Lancer l’application**
   `flask run`  
   L’application sera accessible à l’adresse indiquée dans le terminal (généralement `http://127.0.0.1:5000`).

5. **Se connecter**  
   Utilisez les identifiants fournis en haut du README pour accéder à l’application.
