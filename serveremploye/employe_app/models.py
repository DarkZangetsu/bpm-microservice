from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Utilisateur(models.Model):
    utilisateur_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', null=True, blank=True)
    nom = models.CharField(max_length=255, null=True, blank=True)
    prenom = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    role = models.CharField(max_length=255, null=True, blank=True)
    
    # Identifiant externe du serveur RH
    rh_utilisateur_id = models.IntegerField(unique=True, null=True, blank=True)
    
    def __str__(self):
        return f"{self.prenom} {self.nom}"


class Information(models.Model):
    information_id = models.AutoField(primary_key=True)
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='informations')
    numero_employe = models.CharField(max_length=255, null=True, blank=True)
    adresse = models.CharField(max_length=255, null=True, blank=True)
    numero_assurance = models.CharField(max_length=255, null=True, blank=True)
    cin = models.CharField(max_length=255, null=True, blank=True)
    statut = models.BooleanField(default=False)
    
    # Identifiant externe du serveur RH
    rh_information_id = models.IntegerField(unique=True, null=True, blank=True)
    derniere_mise_a_jour = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Info de {self.utilisateur}"


class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    information = models.ForeignKey(Information, on_delete=models.CASCADE, related_name='notifications')
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