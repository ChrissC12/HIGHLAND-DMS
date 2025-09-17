# generator/urls.py

from django.urls import path
from . import views

# This defines a namespace for your app's URLs, which is a best practice.
app_name = 'generator'

urlpatterns = [
    # ==============================================================================
    # DASHBOARD URLS
    # ==============================================================================
    path('', views.id_card_dashboard, name='id_card_dashboard'),
    path('invoices/', views.invoice_dashboard, name='invoice_dashboard'),

    # ==============================================================================
    # ID CARD URLS
    # ==============================================================================
    path('preview/<int:employee_id>/', views.id_card_preview, name='id_card_preview'),
    path('preview/tangible/<int:employee_id>/', views.id_card_tangible_preview, name='id_card_tangible_preview'),
    path('download/pdf/<int:employee_id>/', views.download_id_card_pdf, name='download_id_card_pdf'),

    # ==============================================================================
    # BUSINESS CARD URLS
    # ==============================================================================
    path('business-card/preview/<int:employee_id>/', views.business_card_preview, name='business_card_preview'),

    # ==============================================================================
    # INVOICE URLS
    # ==============================================================================
    path('invoices/create/', views.create_invoice, name='create_invoice'),
    path('invoices/preview/<int:invoice_id>/', views.invoice_preview, name='invoice_preview'),
    path('invoices/download/pdf/<int:invoice_id>/', views.download_invoice_pdf, name='download_invoice_pdf'),
    path('invoices/print/<int:invoice_id>/', views.invoice_print, name='invoice_print'),
    path('package/download/<int:employee_id>/<int:invoice_id>/', views.download_welcome_package, name='download_welcome_package'),
]