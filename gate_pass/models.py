from django.db import models
from django.utils.safestring import mark_safe
from utils.multis3 import TenantMediaStorage
from django.utils.html import format_html 
from django.utils.translation import gettext as _
# Create your models here.

class HostelStaffGatePass(models.Model):
    
    class Meta:
        verbose_name = 'Hostel Staff Gatepass'
        verbose_name_plural = 'Hostel Staff Gatepass'
        
    #staff    
    staff = models.ForeignKey("staff.StaffProfile", verbose_name=_("Staff"), related_name="staff_gatepasses", on_delete=models.CASCADE)
    
    #requested on & purpose 
    requested_on  = models.DateTimeField(auto_now_add=True)
    purpose = models.CharField(max_length=3000, default="Purpose not mentioned")
    
    #Time requested for gatepasss 
    requesting_date = models.DateField(null=True, blank=True)
    requesting_time = models.TimeField(null=True, blank=True)
    
    #return timing
    return_date = models.DateField(null=True, verbose_name = "Returning Date")
    return_time = models.TimeField(null=True, blank=True)
        

    #unique code & status
    pass_token = models.CharField(max_length=1560, unique=True)
    request_status = models.CharField(max_length=200, default="Requested")
    
    # for mentors approval
    mentor = models.ForeignKey("staff.StaffProfile", verbose_name=_("mentor_warden"), related_name="gatepass_mentor", on_delete=models.CASCADE, null=True, blank=True)
    mentor_updated = models.BooleanField(null=True, blank=True)
    updated_on = models.DateTimeField(blank=True, null=True, verbose_name="Mentor Update On")
    qr_code = models.ImageField(TenantMediaStorage(), upload_to='GatePass/qrCodes/%Y/%m/%d/', blank=True, null=True)
    qr_code_url = models.CharField(max_length=1560, blank=True, null=True)
    
    #mentor remarks on rejected !
    remarks = models.TextField(null=True, blank=True, default="No remarks added !")
    
    # informed warden
    informed_warden = models.BooleanField(default=False)

    # Pass details  
    gatepass_no  =  models.CharField(max_length=50, blank=True, null=True) 
    checked_out = models.BooleanField(default=False)
    date_time_exit = models.DateTimeField(blank=True, null=True , verbose_name = "Check Out")
    checked_in = models.BooleanField(default=False)
    date_time_entry = models.DateTimeField(blank=True, null=True , verbose_name = "Check In")
    duration = models.DurationField(blank=True, null=True)
    
    
    def __str__(self):
        return str(self.staff.name)

    
    @property
    def requested_check_out(self):
        # Convert the date to string in the specified format
        requesting_date_str = self.requesting_date.strftime('%b. %d, %Y') if self.requesting_date else ''
        # Convert the time to the specified 12-hour format with AM/PM
        requesting_time_str = self.requesting_time.strftime('%I:%M %p').lower() if self.requesting_time else ''
        return requesting_date_str + ", " + requesting_time_str if requesting_date_str and requesting_time_str else ''

    @property
    def proposed_check_in(self):
        # Convert the date to string in the specified format
        return_date_str = self.return_date.strftime('%b. %d, %Y') if self.return_date else ''
        # Convert the time to the specified 12-hour format with AM/PM
        return_time_str = self.return_time.strftime('%I:%M %p').lower() if self.return_time else ''
        return return_date_str + ", " + return_time_str if return_date_str and return_time_str else ''

        
    @property
    def status_update(self):
        status_color_map = {
            "Rejected": {"bg_color": "#000000", "text_color": "#FFFFFF"},  # Black for rejected
            "Approved": {"bg_color": "#4CAF50", "text_color": "#FFFFFF"},  # Green for approved
            "Requested": {"bg_color": "#2196f3", "text_color": "#00000"},  # Yellow for requested
        }

        default_color = {"bg_color": "#9E9E9E", "text_color": "#FFFFFF"}  # Grey for unrecognized statuses

        # Get colors for the current request status, or default if not found
        colors = status_color_map.get(self.request_status, default_color)

        return format_html(
            '<h6 style="background-color: {}; color: {}; padding: 10px 10px; margin-top:3px; text-decoration: none; border-radius: 7px; text-align:center;"><i>{}</i></h6>',
            colors["bg_color"],
            colors["text_color"],
            self.request_status or "Status Unknown"
        )
        
    @property  
    def profile_pic(self):
        return mark_safe('<img src="%s" width="80" height="80" style="border-radius: 15px;" />' % (self.staff.picture.url))