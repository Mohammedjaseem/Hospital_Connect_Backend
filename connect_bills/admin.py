from django.contrib import admin
from django.http import HttpResponse
from django.utils.timezone import make_aware
from datetime import datetime
import reportlab.lib.pagesizes as ps
from reportlab.pdfgen import canvas
from .models import WhatsAppBill, EmailLog


class WhatsAppBillAdmin(admin.ModelAdmin):
    list_display = ('type', 'sent_to', 'send_on', 'wa_response')
    search_fields = ('type', 'sent_to')
    list_filter = ('send_on',)

admin.site.register(WhatsAppBill, WhatsAppBillAdmin)

class EmailLogAdmin(admin.ModelAdmin):
    list_display = ("recipient", "subject", "sent_by", "sent_at", "status", "task_id")
    list_filter = ("status", "sent_at")
    search_fields = ("recipient", "subject", "sent_by", "task_id")
    readonly_fields = ("sent_at", "error_message")
    
    fieldsets = (
        ("Email Details", {"fields": ("sent_by", "recipient", "cc_emails", "subject", "status")}),
        ("Meta Info", {"fields": ("sent_at", "task_id", "error_message"), "classes": ("collapse",)}),
    )

admin.site.register(EmailLog, EmailLogAdmin)


