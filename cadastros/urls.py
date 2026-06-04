# cadastros/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('lista/', views.lista_hospedes, name='lista_hospedes'), # Nome mantido para não quebrar o base.html
    path('novo/', views.novo_hospede, name='novo_hospede'),
    path('editar/<int:pk>/', views.editar_cadastro, name='editar_cadastro'),
    path('excluir/<int:pk>/', views.excluir_cadastro, name='excluir_cadastro'),
    path('fornecedores/', views.lista_fornecedores, name='lista_fornecedores'),
    path('fornecedores/novo/', views.novo_fornecedor, name='novo_fornecedor'),
    
]