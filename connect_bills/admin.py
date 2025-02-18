from django.contrib import admin
from django.http import HttpResponse
from django.utils.timezone import make_aware
from datetime import datetime
import reportlab.lib.pagesizes as ps
from reportlab.pdfgen import canvas
from .models import WhatsAppBill


class WhatsAppBillAdmin(admin.ModelAdmin):
    list_display = ('type', 'sent_to', 'send_on', 'wa_response')
    search_fields = ('type', 'sent_to')
    list_filter = ('send_on',)
    actions = ['export_as_pdf']

    def export_as_pdf(self, request, queryset):
        """
        Export the selected WhatsAppBill records as a PDF.
        """
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="whatsapp_bills.pdf"'

        # Create PDF
        pdf = canvas.Canvas(response, pagesize=ps.A4)
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(200, 800, "WhatsApp Bills Report")

        pdf.setFont("Helvetica", 12)
        y_position = 780  # Start position

        for bill in queryset:
            if y_position < 100:  # Prevents overflow
                pdf.showPage()
                pdf.setFont("Helvetica", 12)
                y_position = 800

            pdf.drawString(50, y_position, f"Type: {bill.type}")
            pdf.drawString(250, y_position, f"Sent To: {bill.sent_to}")
            pdf.drawString(450, y_position, f"Date: {bill.send_on.strftime('%Y-%m-%d %H:%M:%S')}")
            y_position -= 20

        pdf.save()
        return response

    export_as_pdf.short_description = "Download selected as PDF"


admin.site.register(WhatsAppBill, WhatsAppBillAdmin)
