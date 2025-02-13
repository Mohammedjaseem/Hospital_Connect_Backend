from django.db import models
from django.utils.translation import gettext_lazy as _



class Hostel(models.Model):
    name = models.CharField(max_length=100)
    incharge = models.ForeignKey("staff.StaffProfile", verbose_name=_("Incharge"),related_name="hostel_incharge", on_delete=models.CASCADE, null=True)
    wardens = models.ManyToManyField("staff.StaffProfile", verbose_name=_("Wardens"), related_name="hostels", blank=True)
    capacity = models.IntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)
    remarks = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = 'Hostel'
        verbose_name_plural = 'Hostels'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['incharge']),
            models.Index(fields=['created_on']),
            models.Index(fields=['updated_on']),
        ]
