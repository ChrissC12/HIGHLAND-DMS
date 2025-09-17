# generator/pdf_utils.py

import io
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm, inch
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from django.contrib.humanize.templatetags.humanize import intcomma

# ==============================================================================
# ID CARD PDF GENERATION UTILITY
# ==============================================================================
CARD_WIDTH_MM = 85.6
CARD_HEIGHT_MM = 54

def generate_id_card_pdf(employee, company_info):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=(CARD_WIDTH_MM * mm, (CARD_HEIGHT_MM * 2 + 20) * mm))
    draw_card_front(p, employee, company_info, y_offset=(CARD_HEIGHT_MM + 10) * mm)
    draw_card_back(p, employee, company_info, y_offset=5 * mm)
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

def draw_card_front(p, employee, company_info, y_offset):
    # This function is correct and remains as is
    red = HexColor('#C0392B')
    gold = HexColor('#D4AF37')
    dark_blue = HexColor('#1A2C42')
    p.setFillColor(red)
    p.rect(0, y_offset, (CARD_WIDTH_MM * 0.35) * mm, CARD_HEIGHT_MM * mm, fill=1, stroke=0)
    p.setFillColorRGB(1, 1, 1)
    p.rect((CARD_WIDTH_MM * 0.35) * mm, y_offset, (CARD_WIDTH_MM * 0.65) * mm, CARD_HEIGHT_MM * mm, fill=1, stroke=0)
    if company_info and company_info.logo_thumbnail:
        logo_path = settings.MEDIA_ROOT / company_info.logo_thumbnail.name
        try: p.drawImage(logo_path, 5*mm, y_offset + 35*mm, width=20*mm, height=20*mm, preserveAspectRatio=True, mask='auto')
        except: pass
    p.setFillColorRGB(1, 1, 1)
    p.setFont("Helvetica-Bold", 8)
    p.saveState()
    p.rotate(90)
    p.drawString(y_offset + 10*mm, -15*mm, f"ID: {employee.employee_id}")
    p.restoreState()
    p.setFillColor(dark_blue)
    p.setFont("Helvetica-Bold", 10)
    p.drawString((CARD_WIDTH_MM * 0.35 + 5) * mm, y_offset + 45 * mm, employee.full_name)
    p.setFont("Helvetica", 8)
    p.drawString((CARD_WIDTH_MM * 0.35 + 5) * mm, y_offset + 40 * mm, employee.job_title)
    if employee.photo_thumbnail:
        photo_path = settings.MEDIA_ROOT / employee.photo_thumbnail.name
        try: p.drawImage(photo_path, (CARD_WIDTH_MM * 0.35 + 5) * mm, y_offset + 10 * mm, width=25*mm, height=25*mm, preserveAspectRatio=True)
        except: pass
    p.setStrokeColor(gold)
    p.setLineWidth(1.5)
    p.rect((CARD_WIDTH_MM * 0.35 + 4) * mm, y_offset + 9 * mm, 27*mm, 27*mm, fill=0, stroke=1)
    
def draw_card_back(p, employee, company_info, y_offset):
    # This function is correct and remains as is
    gold = HexColor('#D4AF37')
    dark_blue = HexColor('#1A2C42')
    p.setFillColorRGB(1, 1, 1)
    p.rect(0, y_offset, CARD_WIDTH_MM * mm, CARD_HEIGHT_MM * mm, fill=1, stroke=0)
    p.setFillColor(gold)
    p.rect(0, y_offset + (CARD_HEIGHT_MM - 2) * mm, CARD_WIDTH_MM * mm, 2 * mm, fill=1, stroke=0)
    p.setFillColor(dark_blue)
    p.setFont("Helvetica-Bold", 9)
    p.drawCentredString(CARD_WIDTH_MM * mm / 2, y_offset + 45 * mm, company_info.name)
    if employee.qr_code:
        qr_path = settings.MEDIA_ROOT / employee.qr_code.name
        try: p.drawImage(qr_path, (CARD_WIDTH_MM * mm / 2 - 12.5*mm), y_offset + 18 * mm, width=25*mm, height=25*mm, preserveAspectRatio=True)
        except: pass
    p.setFont("Helvetica", 6)
    text = p.beginText((CARD_WIDTH_MM * mm / 2), y_offset + 12 * mm)
    text.textAlignment = 1
    text.textLine(company_info.address or "")
    text.textLine(f"Phone: {company_info.phone or 'N/A'}")
    text.textLine(f"Email: {company_info.email or 'N/A'}")
    p.drawText(text)
    p.setFont("Helvetica-Oblique", 5)
    p.drawCentredString(CARD_WIDTH_MM * mm / 2, y_offset + 2 * mm, "This card is property of the company. If found, please return it.")


# ==============================================================================
# FINAL, HIGH-FIDELITY INVOICE PDF GENERATION UTILITY
# ==============================================================================
def generate_invoice_pdf(invoice, company_info):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize='A4')
    width, height = letter
    styles = getSampleStyleSheet()
    styles['Normal'].fontName = 'Helvetica'
    styles['Normal'].fontSize = 9
    styles['Normal'].leading = 12

    hc_red = HexColor('#C0392B')
    hc_gold = HexColor('#D4AF37')
    hc_dark = HexColor('#2C3E50')

    # --- 1. Header Section ---
    if company_info and company_info.logo:
        try:
            logo_path = settings.MEDIA_ROOT / company_info.logo.name
            p.drawImage(logo_path, 1*inch, height - 1.25*inch, width=0.8*inch, preserveAspectRatio=True, mask='auto')
        except: pass
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(1*inch, height - 1.5*inch, (company_info.name or "").upper())
    p.setFont("Helvetica", 9)
    p.drawString(1*inch, height - 1.7*inch, f"P.O.BOX {company_info.address or 'N/A'}, Dodoma")
    p.drawString(1*inch, height - 1.85*inch, company_info.phone or "N/A")
    p.setFillColor(HexColor('#0000FF'))
    p.drawString(1*inch, height - 2.0*inch, company_info.email or "N/A")
    p.setFillColor(black)

    p.setFont("Helvetica-Bold", 28)
    p.setFillColor(hc_red)
    p.drawRightString(width - 1*inch, height - 1.0*inch, "INVOICE")
    p.setFillColor(black)
    p.setFont("Helvetica", 9)
    p.drawRightString(width - 1*inch, height - 1.25*inch, f"Please Remitt to: {company_info.bank_name or 'N/A'}")
    p.drawRightString(width - 1*inch, height - 1.40*inch, f"A/C NO: {company_info.account_number or 'N/A'}")
    p.drawRightString(width - 1*inch, height - 1.55*inch, f"A/C NAME: {company_info.account_name or 'N/A'}")
    
    p.setStrokeColor(hc_gold)
    p.setLineWidth(2)
    p.line(1*inch, height - 2.2*inch, width - 1*inch, height - 2.2*inch)

    # --- 2. Info Grid Section ---
    p.setFillColor(hc_dark)
    p.rect(1*inch, height - 2.8*inch, 1*inch, 0.2*inch, fill=1, stroke=0)
    p.setFillColor(white)
    p.setFont("Helvetica-Bold", 10)
    p.drawString(1.1*inch, height - 2.75*inch, "BILL TO")
    p.setFillColor(black)
    p.setFont("Helvetica-Bold", 9)
    p.drawString(1*inch, height - 3.1*inch, invoice.client_name.upper())
    p.setFont("Helvetica", 9)
    p.drawString(1*inch, height - 3.25*inch, invoice.client_address)
    p.drawString(1*inch, height - 3.4*inch, invoice.client_phone or "")

    info_data = [
        ['DATE', invoice.issue_date.strftime('%m/%d/%Y %H:%M')],
        ['DUE DATE', invoice.due_date.strftime('%m/%d/%Y %H:%M') if invoice.due_date else 'N/A'],
        ['TIN NO.', company_info.tin_number or 'N/A'],
        ['INVOICE NO.', invoice.invoice_number],
    ]
    info_table = Table(info_data, colWidths=[1*inch, 2*inch])
    info_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, black),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,0), (0,-1), '#f2f2f2'),
    ]))
    info_table.wrapOn(p, width, height)
    info_table.drawOn(p, 4.5*inch, height - 3.1*inch)
    
    # --- 3. Items & Comments Tables ---
    table_y_start = height - 4.2*inch
    
    # Items Table
    header = [Paragraph('<b>DESCRIPTION</b>', styles['Normal']), Paragraph('<b>QUANTITY(SQM)</b>', styles['Normal']), Paragraph('<b>PRICE/UNIT</b>', styles['Normal']), Paragraph('<b>AMOUNT</b>', styles['Normal'])]
    data = [header]
    total_quantity = sum(item.quantity for item in invoice.items.all())
    
    for item in invoice.items.all():
        data.append([
            Paragraph(item.description.replace('\n', '<br/>'), styles['Normal']),
            intcomma(int(item.quantity)),
            f"TZS {intcomma(int(item.unit_price))}",
            f"TZS {intcomma(int(item.get_total()))}",
        ])
    
    data.append(['<b>TOTAL</b>', f'<b>{intcomma(int(total_quantity))}</b>', '', f"<b>TZS {intcomma(int(invoice.get_total()))}</b>"])
    
    item_table = Table(data, colWidths=[3.5*inch, 1*inch, 1*inch, 1.5*inch])
    item_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), hc_dark), ('TEXTCOLOR', (0,0), (-1,0), white),
        ('ALIGN', (1,1), (-1,-1), 'CENTER'), ('ALIGN', (3,1), (3,-1), 'RIGHT'),
        ('GRID', (0,0), (-1,-1), 1, black), 
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 10), ('TOPPADDING', (0,0), (-1,0), 10),
    ]))
    table_width, table_height = item_table.wrapOn(p, width - 2*inch, height)
    item_table.drawOn(p, 1*inch, table_y_start - table_height)

    # Comments Table
    comments_y_start = table_y_start - table_height - 0.2*inch
    comments_data = [
        [Paragraph('<b>OTHER COMMENTS</b>', styles['Normal'])],
        [Paragraph(invoice.other_comments or '', styles['Normal']), f"TZS {intcomma(int(invoice.get_total()))}"],
        [f"<b>Terms of payment:</b> {invoice.terms_of_payment or ''}", '']
    ]
    comments_table = Table(comments_data, colWidths=[5*inch, 2.5*inch])
    comments_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), hc_dark), ('TEXTCOLOR', (0,0), (0,0), white),
        ('GRID', (0,0), (-1,-1), 1, black), ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ALIGN', (1,1), (1,1), 'RIGHT'), ('SPAN', (0,1), (0,2)),
    ]))
    comments_width, comments_height = comments_table.wrapOn(p, width, height)
    comments_table.drawOn(p, 1*inch, comments_y_start - comments_height)
    
    # --- 4. Final Total ---
    final_total_y = comments_y_start - comments_height - 0.5*inch
    p.setFont("Helvetica-Bold", 11)
    p.drawRightString(6.5*inch, final_total_y, "TOTAL AMOUNT")
    total_amount_str = f"TZS {intcomma(int(invoice.get_total()))}"
    p.drawRightString(7.5*inch, final_total_y, total_amount_str)
    p.setLineWidth(2)
    p.line(7.5*inch - p.stringWidth(total_amount_str) - 5, final_total_y-2, 7.5*inch, final_total_y-2)
    p.line(7.5*inch - p.stringWidth(total_amount_str) - 5, final_total_y-1, 7.5*inch, final_total_y-1)

    # --- 5. Footer ---
    p.setFont("Helvetica", 9)
    p.drawCentredString(width/2, 1*inch, "If you have any question about this invoice, please contact")
    p.drawCentredString(width/2, 0.8*inch, f"{company_info.phone or ''} | {company_info.name or ''}")
    
    p.save()
    buffer.seek(0)
    return buffer

def generate_welcome_package_pdf(employee, invoice, company_info):
    """
    Generates a single, multi-part A4 PDF containing a full invoice
    and the employee's ID card (front and back).
    """
    buffer = io.BytesIO()
    # Create an A4 canvas
    p = canvas.Canvas(buffer, pagesize='A4')
    width, height = letter # Use letter dimensions for inch calculations

    # --- 1. Draw the full invoice on the top part of the page ---
    # We pass the canvas 'p' to our existing invoice drawing function
    draw_full_invoice(p, invoice, company_info)

    # --- 2. Draw the ID Card Front and Back at the bottom ---
    # We pass the canvas 'p' to a new helper function
    draw_id_cards_on_page(p, employee, company_info)

    # Finalize the single page and save the PDF
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer


def draw_id_cards_on_page(p, employee, company_info):
    """
    Helper function to draw both the front and back of the ID card
    at the bottom of an existing canvas.
    """
    # Define Card Dimensions in inches for easy placement
    CARD_WIDTH_IN = 3.375 * inch
    CARD_HEIGHT_IN = 2.125 * inch
    
    # --- Draw Front of Card on the left side ---
    front_x = 0.5 * inch
    front_y = 0.5 * inch # Place 0.5 inches from the bottom
    # We will need to create a specific `draw_card_front_pdf` helper for this
    # For now, let's just draw a placeholder
    p.rect(front_x, front_y, CARD_WIDTH_IN, CARD_HEIGHT_IN, stroke=1, fill=0)
    p.drawCentredString(front_x + CARD_WIDTH_IN/2, front_y + CARD_HEIGHT_IN/2, "ID Card Front")
    
    # --- Draw Back of Card on the right side ---
    back_x = front_x + CARD_WIDTH_IN + 0.25*inch
    back_y = 0.5 * inch
    p.rect(back_x, back_y, CARD_WIDTH_IN, CARD_HEIGHT_IN, stroke=1, fill=0)
    p.drawCentredString(back_x + CARD_WIDTH_IN/2, back_y + CARD_HEIGHT_IN/2, "ID Card Back")