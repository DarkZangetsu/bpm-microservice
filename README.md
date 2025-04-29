```markdown
# 🧩 Microservices RH, Employé et Assurance – Application GraphQL

Ce projet est une application composée de trois services distincts :  
- **RH Service** (`http://localhost:8000/graphql/`)
- **Employé Service** (`http://localhost:8001/graphql/`)
- **Assurance Service** (`http://localhost:8002/graphql/`)

Chaque service expose une API GraphQL et est orchestré via Docker Compose.

---

## 🚀 Lancement rapide avec Docker Compose

1. Assurez-vous d’avoir Docker et Docker Compose installés.
2. Démarrez les services :
   ```bash
   docker compose up --build -d
   ```
3. Une fois les services en ligne, utilisez [Postman](https://www.postman.com/) ou tout outil de test GraphQL pour interagir avec les APIs.

---

## 🔍 Étapes de test GraphQL

### 1️⃣ Créer un utilisateur (sur le service RH)
```graphql
mutation CreateUtilisateur {
  createUtilisateur(
    input: {
      nom: "Dupont"
      prenom: "Jean"
      email: "jean.dupont@example.com"
      role: "EMPLOYE"
      motDePasse: "1234"
    }
  ) {
    utilisateur {
      utilisateurId
      nom
      prenom
      email
      role
      motDePasse
    }
  }
}
```

---

### 2️⃣ Créer une compagnie d’assurance (sur le service Assurance)
```graphql
mutation CreateCompagnie {
  createCompagnie(
    input: {
      nomCompagnie: "AssuranceCorp"
      adresseCompagnie: "123 Rue de l'Assurance"
      emailCompagnie: "contact@assurancecorp.com"
      apiUrl: "http://localhost:8002/graphql"
    }
  ) {
    compagnie {
      compagnieId
      nomCompagnie
      adresseCompagnie
      emailCompagnie
      apiUrl
    }
  }
}
```

---

### 3️⃣ Créer une information d’employé (sur le service Employé)
```graphql
mutation CreateInformation {
  createInformation(
    input: {
      utilisateurId: 1
      numeroEmploye: "EMP123"
      adresse: "456 Rue des Employés"
      numeroAssurance: "ASS456"
      cin: "ID789"
      statut: true
      compagnieAssuranceId: 1
      emailNotification: "jean.dupont@example.com"
    }
  ) {
    information {
      informationId
      numeroEmploye
      adresse
      numeroAssurance
      cin
      statut
      emailNotification
      utilisateur {
        utilisateurId
        nom
        prenom
      }
      compagnieAssurance {
        compagnieId
      }
    }
  }
}
```

---

### 4️⃣ Récupérer tous les historiques (service RH ou centralisé)
```graphql
query AllHistoriques {
  allHistoriques {
    historiqueId
    date
    typeAction
    description
  }
}
```

---

### 5️⃣ Lister les compagnies et assurés (sur le service Assurance)
```graphql
query AllAssures {
  allCompagnies {
    compagnieId
    nomCompagnie
    adresseCompagnie
    emailCompagnie
    apiUrl
    rhCompagnieId
    assures {
      informationId
      numeroEmploye
      adresse
      numeroAssurance
      cin
      statut
      rhInformationId
      derniereMiseAJour
      notifications {
        notificationId
        objet
        contenu
        expediteur
        destinataire
        dateEnvoi
        dateReception
        statut
        rhNotificationId
      }
    }
  }
}
```

---

### 6️⃣ Récupérer tous les utilisateurs (sur le service RH)
```graphql
query AllUtilisateurs {
  allUtilisateurs {
    utilisateurId
    nom
    prenom
    email
    role
    rhUtilisateurId
    informations {
      informationId
      numeroEmploye
      adresse
      numeroAssurance
      cin
      statut
      rhInformationId
      derniereMiseAJour
    }
  }
}
```

---

## ⚙️ Installation manuelle (sans Docker)

1. **Créer un environnement virtuel** pour chaque service :
   ```bash
   python -m venv env
   source env/bin/activate  # Linux/macOS
   env\Scripts\activate     # Windows
   ```

2. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

3. **Appliquer les migrations** :
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **(Service Assurance uniquement)** : Initialiser la compagnie par défaut :
   ```bash
   python manage.py create_default_company
   ```

5. **Lancer chaque serveur** :
   ```bash
   python manage.py runserver 0.0.0.0:8000  # RH
   python manage.py runserver 0.0.0.0:8001  # Employé
   python manage.py runserver 0.0.0.0:8002  # Assurance
   ```

---

## 📁 Structure du projet

```
microservices/
├── serverassurance/
├── serveremploye/
├── serverrh/
├── docker-compose.yml
└── README.md
```

---

## 📫 Contact

Pour toute question, n’hésitez pas à me contacter.

---

```
