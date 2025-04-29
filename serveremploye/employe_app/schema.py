import graphene
from graphene_django import DjangoObjectType
from .models import Utilisateur, Information, Notification, Historique
from django.utils import timezone
import requests
from django.conf import settings


class UtilisateurType(DjangoObjectType):
    class Meta:
        model = Utilisateur
        fields = '__all__'


class InformationType(DjangoObjectType):
    class Meta:
        model = Information
        fields = '__all__'


class NotificationType(DjangoObjectType):
    class Meta:
        model = Notification
        fields = '__all__'


class HistoriqueType(DjangoObjectType):
    class Meta:
        model = Historique
        fields = '__all__'


class Query(graphene.ObjectType):
    # Utilisateurs
    all_utilisateurs = graphene.List(UtilisateurType)
    utilisateur_by_id = graphene.Field(UtilisateurType, id=graphene.Int(required=True))
    utilisateur_by_rh_id = graphene.Field(UtilisateurType, rh_id=graphene.Int(required=True))
    
    # Informations
    all_informations = graphene.List(InformationType)
    information_by_id = graphene.Field(InformationType, id=graphene.Int(required=True))
    information_by_rh_id = graphene.Field(InformationType, rh_id=graphene.Int(required=True))
    informations_by_utilisateur = graphene.List(InformationType, utilisateur_id=graphene.Int(required=True))
    
    # Notifications
    all_notifications = graphene.List(NotificationType)
    notification_by_id = graphene.Field(NotificationType, id=graphene.Int(required=True))
    notification_by_rh_id = graphene.Field(NotificationType, rh_id=graphene.Int(required=True))
    notifications_by_information = graphene.List(NotificationType, information_id=graphene.Int(required=True))
    
    # Historique
    all_historiques = graphene.List(HistoriqueType)
    historique_by_id = graphene.Field(HistoriqueType, id=graphene.Int(required=True))
    
    def resolve_all_utilisateurs(self, info):
        return Utilisateur.objects.all()
    
    def resolve_utilisateur_by_id(self, info, id):
        return Utilisateur.objects.get(utilisateur_id=id)
    
    def resolve_utilisateur_by_rh_id(self, info, rh_id):
        return Utilisateur.objects.get(rh_utilisateur_id=rh_id)
    
    def resolve_all_informations(self, info):
        return Information.objects.all()
    
    def resolve_information_by_id(self, info, id):
        return Information.objects.get(information_id=id)
    
    def resolve_information_by_rh_id(self, info, rh_id):
        return Information.objects.get(rh_information_id=rh_id)
    
    def resolve_informations_by_utilisateur(self, info, utilisateur_id):
        return Information.objects.filter(utilisateur_id=utilisateur_id)
    
    def resolve_all_notifications(self, info):
        return Notification.objects.all()
    
    def resolve_notification_by_id(self, info, id):
        return Notification.objects.get(notification_id=id)
    
    def resolve_notification_by_rh_id(self, info, rh_id):
        return Notification.objects.get(rh_notification_id=rh_id)
    
    def resolve_notifications_by_information(self, info, information_id):
        return Notification.objects.filter(information_id=information_id)
    
    def resolve_all_historiques(self, info):
        return Historique.objects.all()
    
    def resolve_historique_by_id(self, info, id):
        return Historique.objects.get(historique_id=id)


# Input types pour les mutations
class UtilisateurInfoInput(graphene.InputObjectType):
    id = graphene.Int(required=True)
    nom = graphene.String()
    prenom = graphene.String()
    email = graphene.String()


class InformationDetailsInput(graphene.InputObjectType):
    information_id = graphene.Int(required=True)
    utilisateur = graphene.Field(UtilisateurInfoInput)
    numero_employe = graphene.String()
    adresse = graphene.String()
    numero_assurance = graphene.String()
    cin = graphene.String()
    statut = graphene.Boolean()


class NotificationDetailsInput(graphene.InputObjectType):
    id = graphene.Int()
    objet = graphene.String()
    contenu = graphene.String()
    date_envoi = graphene.String()


class UpdateEmployeeInfoInput(graphene.InputObjectType):
    information_id = graphene.Int(required=True)
    utilisateur = graphene.Field(UtilisateurInfoInput, required=True)
    numero_employe = graphene.String()
    adresse = graphene.String()
    numero_assurance = graphene.String()
    cin = graphene.String()
    statut = graphene.Boolean()
    notification = graphene.Field(NotificationDetailsInput)


# Mutations
class UpdateEmployeeInfo(graphene.Mutation):
    class Arguments:
        input = UpdateEmployeeInfoInput(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, input):
        try:
            # Chercher si l'utilisateur existe déjà (par l'ID RH)
            utilisateur = None
            try:
                utilisateur = Utilisateur.objects.get(rh_utilisateur_id=input.utilisateur.id)
            except Utilisateur.DoesNotExist:
                # Créer un nouvel utilisateur
                utilisateur = Utilisateur(
                    rh_utilisateur_id=input.utilisateur.id,
                    nom=input.utilisateur.nom,
                    prenom=input.utilisateur.prenom,
                    email=input.utilisateur.email
                )
                utilisateur.save()
            
            # Chercher si l'information existe déjà (par l'ID RH)
            information = None
            try:
                information = Information.objects.get(rh_information_id=input.information_id)
                # Mettre à jour l'information existante
                information.numero_employe = input.numero_employe or information.numero_employe
                information.adresse = input.adresse or information.adresse
                information.numero_assurance = input.numero_assurance or information.numero_assurance
                information.cin = input.cin or information.cin
                if input.statut is not None:
                    information.statut = input.statut
                information.derniere_mise_a_jour = timezone.now()
            except Information.DoesNotExist:
                # Créer une nouvelle information
                information = Information(
                    utilisateur=utilisateur,
                    rh_information_id=input.information_id,
                    numero_employe=input.numero_employe,
                    adresse=input.adresse,
                    numero_assurance=input.numero_assurance,
                    cin=input.cin,
                    statut=input.statut if input.statut is not None else False
                )
            
            information.save()
            
            # Créer une notification si fournie
            if input.notification:
                notification = Notification(
                    information=information,
                    objet=input.notification.objet,
                    contenu=input.notification.contenu,
                    expediteur="Système RH",
                    destinataire=f"Employé {utilisateur.prenom} {utilisateur.nom}",
                    date_envoi=timezone.now() if not input.notification.date_envoi else input.notification.date_envoi,
                    statut=True,
                    rh_notification_id=input.notification.id
                )
                notification.save()
                
                # Enregistrer dans l'historique
                historique = Historique.objects.create(
                    type_action="reception_notification",
                    description=f"Notification reçue du système RH concernant la mise à jour d'information",
                    notification=notification
                )
                
                # Envoyer un feedback au serveur RH
                try:
                    response = requests.post(
                        settings.RH_SERVICE_URL,
                        json={"query": """
                            mutation ReceiveNotificationFeedback($notification_id: Int!, $status: Boolean!, $message: String, $source: String!) {
                                receiveNotificationFeedback(notificationId: $notification_id, status: $status, message: $message, source: $source) {
                                    success
                                    message
                                }
                            }
                        """,
                        "variables": {
                            "notification_id": input.notification.id,
                            "status": True,
                            "message": "Notification reçue et traitée avec succès",
                            "source": "employe"
                        }},
                        headers={"Content-Type": "application/json"}
                    )
                except Exception as e:
                    print(f"Erreur lors de l'envoi du feedback au serveur RH: {str(e)}")
            
            return UpdateEmployeeInfo(success=True, message="Information de l'employé mise à jour avec succès")
        except Exception as e:
            return UpdateEmployeeInfo(success=False, message=f"Erreur: {str(e)}")


class Mutation(graphene.ObjectType):
    update_employee_info = UpdateEmployeeInfo.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)