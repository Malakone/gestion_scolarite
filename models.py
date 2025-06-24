from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class Diplome(models.Model):
    libelle = models.CharField(max_length=20)
    duree = models.CharField(max_length=50, blank=True, null=True)  # durée en texte, ex: "3 ans"
    credit = models.IntegerField(blank=True, null=True)
    def __str__(self):
        return self.libelle
    
class SituationFamiliale(models.Model):
    libelle = models.CharField(max_length=100)
    def __str__(self):
        return self.libelle

class Nationalite(models.Model):
    libelle = models.CharField(max_length=100)
    def __str__(self):
        return self.libelle

class Sexe(models.Model):
    libelle = models.CharField(max_length=50)
    def __str__(self):
        return self.libelle

class NatureBac(models.Model):
    libelle = models.CharField(max_length=100)
    def __str__(self):
        return self.libelle

class Niveau(models.Model):
    libelle = models.CharField(max_length=50)
    def __str__(self):
        return self.libelle

class Filiere(models.Model):
    libelle = models.CharField(max_length=100)
    duree = models.SmallIntegerField()
    credit = models.IntegerField()
    def __str__(self):
        return self.libelle

class Mention(models.Model):
    libelle = models.CharField(max_length=50)
    def __str__(self):
        return self.libelle

class Specialite(models.Model):
    libelle = models.CharField(max_length=100)
    DomaineFormation = models.TextField(max_length=100)
    Mention = models.CharField(max_length=100)
    PrincipauxDomaine = models.TextField(max_length=100)
    ExigencesDuProgramme = models.TextField(max_length=100)
    filiere = models.ForeignKey(Filiere, on_delete=models.SET_NULL, null=True)
    diplome = models.ForeignKey(Diplome, on_delete=models.SET_NULL, null=True)
    def __str__(self):
        return self.libelle

class Salle(models.Model):
    libelle = models.CharField(max_length=50)
    def __str__(self):
        return self.libelle

class Semestre(models.Model):
    libelle = models.CharField(max_length=100)
    def __str__(self):
        return self.libelle

class Classe(models.Model):
    libelle = models.CharField(max_length=100)
    specialite = models.ForeignKey(Specialite, on_delete=models.SET_NULL, null=True)
    semestre = models.ForeignKey(Semestre, on_delete=models.SET_NULL, null=True)
    niveau = models.ForeignKey(Niveau, on_delete=models.SET_NULL, null=True)
    def __str__(self):
        return self.libelle

class Enseignant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='enseignant')
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    numTel = models.IntegerField()
    grade = models.CharField(max_length=100)
    CIN = models.CharField(max_length=100)
    email = models.EmailField()
    specialite = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.nom} {self.prenom}"

class Session(models.Model):
    libelle = models.CharField(max_length=100)
    DelibSP = models.DateField()
    DelibSR = models.DateField()
    def __str__(self):
        return self.libelle

class Entreprise(models.Model):
    pays = models.CharField(max_length=100)
    ville = models.CharField(max_length=100)
    adresse = models.CharField(max_length=200)
    numTel = models.IntegerField()
    fax = models.IntegerField()
    email = models.EmailField()
    PDG = models.CharField(max_length=50)
    SecretaireG = models.CharField(max_length=50)
    DStage = models.CharField(max_length=50)
    Directeur = models.CharField(max_length=50)
    siteweb = models.CharField(max_length=100)
    logo = models.CharField(max_length=100, default="path/to/logo.png")
    nomCommercial = models.CharField(max_length=200)
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True)
    def __str__(self):
        return self.nomCommercial

class Tuteur(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    numTel = models.CharField(max_length=100)
    email = models.EmailField()
    def __str__(self):
        return f"{self.nom} {self.prenom}"


class Etudiant(models.Model):
    code_etudiant = models.CharField(max_length=20, unique=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    sexe = models.ForeignKey(Sexe, on_delete=models.SET_NULL, null=True)
    datenaiss = models.DateField()
    lieuNaiss = models.CharField(max_length=20)
    nationalite = models.ForeignKey(Nationalite, on_delete=models.SET_NULL, null=True)
    situationfamiliale = models.ForeignKey(SituationFamiliale, on_delete=models.SET_NULL, null=True)
    CIN_Passeport = models.CharField(unique=True, max_length=50)
    datePasseport = models.DateField()
    lieuPassport = models.CharField(max_length=50)
    adresse = models.CharField(max_length=50)
    CP = models.IntegerField()
    email = models.EmailField()
    numTel = models.IntegerField()
    pays = models.CharField(max_length=50)
    ville = models.CharField(max_length=50)
    boursier = models.BooleanField(default=False)
    dateInscription = models.DateField()
    anneeBac = models.IntegerField()
    nature_bac = models.ForeignKey(NatureBac, on_delete=models.SET_NULL, null=True)
    mentionBac = models.ForeignKey(Mention, on_delete=models.SET_NULL, null=True)
    etablissementBac = models.CharField(max_length=50)
    paysBac = models.CharField(max_length=50)
    emailUMT = models.EmailField()
    numBac = models.CharField(max_length=50)
    diplome = models.ForeignKey(Diplome, on_delete=models.SET_NULL, null=True)
    specialite = models.ForeignKey(Specialite, on_delete=models.SET_NULL, null=True)
    filiere = models.ForeignKey(Filiere, on_delete=models.SET_NULL, null=True)
    niveau = models.ForeignKey(Niveau, on_delete=models.SET_NULL, null=True)
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True)
    classe = models.ForeignKey(Classe, on_delete=models.SET_NULL, null=True)
    affectationTarif = models.FloatField()
    devise = models.CharField(max_length=50)
    etat = models.CharField(max_length=50)
    tuteur = models.ForeignKey(Tuteur, on_delete=models.CASCADE)
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE, related_name='etudiant')
    def __str__(self):
        return f"{self.user.username}"
    
class Matiere(models.Model):
    libelle = models.CharField(max_length=50)
    coefficient = models.IntegerField(default=1)
    credit = models.IntegerField(default=1)
    enseignant = models.ForeignKey('Enseignant', on_delete=models.SET_NULL, null=True, blank=True, related_name='matieres')


    def __str__(self):
        return self.libelle


class PlanEtude(models.Model):
    codePE = models.CharField(max_length=20)
    vhSemaine = models.FloatField()
    vhSemestre = models.FloatField()
    nbreSemaine = models.SmallIntegerField()
    coef = models.FloatField()
    typeUE = models.CharField(max_length=50)
    totalCoef = models.IntegerField()
    totalCredit = models.IntegerField()
    enseignant = models.ForeignKey(Enseignant, on_delete=models.CASCADE)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE, default=1)
    niveau = models.ForeignKey(Niveau, on_delete=models.CASCADE)
    specialite = models.ForeignKey(Specialite, on_delete=models.CASCADE)
    semestre = models.ForeignKey(Semestre, on_delete=models.CASCADE)
    diplome = models.ForeignKey(Diplome, on_delete=models.SET_NULL, null=True)
    matiere = models.ForeignKey(Matiere, on_delete=models.SET_NULL, null=True)
    volume_horaire = models.IntegerField(default=20)
    coefficient = models.FloatField(default=1.0)
    credit = models.FloatField()

class Planning(models.Model):
    jour = models.CharField(max_length=20)
    heuredeb = models.TimeField()
    heurefin = models.TimeField()
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    salle = models.ForeignKey(Salle, on_delete=models.CASCADE)
    planetude = models.ForeignKey(PlanEtude, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    matiere = models.ForeignKey('Matiere', on_delete=models.CASCADE, null=True, blank=True)


class Absence(models.Model):
    planning = models.ForeignKey(Planning, on_delete=models.SET_NULL, null=True)
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE, null=True, blank=True)
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    dateAbsence = models.DateField()
    justification = models.CharField(max_length=255, blank=True, null=True)


class Affectation(models.Model):
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    specialite = models.ForeignKey(Specialite, on_delete=models.CASCADE)
    niveau = models.ForeignKey(Niveau, on_delete=models.CASCADE, default=1)
    diplome = models.ForeignKey(Diplome, on_delete=models.CASCADE, default=1)
    semestre = models.ForeignKey(Semestre, on_delete=models.CASCADE)
    nombre_etudiants = models.IntegerField(default=0)
    def __str__(self):
        return f"{self.classe} - {self.specialite} - {self.semestre}"
    
    def nombre_etudiants(self):
        return Etudiant.objects.filter(classe=self.classe, specialite=self.specialite, niveau=self.niveau).count()
class Elimination(models.Model):
    nbreAbsence = models.IntegerField()
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    motif = models.TextField()

class EtatPaiement(models.Model):
    codeEtudiant = models.IntegerField()
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    etatEtudiant = models.CharField(max_length=50)
    tarifAffecte = models.DecimalField(max_digits=10, decimal_places=2)
    montantPaye = models.DecimalField(max_digits=10, decimal_places=2)
    solde = models.DecimalField(max_digits=10, decimal_places=2)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)

class Historique(models.Model):
    reference = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    dateImpression = models.DateField()
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    specialite = models.ForeignKey(Specialite, on_delete=models.CASCADE)
    niveau = models.ForeignKey(Niveau, on_delete=models.CASCADE)
    def __str__(self):
        return self.designation

class Note(models.Model):
    dateExamen = models.DateField()
    noteCC = models.FloatField()
    observationCC = models.CharField(max_length=100)
    noteExam = models.FloatField()
    observationExamen = models.CharField(max_length=100)
    moyenne = models.FloatField()
    dateRattrapage = models.DateField(null=True, blank=True)
    noteRattrapage = models.FloatField(null=True, blank=True)
    moyRattrapage = models.FloatField(null=True, blank=True)
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)

class PVNote(models.Model):
    moyGen = models.FloatField()
    somNotes = models.FloatField()
    totalCoeff = models.IntegerField()
    totalCredit = models.IntegerField()
    creditValide = models.IntegerField()
    resultat = models.CharField(max_length=100)
    mention = models.CharField(max_length=50)
    somNotesRat = models.FloatField()
    moyRat = models.FloatField()
    resultatRat = models.CharField(max_length=100)
    mentionRat = models.CharField(max_length=100)
    etudiant = models.ForeignKey(Etudiant, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)

class EmploiDuTemps(models.Model):
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    diplome = models.ForeignKey(Diplome, on_delete=models.CASCADE)
    specialite = models.ForeignKey(Specialite, on_delete=models.CASCADE)
    niveau = models.ForeignKey(Niveau, on_delete=models.CASCADE)
    semestre = models.ForeignKey(Semestre, on_delete=models.CASCADE)
    salle = models.ForeignKey(Salle, on_delete=models.CASCADE)

class CreneauHoraire(models.Model):
    JOURS = [
        ('Lundi', 'Lundi'),
        ('Mardi', 'Mardi'),
        ('Mercredi', 'Mercredi'),
        ('Jeudi', 'Jeudi'),
        ('Vendredi', 'Vendredi'),
        ('Samedi', 'Samedi'),
    ]
    
    CRENEAUX = [
        ('8h30-10h00', '8h30-10h00'),
        ('10h30-12h00', '10h30-12h00'),
        ('13h00-14h30', '13h00-14h30'),
        ('14h45-16h15', '14h45-16h15'),
    ]
    
    emploi_du_temps = models.ForeignKey(EmploiDuTemps, on_delete=models.CASCADE, related_name='creneaux')
    jour = models.CharField(max_length=10, choices=JOURS)
    creneau = models.CharField(max_length=20, choices=CRENEAUX)
    plan_etude = models.ForeignKey(PlanEtude, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('emploi_du_temps', 'jour', 'creneau')
        verbose_name = "Créneau horaire"
        verbose_name_plural = "Créneaux horaires"
    
    def __str__(self):
        return f"{self.jour} {self.creneau} - {self.plan_etude.matiere.libelle}"
    
class TarifMvt(models.Model):
    datePrevu = models.DateField()
    montantPrevu = models.FloatField()
    datePayement = models.DateField()
    montantPayement = models.FloatField()
    modePaiement = models.CharField(max_length=100)
    numRecu = models.CharField(max_length=100)
    banque = models.CharField(max_length=50)

class Cours(models.Model):
    enseignant = models.ForeignKey(Enseignant, on_delete=models.CASCADE)
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    fichier = models.FileField(upload_to='cours/')
    date_upload = models.DateTimeField(auto_now_add=True)

