from django.db import models
from django.utils import timezone

class CompagnieAssurance(models.Model):
    compagnie_id = models.AutoField(primary_key=True)
    nom_compagnie = models.CharField(max_length=255)
    adresse_compagnie = models.CharField(max_length=255, null=True, blank=True)
    email_compagnie = models.CharField(max_length=255, null=True, blank=True)
    api_url = models.CharField(max_length=255, null=True, blank=True)
    
    # Identifiant externe du serveur RH
    rh_compagnie_id = models.IntegerField(unique=True, null=True, blank=True)
    
    def __str__(self):
        return self.nom_compagnie

class Assure(models.Model):
    assure_id = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    email = models.CharField(max_length=255, null=True, blank=True)
    
    # Identifiant externe du serveur RH
    rh_utilisateur_id = models.IntegerField(unique=True, null=True, blank=True)
    
    def __str__(self):
        return f"{self.prenom} {self.nom}"

class InformationAssure(models.Model):
    information_id = models.AutoField(primary_key=True)
    assure = models.ForeignKey(Assure, on_delete=models.CASCADE, related_name='informations')
    compagnie = models.ForeignKey(CompagnieAssurance, on_delete=models.CASCADE, related_name='assures')
    numero_employe = models.CharField(max_length=255, null=True, blank=True)
    adresse = models.CharField(max_length=255, null=True, blank=True)
    numero_assurance = models.CharField(max_length=255, null=True, blank=True)
    cin = models.CharField(max_length=255, null=True, blank=True)
    statut = models.BooleanField(default=False)
    
    # Identifiant externe du serveur RH
    rh_information_id = models.IntegerField(unique=True, null=True, blank=True)
    derniere_mise_a_jour = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Info de {self.assure}"

class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    information = models.ForeignKey(InformationAssure, on_delete=models.CASCADE, related_name='notifications')
    objet = models.CharField(max_length=255, null=True, blank=True)
    contenu = models.TextField(null=True, blank=True)
    expediteur = models.CharField(max_length=255, null=True, blank=True)
    destinataire = models.CharField(max_length=255, null=True, blank=True)
    date_envoi = models.DateTimeField(null=True, blank=True)
    date_reception = models.DateTimeField(auto_now_add=True)
    statut = models.BooleanField(default=False)
    
    # Identifiant externe du serveur RH
    rh_notification_id = models.IntegerField(unique=True, null=True, blank=True)
    
    def __str__(self):
        return f"{self.objet} ({self.date_reception})"

class Historique(models.Model):
    historique_id = models.AutoField(primary_key=True)
    date = models.DateTimeField(auto_now_add=True)
    type_action = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    notification = models.ForeignKey(Notification, on_delete=models.SET_NULL, null=True, blank=True, related_name='historiques')
    
    def __str__(self):
        return f"Historique {self.pk} ({self.date})"