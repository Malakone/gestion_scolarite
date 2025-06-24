from django import forms
from .models import *

class SpecialiteForm(forms.ModelForm):
    class Meta:
        model = Specialite
        fields = ['libelle', 'DomaineFormation', 'Mention', 'PrincipauxDomaine', 'ExigencesDuProgramme', 'filiere', 'diplome']
        widgets = {
            'libelle': forms.TextInput(attrs={'class': 'form-control'}),
            'DomaineFormation': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'Mention': forms.TextInput(attrs={'class': 'form-control'}),
            'PrincipauxDomaine': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ExigencesDuProgramme': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'filiere': forms.Select(attrs={'class': 'form-control'}),
            'diplome': forms.Select(attrs={'class': 'form-control'}),
        }

class AbsenceForm(forms.ModelForm):
    class Meta:
        model = Absence
        fields = ['matiere', 'etudiant', 'dateAbsence', 'justification']

    def __init__(self, *args, **kwargs):
        enseignant = kwargs.pop('enseignant')
        super().__init__(*args, **kwargs)
        self.fields['matiere'].queryset = Matiere.objects.filter(enseignant=enseignant)
        self.fields['etudiant'].queryset = Etudiant.objects.all()  # tu peux filtrer davantage ici

class DepotCoursForm(forms.ModelForm):
    class Meta:
        model = Cours
        fields = ['matiere', 'fichier']

    def __init__(self, *args, **kwargs):
        enseignant = kwargs.pop('enseignant')
        super().__init__(*args, **kwargs)
        self.fields['matiere'].queryset = Matiere.objects.filter(enseignant=enseignant)
