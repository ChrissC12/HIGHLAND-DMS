# generator/models.py

from django.db import models
from django.utils import timezone
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, SmartResize

# ==============================================================================
# COMPANY AND EMPLOYEE MODELS
# ==============================================================================

class CompanyInfo(models.Model):
    """
    Stores the central information for the company, used on all documents.
    """
    name = models.CharField(max_length=255, default="HIGHLAND COMPANY LTD")
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    
    # --- Fields for the Invoice ---
    tin_number = models.CharField("TIN Number", max_length=100, blank=True, null=True)
    bank_name = models.CharField(max_length=255, blank=True, null=True, help_text="e.g., CRDB Bank")
    account_number = models.CharField("Bank A/C Number", max_length=100, blank=True, null=True)
    account_name = models.CharField("Bank A/C Name", max_length=255, blank=True, null=True)
    TIN = models.CharField("TIN", max_length=255, blank=True, null=True)
    
    # --- Fields for Business Card ---
    tagline = models.CharField(max_length=255, blank=True, null=True, help_text="e.g., Quality Solutions, Delivered.")
    linkedin_url = models.URLField("LinkedIn URL", blank=True, null=True)
    instagram_url = models.URLField("Instagram URL", blank=True, null=True)
    facebook_url = models.URLField("Facebook URL", blank=True, null=True)
    qr_code = models.ImageField(upload_to='company_qr_codes/', blank=True, editable=False)
    
    # Thumbnail for automatic resizing
    logo_thumbnail = ImageSpecField(source='logo', processors=[SmartResize(100, 100)], format='PNG', options={'quality': 95})

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.pk and self.website and not self.qr_code:
            qr_image = qrcode.make(self.website)
            buffer = BytesIO()
            qr_image.save(buffer, format='PNG')
            file_name = f'company_qr_{self.pk}.png'
            self.qr_code.save(file_name, ContentFile(buffer.getvalue()), save=False)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Company Information"


class Employee(models.Model):
    """
    Stores information for a single employee.
    """
    full_name = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='employee_photos/')
    employee_id = models.CharField(max_length=100, unique=True, blank=True, editable=False)
    qr_code = models.ImageField(upload_to='employee_qr_codes/', blank=True, editable=False)
    photo_thumbnail = ImageSpecField(source='photo', processors=[ResizeToFill(200, 200)], format='JPEG', options={'quality': 90})
    issue_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} ({self.employee_id or 'No ID'})"

    def save(self, *args, **kwargs):
        # ... (save method for Employee remains the same)
        should_generate_id = not self.employee_id
        should_generate_qr = not self.qr_code
        super().save(*args, **kwargs)
        fields_to_update = []
        if should_generate_id:
            year = timezone.now().strftime('%y')
            department_code = self.department[:3].upper()
            self.employee_id = f"{department_code}{year}-{self.pk}"
            fields_to_update.append('employee_id')
        if should_generate_qr:
            qr_data = f"Name: {self.full_name}\nID: {self.employee_id}\nTitle: {self.job_title}"
            qr_image = qrcode.make(qr_data)
            buffer = BytesIO()
            qr_image.save(buffer, format='PNG')
            file_name = f'qr_code_{self.pk}.png'
            self.qr_code.save(file_name, ContentFile(buffer.getvalue()), save=False)
            fields_to_update.append('qr_code')
        if fields_to_update:
            super().save(update_fields=fields_to_update)


class BusinessCard(models.Model):
    """
    Stores specific details for an employee's business card.
    """
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='business_card')
    personal_phone = models.CharField(max_length=100, blank=True, null=True)
    personal_email = models.EmailField(blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Business Card for {self.employee.full_name}"


# ==============================================================================
# INVOICE MODELS
# ==============================================================================

class Invoice(models.Model):
    # The invoice_number field can now be non-editable as it's auto-generated
    invoice_number = models.CharField(max_length=100, unique=True, blank=True, editable=False)
    issue_date = models.DateTimeField()
    due_date = models.DateTimeField(blank=True, null=True)
    client_name = models.CharField(max_length=255)
    client_address = models.TextField()
    client_phone = models.CharField(max_length=100, blank=True, null=True)
    other_comments = models.TextField(blank=True, null=True)
    terms_of_payment = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice {self.invoice_number} for {self.client_name}"

    def get_total(self):
        return sum(item.get_total() for item in self.items.all())
        
    def get_total_quantity(self):
        return sum(item.quantity for item in self.items.all())

    # =======================================================
    # THIS IS THE FIX: The new, automated save method
    # =======================================================
    def save(self, *args, **kwargs):
        # This logic runs only when a new invoice is being created
        if not self.invoice_number:
            # Find the highest existing invoice number
            last_invoice = Invoice.objects.all().order_by('id').last()
            if not last_invoice:
                # This is the very first invoice
                new_number = 1
            else:
                # Get the number from the last invoice's ID and add 1
                new_number = last_invoice.id + 1
            
            # Format the number with the "INV" prefix and leading zeros
            self.invoice_number = f'INV-{new_number:04d}'
        
        # Call the original save method to save the instance
        super().save(*args, **kwargs)


class InvoiceItem(models.Model):
    """
    Represents a single line item within an invoice.
    """
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=1.00) # Use Decimal for quantity like SQM
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.description

    def get_total(self):
        return self.quantity * self.unit_price