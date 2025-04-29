from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.html import strip_tags
import requests
import json
from django.conf import settings
        
class Utilisateur(models.Model):
    utilisateur_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    nom = models.CharField(max_length=255, null=True, blank=True)
    prenom = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    role = models.CharField(max_length=255, null=True, blank=True)
    mot_de_passe = models.CharField(max_length=255)
    
    def __str__(self):
        return f"{self.prenom} {self.nom}"
    
    def save(self, *args, **kwargs):
        # Synchroniser les informations avec le User associé
        if self.user and (self.email or self.nom or self.prenom):
            if self.email:
                self.user.email = self.email
            if self.nom:
                self.user.last_name = self.nom
            if self.prenom:
                self.user.first_name = self.prenom
            self.user.save()
        super().save(*args, **kwargs)


class Compagnie_Assurance(models.Model):
    compagnie_id = models.AutoField(primary_key=True)
    nom_compagnie = models.CharField(max_length=255, null=True, blank=True)
    adresse_compagnie = models.CharField(max_length=255, null=True, blank=True)
    email_compagnie = models.CharField(max_length=255, null=True, blank=True)
    api_url = models.URLField(max_length=255, null=True, blank=True, 
                           help_text="URL de l'API GraphQL de la compagnie d'assurance")
    
    def __str__(self):
        return self.nom_compagnie if self.nom_compagnie else f"Compagnie {self.pk}"


class Information(models.Model):
    information_id = models.AutoField(primary_key=True)
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='informations')
    numero_employe = models.CharField(max_length=255, null=True, blank=True)
    adresse = models.CharField(max_length=255, null=True, blank=True)
    numero_assurance = models.CharField(max_length=255, null=True, blank=True)
    cin = models.CharField(max_length=255, null=True, blank=True)
    statut = models.BooleanField(null=False)
    compagnie_assurance = models.ForeignKey(Compagnie_Assurance, on_delete=models.SET_NULL, 
                                         null=True, blank=True, related_name='informations')
    email_notification = models.EmailField(max_length=255, null=True, blank=True, 
                                        help_text="Email où envoyer la notification pour cette information")
    
    def __str__(self):
        return f"Info de {self.utilisateur}"
    
    def save(self, *args, **kwargs):
        creation = not self.pk
        
        if not creation:
            ancien_etat = Information.objects.get(pk=self.pk)
            ancien_statut = ancien_etat.statut
        else:
            ancien_statut = False
            
        super().save(*args, **kwargs)
        
        if (creation and self.statut) or (not creation and not ancien_statut and self.statut):
            notification = self.creer_notification()
            self.notifier_microservices(notification)
    
    def creer_notification(self):
        """Crée une notification lorsqu'une information est ajoutée avec statut True ou passe de False à True"""
        historique = Historique.objects.create(
            type_action="envoye",
            description=f"Information {self.information_id} confirmée pour l'utilisateur {self.utilisateur}"
        )
        
        destinataire = self.email_notification if self.email_notification else "Administration"
        
        notification = Notification.objects.create(
            historique=historique,
            information=self,
            objet="Confirmation d'information",
            contenu=f"L'information {self.information_id} pour {self.utilisateur} a été confirmée et est maintenant à jour",
            expediteur="Système",
            destinataire=destinataire,
            date_envoi=timezone.now(),
            statut=True
        )
        
        email_recipients = []
        if self.email_notification:
            email_recipients.append(self.email_notification)
        
        # Ajouter l'email de la compagnie d'assurance s'il existe
        if self.compagnie_assurance and self.compagnie_assurance.email_compagnie:
            email_recipients.append(self.compagnie_assurance.email_compagnie)
        
        if email_recipients:
            self.envoyer_email_notification(notification, email_recipients)
        
        return notification
    
    def notifier_microservices(self, notification):
        """Envoie les notifications aux microservices employé et assurance"""
       
        # Données à envoyer
        data = {
            "informationId": self.information_id,  # Utiliser camelCase pour GraphQL
            "utilisateur": {
                "id": self.utilisateur.utilisateur_id,
                "nom": self.utilisateur.nom,
                "prenom": self.utilisateur.prenom,
                "email": self.utilisateur.email
            },
            "numeroEmploye": self.numero_employe,  # Utiliser camelCase
            "adresse": self.adresse,
            "numeroAssurance": self.numero_assurance,  # Utiliser camelCase
            "cin": self.cin,
            "statut": self.statut,
            "notification": {
                "id": notification.notification_id,
                "objet": notification.objet,
                "contenu": notification.contenu,
                "dateEnvoi": notification.date_envoi.isoformat(),  # Utiliser camelCase
            }
        }
        
        # Notification au microservice Employé
        try:
            # S'assurer que l'URL est correcte
            employee_url = settings.EMPLOYEE_SERVICE_URL
            if not employee_url.endswith('/'):
                employee_url += '/'
            employee_url += 'graphql/'
            
            print(f"Envoi de requête GraphQL au service Employé: {employee_url}")
            print(f"Payload: {json.dumps(data, indent=2)}")
            
            response = requests.post(
                employee_url,
                json={
                    "query": """
                        mutation UpdateEmployeeInfo($input: UpdateEmployeeInfoInput!) {
                            updateEmployeeInfo(input: $input) {
                                success
                                message
                            }
                        }
                    """,
                    "variables": {
                        "input": data
                    }
                },
                headers={"Content-Type": "application/json"}
            )
            
            print(f"Réponse du service Employé: {response.status_code} - {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                if "data" in result and "updateEmployeeInfo" in result["data"]:
                    success = result["data"]["updateEmployeeInfo"]["success"]
                    message = result["data"]["updateEmployeeInfo"]["message"]
                    print(f"Traitement réussi: success={success}, message={message}")
                    
                notification.enregistrer_dans_historique(
                    type_action="notification_employee_success",
                    description="Notification envoyée avec succès au service Employé"
                )
            else:
                notification.enregistrer_dans_historique(
                    type_action="notification_employee_failed",
                    description=f"Échec de l'envoi de notification au service Employé: {response.text}"
                )
        except Exception as e:
            print(f"ERREUR lors de l'envoi de notification au service Employé: {str(e)}")
            notification.enregistrer_dans_historique(
                type_action="notification_employee_error",
                description=f"Erreur lors de l'envoi de notification au service Employé: {str(e)}"
            )
        
        # Notification au microservice Assurance (si lié à une compagnie d'assurance)
        if self.compagnie_assurance:
            try:
                # S'assurer que l'URL est correcte pour l'API de la compagnie d'assurance
                insurance_url = settings.INSURANCE_SERVICE_URL
                if not insurance_url.endswith('/'):
                    insurance_url += '/'
                insurance_url += 'graphql/'
                
                print(f"Envoi de requête GraphQL au service Assurance: {insurance_url}")
                print(f"Payload: {json.dumps(data, indent=2)}")
                
                response = requests.post(
                    insurance_url,
                    json={
                        "query": """
                            mutation UpdateInsuranceInfo($input: UpdateInsuranceInfoInput!) {
                                updateInsuranceInfo(input: $input) {
                                    success
                                    message
                                }
                            }
                        """,
                        "variables": {
                            "input": data
                        }
                    },
                    headers={"Content-Type": "application/json"}
                )
                
                print(f"Réponse du service Assurance: {response.status_code} - {response.text}")
                
                if response.status_code == 200:
                    result = response.json()
                    if "data" in result and "updateInsuranceInfo" in result["data"]:
                        success = result["data"]["updateInsuranceInfo"]["success"]
                        message = result["data"]["updateInsuranceInfo"]["message"]
                        print(f"Traitement réussi: success={success}, message={message}")
                        
                    notification.enregistrer_dans_historique(
                        type_action="notification_insurance_success",
                        description=f"Notification envoyée avec succès à la compagnie {self.compagnie_assurance.nom_compagnie}"
                    )
                else:
                    notification.enregistrer_dans_historique(
                        type_action="notification_insurance_failed",
                        description=f"Échec de l'envoi de notification à la compagnie {self.compagnie_assurance.nom_compagnie}: {response.text}"
                    )
            except Exception as e:
                print(f"ERREUR lors de l'envoi de notification au service Assurance: {str(e)}")
                notification.enregistrer_dans_historique(
                    type_action="notification_insurance_error",
                    description=f"Erreur lors de l'envoi de notification à la compagnie {self.compagnie_assurance.nom_compagnie}: {str(e)}"
                )
    
    def envoyer_email_notification(self, notification, recipients):
        """Envoie un email de notification aux destinataires"""
        if not recipients:
            notification.enregistrer_dans_historique(
                type_action="email_non_envoyé", 
                description="Aucune adresse email de notification définie"
            )
            return
        
        sujet = notification.objet
        message_html = f"""
        <html>
        <head></head>
        <body>
            <h2>Confirmation de mise à jour d'information</h2>
            <p>Bonjour,</p>
            <p>{notification.contenu}</p>
            <p>Détails de l'information mise à jour pour {self.utilisateur.prenom} {self.utilisateur.nom}:</p>
            <ul>
                <li>Numéro d'employé: {self.numero_employe or 'Non spécifié'}</li>
                <li>Adresse: {self.adresse or 'Non spécifiée'}</li>
                <li>Numéro d'assurance: {self.numero_assurance or 'Non spécifié'}</li>
                <li>CIN: {self.cin or 'Non spécifiée'}</li>
            </ul>
            <p>Cordialement,<br>L'équipe RH</p>
        </body>
        </html>
        """
        message_texte = strip_tags(message_html)
        
        try:
            print(f"Tentative d'envoi d'email à {', '.join(recipients)}")
            
            # Utiliser la fonction d'envoi d'email de Django
            from django.core.mail import send_mail
            send_mail(
                subject=sujet,
                message=message_texte,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                html_message=message_html,
                fail_silently=False,  
            )
            
            print(f"Email envoyé avec succès à {', '.join(recipients)}")
            
            notification.enregistrer_dans_historique(
                type_action="email_envoye", 
                description=f"Email de notification envoyé à {', '.join(recipients)}"
            )
            
        except Exception as e:
            print(f"ERREUR d'envoi d'email: {str(e)}")
            notification.enregistrer_dans_historique(
                type_action="email_echec", 
                description=f"Échec de l'envoi d'email: {str(e)}"
            )


class Historique(models.Model):
    historique_id = models.AutoField(primary_key=True)
    date = models.DateTimeField(auto_now_add=True)
    type_action = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
     
    def __str__(self):
        return f"Historique {self.pk} ({self.date})"


class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    historique = models.ForeignKey(Historique, on_delete=models.CASCADE, related_name='notifications')
    information = models.ForeignKey(Information, on_delete=models.CASCADE, related_name='notifications')
    objet = models.CharField(max_length=255, null=True, blank=True)
    contenu = models.CharField(max_length=255, null=True, blank=True)
    expediteur = models.CharField(max_length=255, null=True, blank=True)
    destinataire = models.CharField(max_length=255, null=True, blank=True)
    date_envoi = models.DateTimeField(null=True, blank=True) 
    statut = models.BooleanField(null=True)
    
    def __str__(self):
        return f"{self.objet} ({self.date_envoi})"
    
    def enregistrer_dans_historique(self, type_action="envoi", description=None):
        """Méthode pour enregistrer une action dans l'historique"""
        if not description:
            description = f"Notification '{self.objet}' {type_action} à {self.destinataire}"
        
        # Création d'un nouvel historique lié à cette notification
        Historique.objects.create(
            type_action=type_action,
            description=description
        )