import qrcode
import io
import base64
from .forms import DepotCoursForm, SpecialiteForm
from django.db import IntegrityError
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect,get_object_or_404
from .decorators import role_required
from django.views.decorators.csrf import csrf_exempt  # optionnel pour tests
from .models import *
from django.utils import timezone
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.auth.models import Group
from django.shortcuts import render
from django.db.models import Count
import json
from django.utils.safestring import mark_safe
from django.http import JsonResponse
from datetime import datetime
from django.contrib.auth.decorators import login_required
from .forms import AbsenceForm



def get_classes(request):
    classes = Classe.objects.all().values('id', 'nom')
    return JsonResponse(list(classes), safe=False)

def get_etudiants_par_classe(request, classe_id):
    etudiants = Etudiant.objects.filter(classe_id=classe_id).values('id', 'nom', 'prenom')
    return JsonResponse(list(etudiants), safe=False)


def accueil(request):
    return render(request, "gestion/production/accueil.html")
@csrf_exempt

@role_required(['Superviseur'])
def dashboard_superviseur(request):
    # Spécialités
    qs_specialite = Etudiant.objects.values('specialite__libelle').annotate(count=Count('id')).order_by('specialite__libelle')
    labels_specialite = [item['specialite__libelle'] if item['specialite__libelle'] else 'Non défini' for item in qs_specialite]
    data_specialite = [item['count'] for item in qs_specialite]

    # Niveaux
    qs_niveau = Etudiant.objects.values('niveau__libelle').annotate(count=Count('id')).order_by('niveau__libelle')
    labels_niveau = [item['niveau__libelle'] if item['niveau__libelle'] else 'Non défini' for item in qs_niveau]
    data_niveau = [item['count'] for item in qs_niveau]

    # Total étudiants
    total_etudiants = Etudiant.objects.count()
     # Total enseignants
    total_enseignants = Enseignant.objects.count()
     # Total specialites
    total_specialites = Filiere.objects.count()

    context = {
        'labels_specialite': json.dumps(labels_specialite),
        'data_specialite': json.dumps(data_specialite),
        'labels_niveau': json.dumps(labels_niveau),
        'data_niveau': json.dumps(data_niveau),
        'total_etudiants': total_etudiants,
        'total_enseignants': total_enseignants,
        'total_specialites': total_specialites,

    }
    return render(request, 'gestion/production/dashboard_superviseur.html',context)

@role_required(['Etudiant'])
def dashboard_etudiant(request):
    user = request.user
    try:
        etudiant = Etudiant.objects.get(user=user)
    except Etudiant.DoesNotExist:
        etudiant = None

    absences = Absence.objects.filter(etudiant=etudiant).select_related('matiere') if etudiant else []
    etat_paiement = EtatPaiement.objects.filter(etudiant=etudiant).first() if etudiant else None
    emploi_temps = Planning.objects.filter(classe=etudiant.classe).order_by('jour', 'heuredeb')
    notes = Note.objects.filter(etudiant=etudiant).select_related('matiere') if etudiant else []

    context = {
        'etudiant': etudiant,
        'absences': absences,
        'etat_paiement': etat_paiement,
        'emploi_temps': emploi_temps,
        'notes': notes,
    }
    return render(request, 'gestion/production/dashboard_etudiant.html', context)

def consulter_absences_etudiant(request):
    etudiant = request.user.etudiant
    absences = Absence.objects.filter(etudiant=etudiant).select_related('matiere', 'planning')
    return render(request, 'gestion/production/consulter_absences_etudiant.html', {'absences': absences})

def consulter_notes_etudiant(request):
    etudiant = request.user.etudiant
    notes = Note.objects.filter(etudiant=etudiant).select_related('matiere')
    return render(request, 'gestion/production/consulter_notes_etudiant.html', {'notes': notes})

def emploi_temps_etudiant(request):
    etudiant = request.user.etudiant
    emploi_temps = Planning.objects.filter(classe=etudiant.classe).order_by('jour', 'heuredeb')
    return render(request, 'gestion/production/emploi_temps_etudiant.html', {'emploi_temps': emploi_temps})

def etat_paiement_etudiant(request):
    etudiant = request.user.etudiant
    etat_paiement = EtatPaiement.objects.filter(etudiant=etudiant).first()
    return render(request, 'gestion/production/etat_paiement_etudiant.html', {'etat_paiement': etat_paiement})

def role_required(roles):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.groups.filter(name__in=roles).exists():
                return view_func(request, *args, **kwargs)
            from django.http import HttpResponseForbidden
            return HttpResponseForbidden("Accès non autorisé")
        return _wrapped_view
    return decorator

@login_required
@role_required(['Enseignant'])
def dashboard_enseignant(request):
    enseignant = request.user.enseignant
    absences = Absence.objects.filter(matiere__enseignant=enseignant)
    emplois = Planning.objects.filter(matiere__enseignant=enseignant)
    cours = Cours.objects.filter(matiere__enseignant=enseignant)
    return render(request, 'gestion/production/dashboard_enseignant.html', {
        'enseignant': enseignant,
        'absences': absences,
        'emplois': emplois,
        'cours': cours
    })


@login_required
@role_required(['Enseignant'])
def noter_absence(request):
    enseignant = request.user.enseignant  # Assure-toi que le lien OneToOne est bien défini

    if request.method == 'POST':
        form = AbsenceForm(request.POST, enseignant=enseignant)
        if form.is_valid():
            form.save()
            messages.success(request, "Absence enregistrée avec succès.")
            return redirect('/noter_absence')
    else:
        form = AbsenceForm(enseignant=enseignant)

    return render(request, 'gestion/production/noter_absence.html', {'form': form})


@login_required
@role_required(['Enseignant'])
def depot_cours(request):
    enseignant = request.user.enseignant
    if request.method == 'POST':
        form = DepotCoursForm(request.POST, request.FILES, enseignant=enseignant)
        if form.is_valid():
            form.save()
            return redirect('/dashboard_enseignant')
    else:
        form = DepotCoursForm(enseignant=enseignant)
    return render(request, 'gestion/production/depot_cours.html', {'form': form})


@login_required
@role_required(['Enseignant'])
def consulter_emploi_temps(request):
    enseignant = request.user.enseignant
    emplois = Planning.objects.filter(matiere__enseignant=enseignant).order_by('jour', 'heure_debut')
    return render(request, 'gestion/production/emploi_temps.html', {'emplois': emplois})


@role_required(['Enseignant'])
def dashboard_enseignant(request):
    enseignant = request.user.enseignant  # relation OneToOne avec User
    context = {
        'enseignant': enseignant,
        'absences': Absence.objects.filter(matiere__enseignant=enseignant),
        'emplois': Planning.objects.filter(matiere__enseignant=enseignant),
        'cours': Cours.objects.filter(matiere__enseignant=enseignant)
    }
    return render(request, 'gestion/production/dashboard_enseignant.html', context)


def saisir_notes_CC(request):
    enseignant = request.user.enseignant
    matieres = Matiere.objects.filter(enseignant=enseignant)
    etudiants = Etudiant.objects.all()  # Ici, adapte la sélection selon ta logique

    if request.method == "POST":
        matiere_id = request.POST.get('matiere')
        if not matiere_id:
            # gérer erreur (matiere non sélectionnée)
            # par exemple, message erreur, ou rechargement page
            pass

        for etudiant in etudiants:
            note_valeur = request.POST.get(f"note_cc_{etudiant.id}")
            observation = request.POST.get(f"observation_{etudiant.id}", "")
            if note_valeur:  # si une note a été saisie
                Note.objects.create(
                    etudiant=etudiant,
                    matiere_id=matiere_id,
                    note_cc=note_valeur,
                    observation=observation,
                    date_saisie=timezone.now()
                )
        return redirect('dashboard_enseignant')

    context = {
        'matieres': matieres,
        'etudiants': etudiants
    }
    return render(request, 'gestion/production/saisir_notes_CC.html', context)


def emploi_temps(request):
    enseignant = request.user.enseignant
    emploi = Planning.objects.filter(matiere__enseignant=enseignant)
    return render(request, 'gestion/production/emploi_temps.html', {'emplois': emploi})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Vérification si l'utilisateur est un étudiant
            try:
                if hasattr(user, 'etudiant'):
                    return redirect('gestion:dashboard_etudiant')
            except:
                pass
            
            # Vérification si l'utilisateur est un enseignant
            try:
                if hasattr(user, 'enseignant'):
                    return redirect('gestion:dashboard_enseignant')
            except:
                pass

            # Vérification des autres groupes
            if user.groups.filter(name='Superviseur').exists():
                return redirect('gestion:dashboard_superviseur')
            elif user.groups.filter(name='Administrateur').exists():
                return redirect('gestion:dashboard_administrateur')
            elif user.groups.filter(name='Agent').exists():
                return redirect('gestion:dashboard_agent')

            messages.error(request, "Aucun rôle défini.")
            return redirect('gestion:unauthorized')
        
        else:
            messages.error(request, "Identifiants incorrects.")
            return redirect('gestion:login')

    return render(request, 'gestion/production/login.html')

def accueil_admin(request):
       
    return render(request, 'gestion/production/dashboard_superviseur.html')


def affectation(request):
    classes = Classe.objects.all()
    diplomes = Diplome.objects.all()
    specialites = Specialite.objects.all()
    niveaux = Niveau.objects.all()
    semestres = Semestre.objects.all()
    affectations = Affectation.objects.select_related('classe', 'diplome', 'specialite', 'niveau', 'semestre').all()

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "ajouter":
            Affectation.objects.create(
                classe_id=request.POST.get('classe'),
                diplome_id=request.POST.get('diplome'),
                specialite_id=request.POST.get('specialite'),
                niveau_id=request.POST.get('niveau'),
                semestre_id=request.POST.get('semestre'),
                nombre_etudiants=request.POST.get('nombre_etudiants') or 0
            )
            messages.success(request, "Affectation ajoutée avec succès.")
            return redirect("gestion:affectation")

        elif action == "modifier":
            aff_id = request.POST.get("affectation_id")
            aff = get_object_or_404(Affectation, pk=aff_id)
            aff.classe_id = request.POST.get('classe')
            aff.diplome_id = request.POST.get('diplome')
            aff.specialite_id = request.POST.get('specialite')
            aff.niveau_id = request.POST.get('niveau')
            aff.semestre_id = request.POST.get('semestre')
            aff.nombre_etudiants = request.POST.get('nombre_etudiants') or 0
            aff.save()
            messages.success(request, "Affectation modifiée avec succès.")
            return redirect("gestion:affectation")

        elif action == "supprimer":
            aff_id = request.POST.get("affectation_id")
            Affectation.objects.filter(pk=aff_id).delete()
            messages.warning(request, "Affectation supprimée.")
            return redirect("gestion:affectation")

    return render(request, "gestion/production/affectationEtudiants.html", {
        "classes": classes,
        "diplomes": diplomes,
        "specialites": specialites,
        "niveaux": niveaux,
        "semestres": semestres,
        "affectations": affectations,
    })

def classes(request):
    if request.method == "POST":
        libelle = request.POST.get('libelle')
        specialite_id = request.POST.get('specialite')
        semestre_id = request.POST.get('semestre')
        niveau_id = request.POST.get('niveau')

        # Validation simple
        if not libelle or not specialite_id or not semestre_id or not niveau_id:
            messages.error(request, "Veuillez remplir tous les champs obligatoires.")
        else:
            try:
                specialite = Specialite.objects.get(pk=specialite_id)
                semestre = Semestre.objects.get(pk=semestre_id)
                niveau = Niveau.objects.get(pk=niveau_id)

                Classe.objects.create(
                    libelle=libelle,
                    specialite=specialite,
                    semestre=semestre,
                    niveau=niveau
                )
                messages.success(request, "Classe enregistrée avec succès.")
                return redirect('gestion:liste_classes')  # À adapter selon ta route de liste
            except Specialite.DoesNotExist:
                messages.error(request, "Spécialité invalide.")
            except Semestre.DoesNotExist:
                messages.error(request, "Semestre invalide.")
            except Niveau.DoesNotExist:
                messages.error(request, "Niveau invalide.")

    # En GET ou en cas d'erreur, recharger les listes
    specialites = Specialite.objects.all()
    semestres = Semestre.objects.all()
    niveaux = Niveau.objects.all()

    return render(request, 'gestion/production/classes.html', {
        'specialites': specialites,
        'semestres': semestres,
        'niveaux': niveaux,
    })

def liste_classes(request):
    classes = Classe.objects.select_related('specialite', 'semestre', 'niveau').all()
    return render(request, 'gestion/production/liste_classes.html', {
        'classes': classes
    })


def modifier_classe(request, classe_id):
    classe = get_object_or_404(Classe, pk=classe_id)

    if request.method == "POST":
        libelle = request.POST.get('libelle')
        specialite_id = request.POST.get('specialite')
        semestre_id = request.POST.get('semestre')
        niveau_id = request.POST.get('niveau')

        if not libelle or not specialite_id or not semestre_id or not niveau_id:
            messages.error(request, "Veuillez remplir tous les champs obligatoires.")
        else:
            try:
                specialite = Specialite.objects.get(pk=specialite_id)
                semestre = Semestre.objects.get(pk=semestre_id)
                niveau = Niveau.objects.get(pk=niveau_id)

                classe.libelle = libelle
                classe.specialite = specialite
                classe.semestre = semestre
                classe.niveau = niveau
                classe.save()

                messages.success(request, "Classe modifiée avec succès.")
                return redirect('gestion:liste_classes')
            except Specialite.DoesNotExist:
                messages.error(request, "Spécialité invalide.")
            except Semestre.DoesNotExist:
                messages.error(request, "Semestre invalide.")
            except Niveau.DoesNotExist:
                messages.error(request, "Niveau invalide.")

    specialites = Specialite.objects.all()
    semestres = Semestre.objects.all()
    niveaux = Niveau.objects.all()

    return render(request, 'gestion/production/modifier_classe.html', {
        'classe': classe,
        'specialites': specialites,
        'semestres': semestres,
        'niveaux': niveaux,
    })

def Diplome_view(request):
    if request.method == "POST":
        libelle = request.POST.get('libelle')
        duree = request.POST.get('duree')
        credit = request.POST.get('credit')

        if not libelle:
            messages.error(request, "Le champ Désignation est obligatoire.")
        else:
            try:
                credit_val = int(credit) if credit else None
            except ValueError:
                messages.error(request, "Le crédit doit être un nombre.")
                return render(request, "gestion/production/Diplome.html")

            diplome = Diplome.objects.create(
                libelle=libelle,
                duree=duree,
                credit=credit_val
            )
            messages.success(request, "Diplôme enregistré avec succès.")
            return redirect('gestion:liste_diplomes')  # remplace par ta route

    return render(request, "gestion/production/Diplome.html")

def liste_diplomes(request):
    diplomes = Diplome.objects.all()
    return render(request, 'gestion/production/liste_diplomes.html', {'diplomes': diplomes})

def InscriEnseignants(request):
    if request.method == "POST":
        nom = request.POST.get("nom")
        prenom = request.POST.get("prenom")
        numTel = request.POST.get("numTel")
        grade = request.POST.get("grade")
        cin = request.POST.get("cin")
        email = request.POST.get("email")

        try:
            Enseignant.objects.create(
                nom=nom,
                prenom=prenom,
                numTel=numTel,
                grade=grade,
                CIN=cin,
                email=email,
            )
            return redirect('/ListeEnseignants')
        except IntegrityError:
            messages.error(request, "Erreur : un enseignant avec ce CIN existe déjà.")

    return render(request, "gestion/production/InscriEnseignants.html")

def ListeEnseignants(request):
    enseignants = Enseignant.objects.all()
    enseignants_qr = []

    for ens in enseignants:
        qr_data = f"http://192.168.100.228:8000/enseignant/{ens.id}/"  # ou toute autre info
        qr_img = qrcode.make(qr_data)

        buffer = io.BytesIO()
        qr_img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()

        enseignants_qr.append({
            'enseignant': ens,
            'qr_code': img_str,
        })

    return render(request, 'gestion/production/ListeEnseignants.html', {'enseignants_qr': enseignants_qr})

def detail_enseignant(request, id):
    enseignant = get_object_or_404(Enseignant, pk=id)
    return render(request, 'gestion/production/detail_enseignant.html', {'enseignant': enseignant})

def InscriEtudiants(request):
    if request.method == "POST":
        # Récupération des données du formulaire
        code_etudiant = request.POST.get('code_etudiant')
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        sexe_id = request.POST.get('sexe')
        datenaiss = request.POST.get('date_naissance')
        lieuNaiss = request.POST.get('lieu_naissance')
        nationalite_id = request.POST.get('nationalite')
        situation_id = request.POST.get('situation_familiale')
        cin = request.POST.get('cin')
        datePasseport = request.POST.get('date_delivrance')
        adresse = request.POST.get('adresse')
        CP = request.POST.get('code_postal')
        email = request.POST.get('email')
        numTel = request.POST.get('telephone')
        ville = request.POST.get('ville')
        pays = request.POST.get('pays_bac') or "Maroc"
        boursier = request.POST.get('boursier') == 'non'
        emailUMT = request.POST.get('email_umt')
        diplome_id = request.POST.get('diplome')
        numBac = request.POST.get('numero_bac')
        etablissementBac = request.POST.get('etablissement_bac')
        anneeBac = request.POST.get('annee_bac')
        nature_bac_id = request.POST.get('nature_bac')
        mention_id = request.POST.get('mention_bac')
        paysBac = request.POST.get('pays_bac')

        # Tuteur
        nom_tuteur = request.POST.get('nom_tuteur')
        prenom_tuteur = request.POST.get('prenom_tuteur')
        tel_tuteur = request.POST.get('tel_tuteur')
        email_tuteur = request.POST.get('email_tuteur')

        # Création du tuteur
        tuteur = Tuteur.objects.create(
            nom=nom_tuteur,
            prenom=prenom_tuteur,
            numTel=tel_tuteur,
            email=email_tuteur
        )

        # Parcours
        diplome_id = request.POST.get('diplome')
        specialite_id = request.POST.get('specialite')
        filiere_id = request.POST.get('filiere')
        niveau_id = request.POST.get('niveau')
        session_id = request.POST.get('session')
        classe_id = request.POST.get('classe')
        
        # Création de l'étudiant
        Etudiant.objects.create(
            code_etudiant=code_etudiant,
            nom=nom,
            prenom=prenom,
            sexe=Sexe.objects.get(pk=sexe_id),
            datenaiss=datenaiss,
            lieuNaiss=lieuNaiss,
            nationalite=Nationalite.objects.get(pk=nationalite_id),
            situationfamiliale=SituationFamiliale.objects.get(pk=situation_id),
            CIN_Passeport=cin,
            datePasseport=datePasseport,
            lieuPassport=lieuNaiss,
            adresse=adresse,
            CP=CP,
            email=email,
            numTel=numTel,
            pays=pays,
            ville=ville,
            boursier=boursier,
            dateInscription=timezone.now().date(),
            numBac=numBac,
            anneeBac=anneeBac,
            nature_bac=NatureBac.objects.get(pk=nature_bac_id),
            mentionBac=Mention.objects.get(pk=mention_id),
            etablissementBac=etablissementBac,
            paysBac=paysBac,
            emailUMT=emailUMT,
            diplome=Diplome.objects.get(pk=diplome_id),
            specialite=Specialite.objects.get(pk=specialite_id),
            niveau=Niveau.objects.get(pk=niveau_id),
            classe=Classe.objects.get(pk=classe_id),
            session=Session.objects.get(pk=session_id),
            affectationTarif=0.0,
            devise='TND',
            etat='actif',
            tuteur=tuteur
        )

        return redirect('/ListeEtudiants')  # Redirection après enregistrement

    # Si GET : charger les listes pour le formulaire
    sexes = Sexe.objects.all()
    nationalites = Nationalite.objects.all()
    situations = SituationFamiliale.objects.all()
    natures_bac = NatureBac.objects.all()
    mentions = Mention.objects.all()
    specialites = Specialite.objects.all()
    niveaux = Niveau.objects.all()
    sessions = Session.objects.all()
    diplomes = Diplome.objects.all()
    classes = Classe.objects.all()
    return render(request, "gestion/production/InscriEtudiants.html", {
        "sexes": sexes,
        "nationalites": nationalites,
        "situations": situations,
        "natures_bac": natures_bac,
        "mentions": mentions,
        "specialites": specialites,
        "niveaux": niveaux,
        "sessions": sessions,
        "diplomes": diplomes,
        "classes": classes,
    })

def detail_etudiant(request, id):
    etudiant = Etudiant.objects.get(id=id)
    return render(request, 'gestion/production/detail_etudiant.html', {'etudiant': etudiant})

def ListeEtudiants(request):
    etudiants = Etudiant.objects.all()
    etudiants_qr = []

    for etu in etudiants:
        qr_data = f"http://192.168.100.228:8000/etudiant/{etu.id}/"

        # Génération QR Code
        qr_img = qrcode.make(qr_data)

        # Sauvegarder en mémoire tampon
        buffer = io.BytesIO()
        qr_img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()  # Encodage en base64

        etudiants_qr.append({
            'etudiant': etu,
            'qr_code': img_str,
        })

    return render(request, 'gestion/production/ListeEtudiants.html', {'etudiants_qr': etudiants_qr})

def matieres(request):
    if request.method == "POST":
        libelle = request.POST.get('libelle')

        if not libelle:
            messages.error(request, "Le champ Désignation est obligatoire.")
            return render(request, "gestion/production/matieres.html")  # retour avec le message d'erreur
        else:
            Matiere.objects.create(libelle=libelle)
            messages.success(request, "Matière enregistrée avec succès.")
            return redirect('/liste_matieres')  # redirection vers la liste

    # 👉 Ajout du return manquant pour GET
    return render(request, "gestion/production/matieres.html")

def liste_matieres(request):
    matieres = Matiere.objects.all().order_by('libelle')
    return render(request, "gestion/production/liste_matieres.html", {
        "matieres": matieres
    })

def specialite(request):
    if request.method == "POST":
        libelle = request.POST.get('libelle')
        domaine = request.POST.get('domaine')
        mention = request.POST.get('mention')
        principaux = request.POST.get('principaux')
        exigences = request.POST.get('exigences')
        filiere_id = request.POST.get('filiere')
        diplome_id = request.POST.get('diplome')

        if not all([libelle, domaine, mention, principaux, exigences, filiere_id, diplome_id]):
            messages.error(request, "Tous les champs sont obligatoires.")
        else:
            filiere = Filiere.objects.get(pk=filiere_id)
            diplome = Diplome.objects.get(pk=diplome_id)

            Specialite.objects.create(
                libelle=libelle,
                DomaineFormation=domaine,
                Mention=mention,
                PrincipauxDomaine=principaux,
                ExigencesDuProgramme=exigences,
                filiere=filiere,
                diplome=diplome
            )
            messages.success(request, "Spécialité enregistrée avec succès.")
            return redirect('/liste_specialites')

    filieres = Filiere.objects.all()
    diplomes = Diplome.objects.all()
    return render(request, "gestion/production/specialite.html", {
        "filieres": filieres,
        "diplomes": diplomes
    })

def liste_specialites(request):
    specialites = Specialite.objects.select_related('filiere', 'diplome').all()
    return render(request, 'gestion/production/liste_specialites.html', {
        'specialites': specialites
    })

def supprimer_specialite(request, specialite_id):
    specialite = get_object_or_404(Specialite, pk=specialite_id)
    specialite.delete()
    messages.success(request, "Spécialité supprimée avec succès.")
    return redirect('gestion:liste_specialites')

def modifier_specialite(request, specialite_id):
    specialite = get_object_or_404(Specialite, pk=specialite_id)
    
    if request.method == 'POST':
        form = SpecialiteForm(request.POST, instance=specialite)
        if form.is_valid():
            form.save()
            messages.success(request, "Spécialité modifiée avec succès.")
            return redirect('gestion:liste_specialites')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = SpecialiteForm(instance=specialite)

    return render(request, 'gestion/production/modifier_specialite.html', {
        'form': form,
        'specialite': specialite
    })


def calcul_PV(request):
    classes = Classe.objects.all()
    classe = None
    etudiants = []
    classe_id = None
    moyenne_calculee = False
    message = None
    session = Session.objects.last()  # adapte selon ta logique

    if request.method == "POST":
        classe_id = request.POST.get('classe_id')
        action = request.POST.get('action')

        if classe_id:
            try:
                classe = Classe.objects.get(pk=int(classe_id))
            except Classe.DoesNotExist:
                classe = None
                message = "Classe non trouvée."
        else:
            message = "Veuillez sélectionner une classe."

        if action == "afficher_etudiants" and classe:
            etudiants = Etudiant.objects.filter(classe=classe)

        elif action == "calculer" and classe:
            etudiants = Etudiant.objects.filter(classe=classe)
            # ... Ton code calcul PV ici ...
            moyenne_calculee = True
            message = "Calcul effectué."

        # Tu peux aussi gérer 'enregistrer' etc.

    context = {
        "classes": classes,
        "classe": classe,
        "classe_id": int(classe_id) if classe_id else None,
        "etudiants": etudiants,
        "moyenne_calculee": moyenne_calculee,
        "message": message,
        "session": session,
    }

    return render(request, "gestion/production/calcul_PV.html", context)


def voir_pv(request, classe_id, session_id):
    classe = Classe.objects.get(pk=classe_id)
    session = Session.objects.get(pk=session_id)
    resultat_pv = PVNote.objects.filter(classe=classe, session=session)

    # Génération du lien vers cette page
    url = request.build_absolute_uri()

    # Génération du QR Code
    qr_img = qrcode.make(url)
    buffer = io.BytesIO()
    qr_img.save(buffer, format="PNG")
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, 'gestion/production/voir_pv.html', {
        'classe': classe,
        'session': session,
        'resultat_pv': resultat_pv,
        'qr_code': qr_code_base64,  # ajout du QR code
    })

def get_classe_details(request, classe_id):
    try:
        classe = Classe.objects.get(pk=classe_id)
        niveau = classe.niveau  # suppose que tu as une FK vers Niveau
        specialite = classe.specialite  # idem

        # Récupère tous les semestres si besoin
        semestres = Semestre.objects.all()
        semestres_data = [{"id": s.id, "libelle": s.libelle} for s in semestres]

        data = {
            "niveau": {"id": niveau.id, "libelle": niveau.libelle},
            "specialite": {"id": specialite.id, "nom": specialite.nom},
            "semestres": semestres_data
        }
        return JsonResponse(data)

    except Classe.DoesNotExist:
        return JsonResponse({"error": "Classe non trouvée"}, status=404)

@role_required(['Superviseur', 'Administrateur'])
def plan_etudes(request):
    current_year = datetime.now().year
    annee_scolaire = f"{current_year}-{current_year + 1}"

    if request.method == "POST":
        codePE = request.POST.get('codePE')
        enseignant_id = request.POST.get('enseignant')
        matiere_id = request.POST.get('matiere')
        classe_id = request.POST.get('classe')
        vh_semaine = request.POST.get('vh_semaine')
        nbre_semaine = request.POST.get('nbre_semaine')
        coef = request.POST.get('coef')
        credit = request.POST.get('credit')
        type_ue = request.POST.get('type_ue')
        niveau_id = request.POST.get('niveau')
        specialite_id = request.POST.get('specialite')
        filiere_id = request.POST.get('filiere')
        semestre_id = request.POST.get('semestre')
        diplome_id = request.POST.get('diplome')

        # Vérification des champs obligatoires
        if not all([codePE, enseignant_id, matiere_id, classe_id, vh_semaine, nbre_semaine,
                    coef, credit, type_ue, niveau_id, specialite_id, filiere_id,
                    semestre_id, diplome_id]):
            messages.error(request, "Tous les champs sont obligatoires.")
            return redirect("/plan_etudes")

        try:
            vhSemaine = float(vh_semaine)
            nbreSemaine = int(nbre_semaine)
            vhSemestre = vhSemaine * nbreSemaine
            coef_float = float(coef)
            credit_float = float(credit)

            PlanEtude.objects.create(
                codePE=codePE,
                enseignant=Enseignant.objects.get(pk=enseignant_id),
                matiere=Matiere.objects.get(pk=matiere_id),
                classe=Classe.objects.get(pk=classe_id),
                vhSemaine=vhSemaine,
                vhSemestre=vhSemestre,
                nbreSemaine=nbreSemaine,
                coef=coef_float,
                typeUE=type_ue,
                totalCoef=int(coef_float),  # IntegerField => conversion
                totalCredit=int(credit_float),
                niveau=Niveau.objects.get(pk=niveau_id),
                specialite=Specialite.objects.get(pk=specialite_id),
                filiere=Filiere.objects.get(pk=filiere_id),
                semestre=Semestre.objects.get(pk=semestre_id),
                diplome=Diplome.objects.get(pk=diplome_id),
                volume_horaire=int(vhSemestre),
                coefficient=coef_float,
                credit=credit_float
            )

            messages.success(request, "Plan d'étude enregistré avec succès.")
            return redirect("/liste_plan_etudes")

        except Exception as e:
            messages.error(request, f"Erreur lors de l'enregistrement : {str(e)}")
            return redirect("/plan_etudes")

    # GET : Chargement des listes
    context = {
        "annee_scolaire": annee_scolaire,
        "enseignants": Enseignant.objects.all(),
        "matieres": Matiere.objects.all(),
        "classes": Classe.objects.all(),
        "filieres": Filiere.objects.all(),
        "niveaux": Niveau.objects.all(),
        "specialites": Specialite.objects.all(),
        "semestres": Semestre.objects.all(),
        "diplomes": Diplome.objects.all(),
    }
    return render(request, "gestion/production/plan_etudes.html", context)

def liste_plan_etudes(request):
    plans = PlanEtude.objects.select_related('enseignant', 'matiere', 'classe').all()
    return render(request, 'gestion/production/liste_plan_etudes.html', {'plans': plans})

def modifier_plan_etude(request, id):
    plan = get_object_or_404(PlanEtude, id=id)
    
    if request.method == "POST":
        # (mêmes champs que dans plan_etudes)
        plan.codePE = request.POST.get('codePE')
        plan.vhSemaine = request.POST.get('vh_semaine')
        plan.nbreSemaine = request.POST.get('nbre_semaine')
        plan.vhSemestre = float(plan.vhSemaine) * int(plan.nbreSemaine)
        plan.coef = request.POST.get('coef')
        plan.credit = request.POST.get('credit')
        plan.typeUE = request.POST.get('type_ue')
        plan.save()
        messages.success(request, "Plan modifié avec succès.")
        return redirect('/liste_plan_etudes')
    
    return render(request, 'gestion/production/modifier_plan_etude.html', {
        'plan': plan,
        # Ajoute ici les listes si tu veux les recharger dans le formulaire
    })

def supprimer_plan_etude(request, id):
    plan = get_object_or_404(PlanEtude, id=id)
    plan.delete()
    messages.success(request, "Plan supprimé avec succès.")
    return redirect('/liste_plan_etudes')


def emploi_du_temps(request):
    current_year = datetime.now().year
    annee_scolaire = f"{current_year}-{current_year + 1}"

    jours = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi']
    creneaux = ['8h30-10h00', '10h30-12h00', '13h00-14h30', '14h45-16h15']

    if request.method == "POST":
        try:
            classe_id = request.POST.get('classe')
            diplome_id = request.POST.get('diplome')
            specialite_id = request.POST.get('specialite')
            niveau_id = request.POST.get('niveau')
            semestre_id = request.POST.get('semestre')
            salle_id = request.POST.get('salle')

            if not all([classe_id, diplome_id, specialite_id, niveau_id, semestre_id, salle_id]):
                messages.error(request, "Tous les champs principaux sont obligatoires")
                return redirect("/emploi_du_temps")

            emploi, created = EmploiDuTemps.objects.get_or_create(
                classe_id=classe_id,
                diplome_id=diplome_id,
                specialite_id=specialite_id,
                niveau_id=niveau_id,
                semestre_id=semestre_id,
                salle_id=salle_id,
                defaults={'annee_scolaire': annee_scolaire}
            )

            # Supprimer les anciens créneaux
            CreneauHoraire.objects.filter(emploi_du_temps=emploi).delete()

            # Enregistrer les nouveaux créneaux
            for jour in jours:
                for creneau in creneaux:
                    field_name = f"{jour}_{creneau.replace(':', '').replace('-', '_')}"
                    plan_etude_id = request.POST.get(field_name)
                    if plan_etude_id and plan_etude_id != "vide":
                        CreneauHoraire.objects.create(
                            emploi_du_temps=emploi,
                            jour=jour.capitalize(),
                            creneau=creneau,
                            plan_etude_id=plan_etude_id
                        )

            messages.success(request, "Emploi du temps enregistré avec succès")
            # On continue sur la même page pour afficher le planning à jour

        except Exception as e:
            messages.error(request, f"Erreur technique : {str(e)}")
            return redirect("/emploi_du_temps")

    else:
        emploi = None

    # Chargement du formulaire : liste des choix
    classes = Classe.objects.all()
    diplomes = Diplome.objects.all()
    specialites = Specialite.objects.all()
    niveaux = Niveau.objects.all()
    semestres = Semestre.objects.all()
    salles = Salle.objects.all()
    plans_etudes = PlanEtude.objects.select_related('specialite', 'enseignant')

    # Si on a un emploi du temps (POST ou GET), on récupère les créneaux pour affichage
    creneaux_enregistres = {}
    if request.method == "POST" or emploi:
        if not emploi:
            # Si on est en GET, on peut essayer de récupérer l'emploi du temps en fonction des filtres (optionnel)
            emploi = None
        if emploi:
            creneaux_qs = CreneauHoraire.objects.filter(emploi_du_temps=emploi)\
                .select_related('plan_etude', 'plan_etude__specialite', 'plan_etude__enseignant', 'emploi_du_temps', 'emploi_du_temps__salle')
            for c in creneaux_qs:
                key = f"{c.jour.lower()}:{c.creneau}"
                creneaux_enregistres[key] = c

    context = {
        "annee_scolaire": annee_scolaire,
        "classes": classes,
        "diplomes": diplomes,
        "specialites": specialites,
        "niveaux": niveaux,
        "semestres": semestres,
        "salles": salles,
        "plans_etudes": plans_etudes,
        "jours": jours,
        "creneaux": creneaux,
        "creneaux_enregistres": creneaux_enregistres,
    }

    return render(request, "gestion/production/emploi_du_temps.html", context)

def absences(request):
    return render(request, "gestion/production/absences.html")


def elimination(request):
    return render(request, "gestion/production/elimination.html")

@role_required(['Superviseur', 'Administrateur'])
def saisie_des_notes(request):
    classes = Classe.objects.all()
    matieres = Matiere.objects.all()
    etudiants = []
    selected_classe = ''

    if request.method == "POST":
        classe_id = request.POST.get('classe')
        matiere_id = request.POST.get('matiere')
        dateExamen = request.POST.get('dateExamen')

        if classe_id and not matiere_id:
            etudiants = Etudiant.objects.filter(classe_id=classe_id)
            selected_classe = classe_id

        elif classe_id and matiere_id and dateExamen:
            etudiants = Etudiant.objects.filter(classe_id=classe_id)
            for etudiant in etudiants:
                noteCC = request.POST.get(f'noteCC_{etudiant.id}')
                noteExam = request.POST.get(f'noteExam_{etudiant.id}')
                observationCC = request.POST.get(f'observationCC_{etudiant.id}', '')
                observationExamen = request.POST.get(f'observationExamen_{etudiant.id}', '')
                if noteCC and noteExam:
                    moyenne = (float(noteCC) * 0.4) + (float(noteExam) * 0.6)
                    Note.objects.create(
                        etudiant=etudiant,
                        matiere_id=matiere_id,
                        classe_id=classe_id,
                        session=etudiant.session,
                        noteCC=noteCC,
                        noteExam=noteExam,
                        moyenne=moyenne,
                        observationCC=observationCC,
                        observationExamen=observationExamen,
                        dateExamen=dateExamen
                        
                    )
            messages.success(request, "Les notes ont été enregistrées avec succès.")
            return redirect('/liste_saisie_des_notes')

    return render(request, 'gestion/production/saisie_des_notes.html', {
        'classes': classes,
        'matieres': matieres,
        'etudiants': etudiants,
        'selected_classe': selected_classe,
    })


def liste_saisie_des_notes(request):
    classes = Classe.objects.all()
    matieres = Matiere.objects.all()
    notes = []
    selected_classe = ''
    selected_matiere = ''

    if request.method == 'POST':
        action = request.POST.get('action')

        # Si action = rechercher (bouton rechercher)
        if action == 'rechercher':
            selected_classe = request.POST.get('classe')
            selected_matiere = request.POST.get('matiere')

        # Sinon action modifier ou supprimer (sur une note)
        elif action in ['modifier', 'supprimer']:
            note_id = request.POST.get('note_id')
            note = get_object_or_404(Note, pk=note_id)

            # Garder la sélection pour afficher la liste à jour après action
            selected_classe = request.POST.get('classe_id')
            selected_matiere = request.POST.get('matiere_id')

            if action == 'modifier':
                note.noteCC = request.POST.get('noteCC')
                note.observationCC = request.POST.get('observationCC')
                note.noteExam = request.POST.get('noteExam')
                note.observationExamen = request.POST.get('observationExamen')
                note.moyenne = (float(note.noteCC) * 0.4 + float(note.noteExam) * 0.6)
                note.save()
                messages.success(request, "Note mise à jour avec succès.")

            elif action == 'supprimer':
                note.delete()
                messages.warning(request, "Note supprimée.")

    # Filtrer les notes selon la sélection
    if selected_classe and selected_matiere:
        notes = Note.objects.filter(classe_id=selected_classe, matiere_id=selected_matiere)

    return render(request, 'gestion/production/liste_saisie_des_notes.html', {
        'classes': classes,
        'matieres': matieres,
        'notes': notes,
        'selected_classe': selected_classe,
        'selected_matiere': selected_matiere,
    })

@role_required(['Superviseur', 'Administrateur'])
def dashboard_administrateur(request):
    return render(request, 'gestion/production/dashboard_administrateur.html')

@role_required(['Agent'])
def dashboard_agent(request):
    return render(request, 'gestion/production/dashboard_agent.html')

def unauthorized(request):
    return render(request, 'gestion/production/unauthorized.html')


@role_required(['Superviseur', 'Administrateur'])
def Tarif_view(request):
    return render(request, 'gestion/production/Tarif.html', {
        'titre_page': 'Tarif',
    })
