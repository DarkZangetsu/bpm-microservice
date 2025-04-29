import requests
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    def notify_employee_service(information, notification=None):
        """
        Envoie une notification au service des employés
        """
        try:
            # Préparation des données
            utilisateur_data = {
                "id": information.utilisateur.utilisateur_id,
                "nom": information.utilisateur.nom,
                "prenom": information.utilisateur.prenom,
                "email": information.utilisateur.email
            }
            
            mutation_input = {
                "information_id": information.information_id,
                "utilisateur": utilisateur_data,
                "numero_employe": information.numero_employe,
                "adresse": information.adresse,
                "numero_assurance": information.numero_assurance,
                "cin": information.cin,
                "statut": information.statut
            }
            
            # Ajout de la notification si elle existe
            if notification:
                mutation_input["notification"] = {
                    "id": notification.notification_id,
                    "objet": notification.objet,
                    "contenu": notification.contenu,
                    "date_envoi": notification.date_envoi.isoformat() if notification.date_envoi else None
                }
            
            # Construction de la requête GraphQL
            query = """
                mutation UpdateEmployeeInfo($input: UpdateEmployeeInfoInput!) {
                    updateEmployeeInfo(input: $input) {
                        success
                        message
                    }
                }
            """
            
            # Envoi de la requête
            response = requests.post(
                settings.EMPLOYEE_SERVICE_URL,
                json={"query": query, "variables": {"input": mutation_input}},
                headers={"Content-Type": "application/json"}
            )
            
            result = response.json()
            if "errors" in result:
                logger.error(f"Erreur lors de la notification au service des employés: {result['errors']}")
                return False, result['errors']
            
            return True, "Notification envoyée avec succès au service des employés"
        
        except Exception as e:
            logger.error(f"Exception lors de la notification au service des employés: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def notify_insurance_service(information, notification=None):
        """
        Envoie une notification au service des assurances
        """
        try:
            # Vérifier que l'information a une compagnie d'assurance associée
            if not information.compagnie_assurance:
                return False, "Aucune compagnie d'assurance associée à cette information"
            
            # Préparation des données
            utilisateur_data = {
                "id": information.utilisateur.utilisateur_id,
                "nom": information.utilisateur.nom,
                "prenom": information.utilisateur.prenom,
                "email": information.utilisateur.email
            }
            
            mutation_input = {
                "information_id": information.information_id,
                "utilisateur": utilisateur_data,
                "numero_employe": information.numero_employe,
                "adresse": information.adresse,
                "numero_assurance": information.numero_assurance,
                "cin": information.cin,
                "statut": information.statut
            }
            
            # Ajout de la notification si elle existe
            if notification:
                mutation_input["notification"] = {
                    "id": notification.notification_id,
                    "objet": notification.objet,
                    "contenu": notification.contenu,
                    "date_envoi": notification.date_envoi.isoformat() if notification.date_envoi else None
                }
            
            # Construction de la requête GraphQL
            query = """
                mutation UpdateInsuranceInfo($input: UpdateInsuranceInfoInput!) {
                    updateInsuranceInfo(input: $input) {
                        success
                        message
                    }
                }
            """
            
            # Envoi de la requête
            response = requests.post(
                settings.ASSURANCE_SERVICE_URL,
                json={"query": query, "variables": {"input": mutation_input}},
                headers={"Content-Type": "application/json"}
            )
            
            result = response.json()
            if "errors" in result:
                logger.error(f"Erreur lors de la notification au service des assurances: {result['errors']}")
                return False, result['errors']
            
            return True, "Notification envoyée avec succès au service des assurances"
        
        except Exception as e:
            logger.error(f"Exception lors de la notification au service des assurances: {str(e)}")
            return False, str(e)

    @staticmethod
    def send_notifications_for_information_update(information, notification_text=None):
        """
        Envoie des notifications à tous les services concernés lors d'une mise à jour d'information
        """
        results = []
        notification = None
        
        # Créer une notification si un texte est fourni
        if notification_text:
            # Créer la notification dans le modèle Notification (supposant l'existence de ce modèle)
            from .models import Notification
            
            notification = Notification.objects.create(
                information=information,
                objet=f"Mise à jour des informations de {information.utilisateur.prenom} {information.utilisateur.nom}",
                contenu=notification_text,
                expediteur="Système RH",
                destinataire="Services concernés",
                statut=True
            )
        
        # Notifier le service des employés
        success_employee, message_employee = NotificationService.notify_employee_service(information, notification)
        results.append({"service": "employe", "success": success_employee, "message": message_employee})
        
        # Notifier le service des assurances si une compagnie est associée
        if information.compagnie_assurance:
            success_insurance, message_insurance = NotificationService.notify_insurance_service(information, notification)
            results.append({"service": "assurance", "success": success_insurance, "message": message_insurance})
        
        return results