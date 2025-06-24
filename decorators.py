from django.shortcuts import redirect
from functools import wraps
from django.contrib import messages
from .models import *

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user

            if not user.is_authenticated:
                messages.error(request, "Authentification requise.")
                return redirect('gestion:login')

            user_groups = user.groups.values_list('name', flat=True)

            # Cas général pour les groupes (Superviseur, Agent, Enseignant, etc.)
            if any(role in user_groups for role in allowed_roles):
                return view_func(request, *args, **kwargs)

            # Cas spécial : rôle Etudiant (lié par FK ou OneToOne à user)
            if 'Etudiant' in allowed_roles and hasattr(user, 'etudiant'):
                return view_func(request, *args, **kwargs)

            messages.error(request, "Accès refusé. Permissions insuffisantes.")
            return redirect('gestion:unauthorized')

        return _wrapped_view
    return decorator
