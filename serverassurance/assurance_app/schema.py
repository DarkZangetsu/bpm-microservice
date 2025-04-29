import graphene
from graphene_django import DjangoObjectType
from .models import CompagnieAssurance, Assure, InformationAssure, Notification, Historique
from django.utils import timezone
import requests
from django.conf import settings


class CompagnieAssuranceType(DjangoObjectType):
    class Meta:
        model = CompagnieAssurance
        fields = '__all__'


class AssureType(DjangoObjectType):
    class Meta:
        model = Assure
        fields = '__all__'


class InformationAssureType(DjangoObjectType):
    class Meta:
        model = InformationAssure
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
    # Compagnies
    all_compagnies = graphene.List(CompagnieAssuranceType)
    compagnie_by_id = graphene.Field(CompagnieAssuranceType, id=graphene.Int(required=True))
    compagnie_by_rh_id = graphene.Field(CompagnieAssuranceType, rh_id=graphene.Int(required=True))
    
    # Assurés
    all_assures = graphene.List(AssureType)
    assure_by_id = graphene.Field(AssureType, id=graphene.Int(required=True))
    assure_by_rh_id = graphene.Field(AssureType, rh_id=graphene.Int(required=True))
    assures_by_compagnie = graphene.List(AssureType, compagnie_id=graphene.Int(required=True))
    
    # Informations
    all_informations = graphene.List(InformationAssureType)
    information_by_id = graphene.Field(InformationAssureType, id=graphene.Int(required=True))
    information_by_rh_id = graphene.Field(InformationAssureType, rh_id=graphene.Int(required=True))
    informations_by_assure = graphene.List(InformationAssureType, assure_id=graphene.Int(required=True))
    
    # Notifications
    all_notifications = graphene.List(NotificationType)
    notification_by_id = graphene.Field(NotificationType, id=graphene.Int(required=True))
    notification_by_rh_id = graphene.Field(NotificationType, rh_id=graphene.Int(required=True))
    notifications_by_information = graphene.List(NotificationType, information_id=graphene.Int(required=True))
    
    # Historique
    all_historiques = graphene.List(HistoriqueType)
    historique_by_id = graphene.Field(HistoriqueType, id=graphene.Int(required=True))
    
    def resolve_all_compagnies(self, info):
        return CompagnieAssurance.objects.all()
    
    def resolve_compagnie_by_id(self, info, id):
        return CompagnieAssurance.objects.get(compagnie_id=id)
    
    def resolve_compagnie_by_rh_id(self, info, rh_id):
        return CompagnieAssurance.objects.get(rh_compagnie_id=rh_id)
    
    def resolve_all_assures(self, info):
        return Assure.objects.all()
    
    def resolve_assure_by_id(self, info, id):
        return Assure.objects.get(assure_id=id)
    
    def resolve_assure_by_rh_id(self, info, rh_id):
        return Assure.objects.get(rh_utilisateur_id=rh_id)
    
    def resolve_assures_by_compagnie(self, info, compagnie_id):
        return Assure.objects.filter(informations__compagnie_id=compagnie_id).distinct()
    
    def resolve_all_informations(self, info):
        return InformationAssure.objects.all()
    
    def resolve_information_by_id(self, info, id):
        return InformationAssure.objects.get(information_id=id)
    
    def resolve_information_by_rh_id(self, info, rh_id):
        return InformationAssure.objects.get(rh_information_id=rh_id)
    
    def resolve_informations_by_assure(self, info, assure_id):
        return InformationAssure.objects.filter(assure_id=assure_id)
    
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


class NotificationDetailsInput(graphene.InputObjectType):
    id = graphene.Int()
    objet = graphene.String()
    contenu = graphene.String()
    date_envoi = graphene.String()


class UpdateInsuranceInfoInput(graphene.InputObjectType):
    information_id = graphene.Int(required=True)
    utilisateur = graphene.Field(UtilisateurInfoInput, required=True)
    numero_employe = graphene.String()
    adresse = graphene.String()
    numero_assurance = graphene.String()
    cin = graphene.String()
    statut = graphene.Boolean()
    notification = graphene.Field(NotificationDetailsInput)


# Mutations
class UpdateInsuranceInfo(graphene.Mutation):
    class Arguments:
        input = UpdateInsuranceInfoInput(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, input):
        try:
            # Chercher si la compagnie existe (on suppose qu'il n'y a qu'une seule compagnie par serveur)
            compagnie = CompagnieAssurance.objects.first()
            if not compagnie:
                return UpdateInsuranceInfo(success=False, message="Aucune compagnie d'assurance configurée dans ce serveur")
            
            # Chercher si l'assuré existe déjà (par l'ID RH)
            assure = None
            try:
                assure = Assure.objects.get(rh_utilisateur_id=input.utilisateur.id)
                # Mise à jour éventuelle des infos de l'assuré
                if input.utilisateur.nom:
                    assure.nom = input.utilisateur.nom
                if input.utilisateur.prenom:
                    assure.prenom = input.utilisateur.prenom
                if input.utilisateur.email:
                    assure.email = input.utilisateur.email
                assure.save()
            except Assure.DoesNotExist:
                # Créer un nouvel assuré
                assure = Assure(
                    rh_utilisateur_id=input.utilisateur.id,
                    nom=input.utilisateur.nom,
                    prenom=input.utilisateur.prenom,
                    email=input.utilisateur.email
                )
                assure.save()
            
            # Chercher si l'information existe déjà (par l'ID RH)
            information = None
            try:
                information = InformationAssure.objects.get(rh_information_id=input.information_id)
                # Mettre à jour l'information existante
                information.numero_employe = input.numero_employe or information.numero_employe
                information.adresse = input.adresse or information.adresse
                information.numero_assurance = input.numero_assurance or information.numero_assurance
                information.cin = input.cin or information.cin
                if input.statut is not None:
                    information.statut = input.statut
                information.derniere_mise_a_jour = timezone.now()
            except InformationAssure.DoesNotExist:
                # Créer une nouvelle information
                information = InformationAssure(
                    assure=assure,
                    compagnie=compagnie,
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
                    destinataire=f"Compagnie d'assurance {compagnie.nom_compagnie}",
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
                            "message": "Notification reçue et traitée avec succès par la compagnie d'assurance",
                            "source": "assurance"
                        }},
                        headers={"Content-Type": "application/json"}
                    )
                except Exception as e:
                    print(f"Erreur lors de l'envoi du feedback au serveur RH: {str(e)}")
            
            return UpdateInsuranceInfo(success=True, message="Information de l'assuré mise à jour avec succès")
        except Exception as e:
            return UpdateInsuranceInfo(success=False, message=f"Erreur: {str(e)}")


class Mutation(graphene.ObjectType):
    update_insurance_info = UpdateInsuranceInfo.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)