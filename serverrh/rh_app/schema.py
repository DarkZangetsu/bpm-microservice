import graphene
from graphene_django import DjangoObjectType
from .models import Utilisateur, Information, Compagnie_Assurance, Notification, Historique
from django.utils import timezone


class UtilisateurType(DjangoObjectType):
    class Meta:
        model = Utilisateur
        fields = '__all__'


class CompagnieAssuranceType(DjangoObjectType):
    class Meta:
        model = Compagnie_Assurance
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
    
    # Informations
    all_informations = graphene.List(InformationType)
    information_by_id = graphene.Field(InformationType, id=graphene.Int(required=True))
    informations_by_utilisateur = graphene.List(InformationType, utilisateur_id=graphene.Int(required=True))
    
    # Compagnies d'assurance
    all_compagnies = graphene.List(CompagnieAssuranceType)
    compagnie_by_id = graphene.Field(CompagnieAssuranceType, id=graphene.Int(required=True))
    
    # Notifications
    all_notifications = graphene.List(NotificationType)
    notification_by_id = graphene.Field(NotificationType, id=graphene.Int(required=True))
    notifications_by_information = graphene.List(NotificationType, information_id=graphene.Int(required=True))
    
    # Historique
    all_historiques = graphene.List(HistoriqueType)
    historique_by_id = graphene.Field(HistoriqueType, id=graphene.Int(required=True))
    
    def resolve_all_utilisateurs(self, info):
        return Utilisateur.objects.all()
    
    def resolve_utilisateur_by_id(self, info, id):
        return Utilisateur.objects.get(utilisateur_id=id)
    
    def resolve_all_informations(self, info):
        return Information.objects.all()
    
    def resolve_information_by_id(self, info, id):
        return Information.objects.get(information_id=id)
    
    def resolve_informations_by_utilisateur(self, info, utilisateur_id):
        return Information.objects.filter(utilisateur_id=utilisateur_id)
    
    def resolve_all_compagnies(self, info):
        return Compagnie_Assurance.objects.all()
    
    def resolve_compagnie_by_id(self, info, id):
        return Compagnie_Assurance.objects.get(compagnie_id=id)
    
    def resolve_all_notifications(self, info):
        return Notification.objects.all()
    
    def resolve_notification_by_id(self, info, id):
        return Notification.objects.get(notification_id=id)
    
    def resolve_notifications_by_information(self, info, information_id):
        return Notification.objects.filter(information_id=information_id)
    
    def resolve_all_historiques(self, info):
        return Historique.objects.all()
    
    def resolve_historique_by_id(self, info, id):
        return Historique.objects.get(historique_id=id)


# Mutations
class CreateUtilisateurInput(graphene.InputObjectType):
    nom = graphene.String(required=True)
    prenom = graphene.String(required=True)
    email = graphene.String(required=True)
    role = graphene.String()
    mot_de_passe = graphene.String(required=True)


class UpdateUtilisateurInput(graphene.InputObjectType):
    utilisateur_id = graphene.Int(required=True)
    nom = graphene.String()
    prenom = graphene.String()
    email = graphene.String()
    role = graphene.String()


class CreateCompagnieInput(graphene.InputObjectType):
    nom_compagnie = graphene.String(required=True)
    adresse_compagnie = graphene.String()
    email_compagnie = graphene.String()
    api_url = graphene.String()


class UpdateCompagnieInput(graphene.InputObjectType):
    compagnie_id = graphene.Int(required=True)
    nom_compagnie = graphene.String()
    adresse_compagnie = graphene.String()
    email_compagnie = graphene.String()
    api_url = graphene.String()


class CreateInformationInput(graphene.InputObjectType):
    utilisateur_id = graphene.Int(required=True)
    numero_employe = graphene.String()
    adresse = graphene.String()
    numero_assurance = graphene.String()
    cin = graphene.String()
    statut = graphene.Boolean(required=True)
    compagnie_assurance_id = graphene.Int()
    email_notification = graphene.String()


class UpdateInformationInput(graphene.InputObjectType):
    information_id = graphene.Int(required=True)
    numero_employe = graphene.String()
    adresse = graphene.String()
    numero_assurance = graphene.String()
    cin = graphene.String()
    statut = graphene.Boolean()
    compagnie_assurance_id = graphene.Int()
    email_notification = graphene.String()


class CreateUtilisateur(graphene.Mutation):
    class Arguments:
        input = CreateUtilisateurInput(required=True)
    
    utilisateur = graphene.Field(UtilisateurType)
    
    @staticmethod
    def mutate(root, info, input):
        from django.contrib.auth.models import User
        
        user = User.objects.create_user(
            username=input.email,
            email=input.email,
            password=input.mot_de_passe,
            first_name=input.prenom,
            last_name=input.nom
        )
        
        utilisateur = Utilisateur(
            user=user,
            nom=input.nom,
            prenom=input.prenom,
            email=input.email,
            role=input.role,
            mot_de_passe=input.mot_de_passe  # Considérer le hachage du mot de passe
        )
        utilisateur.save()
        
        return CreateUtilisateur(utilisateur=utilisateur)


class UpdateUtilisateur(graphene.Mutation):
    class Arguments:
        input = UpdateUtilisateurInput(required=True)
    
    utilisateur = graphene.Field(UtilisateurType)
    
    @staticmethod
    def mutate(root, info, input):
        utilisateur = Utilisateur.objects.get(utilisateur_id=input.utilisateur_id)
        
        if input.nom:
            utilisateur.nom = input.nom
        if input.prenom:
            utilisateur.prenom = input.prenom
        if input.email:
            utilisateur.email = input.email
        if input.role:
            utilisateur.role = input.role
        
        utilisateur.save()
        return UpdateUtilisateur(utilisateur=utilisateur)


class CreateCompagnie(graphene.Mutation):
    class Arguments:
        input = CreateCompagnieInput(required=True)
    
    compagnie = graphene.Field(CompagnieAssuranceType)
    
    @staticmethod
    def mutate(root, info, input):
        compagnie = Compagnie_Assurance(
            nom_compagnie=input.nom_compagnie,
            adresse_compagnie=input.adresse_compagnie,
            email_compagnie=input.email_compagnie,
            api_url=input.api_url
        )
        compagnie.save()
        return CreateCompagnie(compagnie=compagnie)


class UpdateCompagnie(graphene.Mutation):
    class Arguments:
        input = UpdateCompagnieInput(required=True)
    
    compagnie = graphene.Field(CompagnieAssuranceType)
    
    @staticmethod
    def mutate(root, info, input):
        compagnie = Compagnie_Assurance.objects.get(compagnie_id=input.compagnie_id)
        
        if input.nom_compagnie:
            compagnie.nom_compagnie = input.nom_compagnie
        if input.adresse_compagnie:
            compagnie.adresse_compagnie = input.adresse_compagnie
        if input.email_compagnie:
            compagnie.email_compagnie = input.email_compagnie
        if input.api_url:
            compagnie.api_url = input.api_url
        
        compagnie.save()
        return UpdateCompagnie(compagnie=compagnie)


class CreateInformation(graphene.Mutation):
    class Arguments:
        input = CreateInformationInput(required=True)
    
    information = graphene.Field(InformationType)
    
    @staticmethod
    def mutate(root, info, input):
        utilisateur = Utilisateur.objects.get(utilisateur_id=input.utilisateur_id)
        
        compagnie_assurance = None
        if input.compagnie_assurance_id:
            compagnie_assurance = Compagnie_Assurance.objects.get(compagnie_id=input.compagnie_assurance_id)
        
        information = Information(
            utilisateur=utilisateur,
            numero_employe=input.numero_employe,
            adresse=input.adresse,
            numero_assurance=input.numero_assurance,
            cin=input.cin,
            statut=input.statut,
            compagnie_assurance=compagnie_assurance,
            email_notification=input.email_notification
        )
        information.save()
        return CreateInformation(information=information)


class UpdateInformation(graphene.Mutation):
    class Arguments:
        input = UpdateInformationInput(required=True)
    
    information = graphene.Field(InformationType)
    
    @staticmethod
    def mutate(root, info, input):
        information = Information.objects.get(information_id=input.information_id)
        
        if input.numero_employe:
            information.numero_employe = input.numero_employe
        if input.adresse:
            information.adresse = input.adresse
        if input.numero_assurance:
            information.numero_assurance = input.numero_assurance
        if input.cin:
            information.cin = input.cin
        if input.statut is not None:
            information.statut = input.statut
        if input.compagnie_assurance_id:
            information.compagnie_assurance = Compagnie_Assurance.objects.get(compagnie_id=input.compagnie_assurance_id)
        if input.email_notification:
            information.email_notification = input.email_notification
        
        information.save()
        return UpdateInformation(information=information)


class ReceiveNotificationFeedback(graphene.Mutation):
    class Arguments:
        notification_id = graphene.Int(required=True)
        status = graphene.Boolean(required=True)
        message = graphene.String()
        source = graphene.String(required=True)  # "employe" ou "assurance"
    
    success = graphene.Boolean()
    message = graphene.String()
    
    @staticmethod
    def mutate(root, info, notification_id, status, message, source):
        try:
            notification = Notification.objects.get(notification_id=notification_id)
            
            historique = Historique.objects.create(
                type_action=f"feedback_{source}",
                description=f"Feedback reçu de {source}: {'Succès' if status else 'Échec'}{' - ' + message if message else ''}"
            )
            
            notification.enregistrer_dans_historique(
                type_action=f"feedback_{source}",
                description=f"Feedback reçu de {source}: {'Succès' if status else 'Échec'}{' - ' + message if message else ''}"
            )
            
            return ReceiveNotificationFeedback(success=True, message="Feedback enregistré avec succès")
        except Notification.DoesNotExist:
            return ReceiveNotificationFeedback(success=False, message="Notification introuvable")
        except Exception as e:
            return ReceiveNotificationFeedback(success=False, message=f"Erreur: {str(e)}")


class Mutation(graphene.ObjectType):
    create_utilisateur = CreateUtilisateur.Field()
    update_utilisateur = UpdateUtilisateur.Field()
    create_compagnie = CreateCompagnie.Field()
    update_compagnie = UpdateCompagnie.Field()
    create_information = CreateInformation.Field()
    update_information = UpdateInformation.Field()
    receive_notification_feedback = ReceiveNotificationFeedback.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)