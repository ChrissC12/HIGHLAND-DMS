# generator/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.http import FileResponse
from django.forms import inlineformset_factory
from django.contrib import messages
# Import all the models we need from our models.py file
from .models import Employee, CompanyInfo, BusinessCard, Invoice, InvoiceItem
# Import our PDF generation utilities
from .pdf_utils import generate_id_card_pdf, generate_invoice_pdf
from .pdf_utils import generate_welcome_package_pdf


# ==============================================================================
# DASHBOARD VIEWS
# ==============================================================================
def id_card_dashboard(request):
    """
    Displays the main dashboard with a list of all employees,
    allowing the user to select one to generate a document for.
    """
    employees = Employee.objects.all().order_by('full_name')
    context = {
        'employees': employees
    }
    return render(request, 'generator/id_card_dashboard.html', context)


def invoice_dashboard(request):
    """
    Displays a list of all created invoices.
    """
    invoices = Invoice.objects.all().order_by('-issue_date')
    context = {
        'invoices': invoices
    }
    return render(request, 'generator/invoice_dashboard.html', context)


# ==============================================================================
# ID CARD VIEWS
# ==============================================================================
def id_card_preview(request, employee_id):
    """
    Renders the simple, clean "printable sheet" preview of the ID card.
    """
    employee = get_object_or_404(Employee, id=employee_id)
    company_info = CompanyInfo.objects.first()
    context = {
        'employee': employee,
        'company_info': company_info,
    }
    return render(request, 'generator/id_card_preview.html', context)


def id_card_tangible_preview(request, employee_id):
    """
    Renders the realistic, "tangible" 3D preview of the ID card.
    """
    employee = get_object_or_404(Employee, id=employee_id)
    company_info = CompanyInfo.objects.first()
    context = {
        'employee': employee,
        'company_info': company_info,
    }
    return render(request, 'generator/id_card_tangible_preview.html', context)


def download_id_card_pdf(request, employee_id):
    """
    Generates and serves a print-ready PDF of the employee's ID card.
    """
    employee = get_object_or_404(Employee, id=employee_id)
    company_info = CompanyInfo.objects.first()
    pdf_buffer = generate_id_card_pdf(employee, company_info)
    filename = f"Highland_ID_Card_{employee.employee_id}.pdf"
    return FileResponse(pdf_buffer, as_attachment=True, filename=filename)


# ==============================================================================
# BUSINESS CARD VIEWS
# ==============================================================================
def business_card_preview(request, employee_id):
    """
    Renders a preview of the business card for a specific employee.
    """
    employee = get_object_or_404(Employee, id=employee_id)
    company_info = CompanyInfo.objects.first()
    business_card, created = BusinessCard.objects.get_or_create(employee=employee)
    context = {
        'employee': employee,
        'company_info': company_info,
        'card': business_card,
    }
    return render(request, 'generator/business_card_preview.html', context)


# ==============================================================================
# INVOICE VIEWS
# ==============================================================================
def create_invoice(request):
    """
    Handles the creation of a new invoice with its line items.
    """
    InvoiceItemFormSet = inlineformset_factory(
        Invoice, InvoiceItem, fields=('description', 'quantity', 'unit_price'),
        extra=1, can_delete=True
    )

    if request.method == 'POST':
        due_date_str = request.POST.get('due_date')
        due_date = due_date_str if due_date_str else None

        # --- THIS IS THE FIX ---
        # We REMOVE 'tax_rate' and ADD 'client_phone'.
        invoice = Invoice.objects.create(
            invoice_number=request.POST.get('invoice_number', ''),
            issue_date=request.POST.get('issue_date'),
            due_date=due_date,
            client_name=request.POST.get('client_name', ''),
            client_address=request.POST.get('client_address', ''),
            client_phone=request.POST.get('client_phone', ''), # ADD this line
            other_comments=request.POST.get('other_comments', ''),
            terms_of_payment=request.POST.get('terms_of_payment', '')
        )
        # --- END OF FIX ---
        
        formset = InvoiceItemFormSet(request.POST, instance=invoice)
        
        if formset.is_valid():
            formset.save()
            messages.success(request, f"Invoice {invoice.invoice_number} created successfully!")
            return redirect('generator:invoice_preview', invoice_id=invoice.id)
        else:
            invoice.delete()
            messages.error(request, "Please correct the errors in the invoice items.")
            formset_with_errors = InvoiceItemFormSet(request.POST)
            context = {'formset': formset_with_errors}
            return render(request, 'generator/create_invoice.html', context)

    else:
        formset = InvoiceItemFormSet(queryset=InvoiceItem.objects.none())

    context = {
        'formset': formset
    }
    return render(request, 'generator/create_invoice.html', context)
    
def invoice_preview(request, invoice_id):
    """
    Displays a preview of the generated invoice before downloading.
    """
    invoice = get_object_or_404(Invoice, id=invoice_id)
    company_info = CompanyInfo.objects.first()
    context = {
        'invoice': invoice,
        'company_info': company_info,
    }
    return render(request, 'generator/invoice_preview.html', context)


def download_invoice_pdf(request, invoice_id):
    """
    Generates and serves a print-ready PDF of the final invoice.
    """
    invoice = get_object_or_404(Invoice, id=invoice_id)
    company_info = CompanyInfo.objects.first()

    # Call the PDF generation utility to create the PDF in memory.
    pdf_buffer = generate_invoice_pdf(invoice, company_info)

    # Create a clean filename for the download.
    filename = f"Invoice_{invoice.invoice_number}_{invoice.client_name.replace(' ', '_')}.pdf"

    # Serve the generated PDF as a file download.
    return FileResponse(pdf_buffer, as_attachment=True, filename=filename)

def invoice_print(request, invoice_id):
    """
    Renders a clean, print-only version of the invoice.
    """
    invoice = get_object_or_404(Invoice, id=invoice_id)
    company_info = CompanyInfo.objects.first()
    context = {
        'invoice': invoice,
        'company_info': company_info
    }
    return render(request, 'generator/invoice_print.html', context)


def download_welcome_package(request, employee_id, invoice_id):
    """
    Generates a single PDF containing the invoice and ID card for a new hire.
    """
    employee = get_object_or_404(Employee, id=employee_id)
    invoice = get_object_or_404(Invoice, id=invoice_id)
    company_info = CompanyInfo.objects.first()

    # Call the new all-in-one PDF generation utility
    pdf_buffer = generate_welcome_package_pdf(employee, invoice, company_info)
    
    filename = f"Welcome_Package_{employee.full_name.replace(' ', '_')}.pdf"
    
    return FileResponse(pdf_buffer, as_attachment=True, filename=filename)