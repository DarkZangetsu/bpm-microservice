from django.core.management.base import BaseCommand
from assurance_app.models import CompagnieAssurance

class Command(BaseCommand):
    help = 'Créer une compagnie d\'assurance par défaut si aucune n\'existe'

    def handle(self, *args, **options):
        if not CompagnieAssurance.objects.exists():
            company = CompagnieAssurance.objects.create(
                nom_compagnie="Assurance Générale",
                adresse_compagnie="123 Rue de l'Assurance",
                email_compagnie="contact@assurance-generale.com",
                rh_compagnie_id=1 
            )
            self.stdout.write(self.style.SUCCESS(f'Compagnie d\'assurance par défaut créée: {company.nom_compagnie}'))
        else:
            self.stdout.write(self.style.WARNING('Une compagnie d\'assurance existe déjà.'))