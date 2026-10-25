from django.urls import path
from . import views 
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('agences/', views.agences, name='agences'),
    path('carte_reseau/', views.carte_reseau, name='carte_reseau'),
    path('performances/', views.performances, name='performances'),
    path('kpi/', views.kpi, name='kpi'),
    path('alertes/', views.alertes, name='alertes'),
    path('historique/', views.historique, name='historique'),
    path('rapports/', views.rapports, name='rapports'),
    path('profil/', views.profil, name='profil'),
    path('alertes/<int:alerte_id>/resoudre/', views.resoudre_alerte, name='resoudre_alerte'),
    path('rapports/pdf/', views.generer_rapport_pdf, name='generer_rapport_pdf'),
]
