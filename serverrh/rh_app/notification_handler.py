from .notification_service import NotificationService
from .models import Notification, Historique

class NotificationHandler:
    @staticmethod
    def handle_information_update(information, update_message=None):
        """
        Gère l'ensemble du processus de notification lors d'une mise à jour d'information
        
        Args:
            information: L'instance du modèle Information qui a été mise à jour
            update_message: Message optionnel détaillant la mise à jour
        
        Returns:
            Liste des résultats des notifications envoyées
        """
        # Message par défaut si aucun n'est fourni
        message = update_message or f"Les informations de {information.utilisateur.prenom} {information.utilisateur.nom} ont été mises à jour."
        
        # Créer une notification dans le système RH
        notification = Notification.objects.create(
            information=information,
            objet=f"Mise à jour d'informations employé",
            contenu=message,
            expediteur="Système RH",
            destinataire="Services concernés",
            statut=True
        )
        
        # Enregistrer dans l'historique
        Historique.objects.create(
            type_action="envoi_notification",
            description=f"Notification créée pour la mise à jour des informations de {information.utilisateur.nom} {information.utilisateur.prenom}",
            notification=notification
        )
        
        # Envoyer les notifications aux services externes
        results = NotificationService.send_notifications_for_information_update(information, message)
        
        # Journaliser les résultats
        for result in results:
            status = "réussie" if result["success"] else "échouée"
            Historique.objects.create(
                type_action=f"notification_{result['service']}",
                description=f"Notification au service {result['service']} {status}: {result['message']}",
                notification=notification
            )
        
        return results