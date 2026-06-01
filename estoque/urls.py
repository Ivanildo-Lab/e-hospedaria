from django.urls import path
from . import views

app_name = 'estoque'

urlpatterns = [
    path('produtos/', views.lista_produtos, name='lista_produtos'),
    path('movimentacao/', views.entrada_estoque, name='entrada_estoque'),
    path('reposicao/', views.relatorio_reposicao, name='relatorio_reposicao'),
]