import uuid
from django.db import models
from utils.choices import AcademicYearChoices,SectionChoices,DivisionChoices,ClassChoices,DepartmentChoices

class Departments(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    name = models.CharField(max_length=300, unique=True, db_index=True)  # Unique for clear identification
    short_code = models.CharField(max_length=10, unique=True, db_index=True)  # Ensure unique short codes
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    hod = models.ForeignKey(
        "staff.StaffProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hod_departments",
    )
    incharge = models.ForeignKey(
        "staff.StaffProfile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="incharge_departments",
    )

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["short_code"]),
        ]

    def __str__(self):
        return f"{self.short_code} - {self.name}"


class Designations(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    department = models.ForeignKey("administration.Departments", on_delete=models.CASCADE, related_name="designations",null=True)
    name = models.CharField(max_length=100, db_index=True)  # Renamed for better clarity
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Designation"
        verbose_name_plural = "Designations"
        indexes = [
            models.Index(fields=["department"]),
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name


class DepartmentInchargeAndHod(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    department = models.ForeignKey(
        "administration.Departments", on_delete=models.CASCADE, related_name="incharge_and_hod_records"
    )
    hod = models.ForeignKey("staff.StaffProfile", on_delete=models.CASCADE, related_name="hod_records", null=True)
    incharge = models.ForeignKey("staff.StaffProfile", on_delete=models.CASCADE, related_name="incharge_records", null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Department Incharge and HOD"
        verbose_name_plural = "Department Incharge and HODs"
        indexes = [
            models.Index(fields=["department"]),
        ]

    def __str__(self):
        hod_name = self.hod.name if self.hod else "N/A"
        incharge_name = self.incharge.name if self.incharge else "N/A"
        return f"{self.department.name} - HOD: {hod_name}, Incharge: {incharge_name}"
    


# # class ClassRoom(models.Model):
# #     uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
# #     name = models.CharField(max_length=50, unique=True, db_index=True)
# #     academic_year = models.CharField(
# #         max_length=9, 
# #         choices=AcademicYearChoices.CHOICES, 
# #     )
# #     section = models.CharField(
# #         max_length=10, 
# #         choices=SectionChoices.CHOICES, 
# #     )
# #     division = models.CharField(
# #         max_length=10, 
# #         choices=DivisionChoices.CHOICES, 
# #         null=True, 
# #         blank=True
# #     )

# #     department = models.CharField(
# #         max_length=20, 
# #         choices=DepartmentChoices.CHOICES, 
# #         null=True, 
# #         blank=True
# #     )

# #     classs = models.CharField(max_length=10,choices=ClassChoices.CHOICES) 
# #     class_teacher = models.ForeignKey("staff.StaffProfile", on_delete=models.SET_NULL, null=True)
# #     # time_table = models.ForeignKey("administration.TimeTable", on_delete=models.SET_NULL, null=True)
# #     description = models.TextField(blank=True, null=True)
# #     created_at = models.DateTimeField(auto_now_add=True)
# #     updated_at = models.DateTimeField(auto_now=True)

# #     def __str__(self):
# #         return self.name
# #     def save(self, *args, **kwargs):
# #         # Automatically generate the name if it is not set
# #         self.name = f"{self.classs} {self.department or ''} {self.division or ''} {self.academic_year}".strip()
# #         super().save(*args, **kwargs)

# #     class Meta:
# #         verbose_name = "Class Room"
# #         verbose_name_plural = "Class Rooms"







# # class AcademicYear(models.Model):
# #     start_year = models.PositiveIntegerField()
# #     end_year = models.PositiveIntegerField()
# #     name = models.CharField(max_length=20, blank=True, null=True, unique=True, db_index=True)
# #     # start_date = models.DateField()
# #     # end_date = models.DateField()
# #     description = models.TextField(blank=True, null=True)
# #     created_at = models.DateTimeField(auto_now_add=True)
# #     updated_at = models.DateTimeField(auto_now=True)

# #     def __str__(self):
# #         return self.name

# #     def clean(self):
# #         if self.end_year != self.start_year + 1:
# #             raise ValidationError("End year must be exactly one year after the start year.")
# #         # if self.start_date >= self.end_date:
# #         #     raise ValidationError("Start date must be earlier than the end date.")

# #     def save(self, *args, **kwargs):
# #         if not self.name:
# #             self.name = f"{self.start_year}-{self.end_year}"
# #         super().save(*args, **kwargs)

# #     class Meta:
# #         ordering = ["start_year"]
# #         verbose_name_plural = "Academic Years"
# #         indexes = [models.Index(fields=["name"])]
# #         constraints = [
# #             models.CheckConstraint(check=models.Q(end_year=models.F("start_year") + 1), name="end_year_greater_by_one"),
# #             # models.CheckConstraint(check=models.Q(start_date__lt=models.F("end_date")), name="start_date_before_end_date"),
# #         ]


# # class Section(models.Model):
# #     name = models.CharField(max_length=50, unique=True, db_index=True)
# #     description = models.TextField(blank=True, null=True)
# #     created_at = models.DateTimeField(auto_now_add=True)
# #     updated_at = models.DateTimeField(auto_now=True)

# #     def __str__(self):
# #         return self.name

# #     class Meta:
# #         ordering = ["name"]
# #         verbose_name_plural = "Sections"
# #         indexes = [models.Index(fields=["name"])]


# # class Division(models.Model):
# #     name = models.CharField(max_length=50, unique=True, db_index=True)
# #     description = models.TextField(blank=True, null=True)
# #     created_at = models.DateTimeField(auto_now_add=True)
# #     updated_at = models.DateTimeField(auto_now=True)

# #     def __str__(self):
# #         return self.name

# #     class Meta:
# #         ordering = ["name"]
# #         verbose_name_plural = "Divisions"
# #         indexes = [models.Index(fields=["name"])]





# # from django.db import models
# # from django_tenants.models import TenantMixin  # Assuming you're using django-tenants

# # class Tenant(models.Model):  # Example Tenant model for multi-tenancy
# #     name = models.CharField(max_length=255)
# #     created_at = models.DateTimeField(auto_now_add=True)

# # class Student(models.Model):
# #     name = models.CharField(max_length=100)
# #     class_name = models.CharField(max_length=50)
# #     section = models.CharField(max_length=10, blank=True, null=True)
# #     roll_number = models.IntegerField()
# #     academic_year = models.CharField(max_length=10)
# #     tenant_id = models.ForeignKey(Tenant, on_delete=models.CASCADE)

# #     def __str__(self):
# #         return f"{self.name} ({self.roll_number})"

# # class FeeStructure(models.Model):
# #     class_name = models.CharField(max_length=50)
# #     academic_year = models.CharField(max_length=10)
# #     total_fee = models.DecimalField(max_digits=10, decimal_places=2)
# #     tenant_id = models.ForeignKey(Tenant, on_delete=models.CASCADE)

# #     def __str__(self):
# #         return f"{self.class_name} - {self.academic_year}"

# # class StudentFee(models.Model):
# #     student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="fees")
# #     fee_structure = models.ForeignKey(FeeStructure, on_delete=models.SET_NULL, null=True)
# #     academic_year = models.CharField(max_length=10)
# #     total_fee = models.DecimalField(max_digits=10, decimal_places=2)
# #     outstanding_fee = models.DecimalField(max_digits=10, decimal_places=2)
# #     num_installments = models.IntegerField()
# #     tenant_id = models.ForeignKey(Tenant, on_delete=models.CASCADE)

# #     def __str__(self):
# #         return f"{self.student.name} - {self.academic_year}"

# # class InstallmentPlan(models.Model):
# #     student_fee = models.ForeignKey(StudentFee, on_delete=models.CASCADE, related_name="installments")
# #     installment_number = models.IntegerField()
# #     due_date = models.DateField()
# #     installment_amount = models.DecimalField(max_digits=10, decimal_places=2)
# #     is_paid = models.BooleanField(default=False)
# #     paid_date = models.DateField(null=True, blank=True)
# #     tenant_id = models.ForeignKey(Tenant, on_delete=models.CASCADE)

# #     def __str__(self):
# #         return f"Installment {self.installment_number} for {self.student_fee.student.name}"








