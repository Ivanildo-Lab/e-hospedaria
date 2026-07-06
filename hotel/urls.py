from django.urls import path
from . import views

app_name = 'hotel'

urlpatterns = [
    path('mapa/', views.mapa_quartos, name='mapa_quartos'),
    path('checkin/<int:quarto_id>/', views.realizar_checkin, name='realizar_checkin'),
    path('liberar/<int:quarto_id>/', views.liberar_limpeza, name='liberar_limpeza'),
    path('checkout/<int:hospedagem_id>/', views.realizar_checkout, name='realizar_checkout'),
    path('comprovante/<int:hospedagem_id>/', views.imprimir_comprovante, name='imprimir_comprovante'),
    path('historico/', views.historico_hospedagens, name='historico_hospedagens'),
    path('categorias/', views.lista_categorias, name='lista_categorias'),
    path('categorias/nova/', views.nova_categoria, name='nova_categoria'),
    path('categorias/editar/<int:categoria_id>/', views.editar_categoria, name='editar_categoria'),
    path('categorias/excluir/<int:categoria_id>/', views.excluir_categoria, name='excluir_categoria'),
    path('quartos/', views.lista_quartos, name='lista_quartos'),
    path('quartos/novo/', views.novo_quarto, name='novo_quarto'),
    path('quartos/editar/<int:quarto_id>/', views.editar_quarto, name='editar_quarto'),
    path('quartos/excluir/<int:quarto_id>/', views.excluir_quarto, name='excluir_quarto'),

]