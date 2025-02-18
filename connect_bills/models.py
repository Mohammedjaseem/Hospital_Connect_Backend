from django.db import models

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