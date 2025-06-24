from django.shortcuts import redirect
from django.urls import path
from . import views
from .views import Tarif_view
app_name = 'gestion'

urlpatterns = [
    path('', lambda request: redirect('login/', permanent=False)),
    path('tarif/', Tarif_view, name='tarif'),
    path('dashboard_superviseur/', views.dashboard_superviseur, name='dashboard_superviseur'),
    path('dashboard_administrateur/', views.dashboard_administrateur, name='dashboard_administrateur'),
    path('dashboard_agent/', views.dashboard_agent, name='dashboard_agent'),
    path('unauthorized/', views.unauthorized, name='unauthorized'),

    path('dashboard_etudiant/', views.dashboard_etudiant, name='dashboard_etudiant'),
    path('consulter_absences_etudiant/', views.consulter_absences_etudiant, name='consulter_absences_etudiant'),
    path('consulter_notes_etudiant/', views.consulter_notes_etudiant, name='consulter_notes_etudiant'),
    path('emploi_temps_etudiant/', views.emploi_temps_etudiant, name='emploi_temps_etudiant'),
    path('etat_paiement_etudiant/', views.etat_paiement_etudiant, name='etat_paiement_etudiant'),


    path('dashboard_enseignant/', views.dashboard_enseignant, name='dashboard_enseignant'),
    path('noter_absence/', views.noter_absence, name='noter_absence'),
    path('saisir_notes_CC/', views.saisir_notes_CC, name='saisir_notes_CC'),
    path('depot_cours/', views.depot_cours, name='depot_cours'),
    path('emploi_temps/', views.emploi_temps, name='emploi_temps'),

    path('login/', views.login_view, name= 'login'),
    path('accueil/', views.accueil, name='accueil'),
    path('affectationEtudiants/', views.affectation, name='affectationEtudiants'),

    path('classes/', views.classes, name='classes'),
    path('liste_classes/', views.liste_classes, name='liste_classes'),
    path('classes/modifier/<int:classe_id>/', views.modifier_classe, name='modifier_classe'),

    path('Diplome/', views.Diplome_view, name='Diplome'),
    path('liste_diplomes/', views.liste_diplomes, name='liste_diplomes'),

    path('InscriEnseignants/', views.InscriEnseignants, name='InscriEnseignants'),
    path('ListeEnseignants/', views.ListeEnseignants, name='ListeEnseignants'),
    path('enseignant/<int:id>/', views.detail_enseignant, name='detail_enseignant'),

    path('InscriEtudiants/', views.InscriEtudiants, name='InscriEtudiants'),
    path('ListeEtudiants/', views.ListeEtudiants, name='ListeEtudiants'),
    path('etudiant/<int:id>/', views.detail_etudiant, name='detail_etudiant'),

    path('matieres/', views.matieres, name='matieres'),
    path('liste_matieres/', views.liste_matieres, name='liste_matieres'),

    path('liste_specialites/', views.liste_specialites, name='liste_specialites'),
    path('specialite/supprimer/<int:specialite_id>/', views.supprimer_specialite, name='supprimer_specialite'),
    path('specialite/modifier/<int:specialite_id>/', views.modifier_specialite, name='modifier_specialite'),
    path('specialite/', views.specialite, name='specialite'),

    path('plan_etudes/', views.plan_etudes, name='plan_etudes'),
    path('liste_plan_etudes/', views.liste_plan_etudes, name='liste_plan_etudes'),
    path('modifier_plan_etude/<int:id>/', views.modifier_plan_etude, name='modifier_plan_etude'),
    path('supprimer_plan_etude/<int:id>/', views.supprimer_plan_etude, name='supprimer_plan_etude'),

    path('emploi_du_temps/', views.emploi_du_temps, name='emploi_du_temps'),
    

    path('absences/', views.absences, name='absences'),
    path('elimination/', views.elimination, name='elimination'),

    path('saisie_des_notes/', views.saisie_des_notes, name='saisie_des_notes'),
    path('liste_saisie_des_notes/', views.liste_saisie_des_notes, name='liste_saisie_des_notes'),

    path('voir_pv/<int:classe_id>/<int:session_id>/', views.voir_pv, name='voir_pv'),
    path('calcul_PV/', views.calcul_PV, name='calcul_PV'),

    path('ajax/classes/', views.get_classes, name='ajax_get_classes'),
    path('ajax/etudiants/<int:classe_id>/', views.get_etudiants_par_classe, name='ajax_get_etudiants'),
    path("get_classe_details/<int:classe_id>/", views.get_classe_details, name="get_classe_details"),
   

]







