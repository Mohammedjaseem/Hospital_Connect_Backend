from django.db import models
from django.utils import timezone

# Create your models here.

class WhatsAppBill(models.Model):
    # Fields
    type = models.CharField(max_length=100)
    sent_to = models.CharField(max_length=100)
    send_on = models.DateTimeField(auto_now_add=True)
    wa_response = models.TextField((""), null=True, blank=True)

    # String representation of the model
    def __str__(self):
        # Provides a more readable string representation
        return f"{self.type}"

    # Meta class to define model-level properties
    class Meta:
        verbose_name = 'WhatsApp Bill'
        verbose_name_plural = 'WhatsApp Bills'
        

class EmailLog(models.Model):
    sent_by = models.CharField(max_length=255, null=True)
    subject = models.CharField(max_length=255)
    recipient = models.EmailField()
    cc_emails = models.TextField(blank=True, null=True)
    sent_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=200, default='Pending')
    task_id = models.CharField(max_length=250, default='Main Thread')
    error_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Email to {self.recipient} - {self.sent_at}"