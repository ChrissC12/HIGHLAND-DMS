# generator/context_processors.py

from .models import CompanyInfo

def company_info_processor(request):
    """
    Makes the single CompanyInfo object available in the context of every template.
    This allows the navbar to display the company logo and name on every page.
    """
    # We use .first() to get the single company info object.
    # This is more efficient than .get() and won't crash if the table is empty.
    company = CompanyInfo.objects.first()
    return {'company_info': company}