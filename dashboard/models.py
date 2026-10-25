from django.db import models

# Create your models here.
class Agence(models.Model):
    nom = models.CharField(max_length=100)
    ville = models.CharField(max_length=100)
    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)
    latence = models.FloatField(default=0.0)
    perte_paquets = models.FloatField(default=0.0)
    bande_passante = models.FloatField(default=0.0)
    statut = models.CharField(max_length=20, choices=[('en ligne', 'En ligne'), ('hors ligne', 'Hors ligne'), ('anomalie', 'Anomalie')], default='en ligne')
    def __str__(self):
        return self.nom

class Alerte(models.Model):
    agence = models.ForeignKey(Agence, on_delete=models.CASCADE)
    type_alerte = models.CharField(max_length=100)
    severite = models.CharField(max_length=30)
    statut = models.CharField(max_length=20, choices=[('ouverte', 'Ouverte'), ('en cours', 'En cours'), ('fermée', 'Fermée')], default='ouverte')
    date_creation = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.type_alerte} - {self.agence.nom}"