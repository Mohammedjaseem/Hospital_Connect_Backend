import uuid
from django.db import models
from django.utils.timezone import now
from django.utils.safestring import mark_safe
from datetime import date
from utils.multis3 import TenantMediaStorage
from utils.image_compressor import ImageCompressorMixin
from utils.choices import GenderChoices, BloodGroupChoices



class StaffProfile(models.Model, ImageCompressorMixin):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_active = models.BooleanField(default=True)
    user = models.OneToOneField(
        "custom_users.CustomUser",
        on_delete=models.CASCADE,
        related_name="staff_profile",
    )
    emp_id = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=250)
    gender = models.CharField(
        max_length=10, choices=GenderChoices.CHOICES, blank=True, null=True
    )
    dob = models.DateField(blank=True, null=True)
    mobile = models.CharField(max_length=15, unique=True)
    department = models.ForeignKey(
        "administration.Departments", on_delete=models.SET_NULL, null=True, blank=True
    )
    designation = models.ForeignKey(
        "administration.Designations", on_delete=models.SET_NULL, null=True, blank=True
    )
    is_verified = models.BooleanField(default=False)
    is_hosteller = models.BooleanField(default=False)
    hostel = models.ForeignKey(
        "hostel.Hostel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="hostel_staff",  # Explicit related_name to avoid clash
    )
    room_no = models.CharField(max_length=10, blank=True, null=True)

    # Store images in tenant-specific S3 folders
    picture = models.ImageField(
        storage=TenantMediaStorage(), upload_to="users/picture", blank=True, null=True
    )

    address = models.TextField(blank=True, null=True)
    blood_group = models.CharField(
        max_length=3, choices=BloodGroupChoices.CHOICES, blank=True, null=True
    )
    emergency_contact = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_default_picture_url(self):
        return "https://cdn.vectorstock.com/i/preview-1x/82/99/no-image-available-like-missing-picture-vector-43938299.jpg"

    def profile_pic(self):
        img_url = self.picture.url if self.picture else self.get_default_picture_url()
        return mark_safe(
            f'<img src="{img_url}" width="80" height="80" style="border-radius: 15px;" />'
        )

    def calculate_age(self):
        if self.dob:
            today = date.today()
            return (
                today.year
                - self.dob.year
                - ((today.month, today.day) < (self.dob.month, self.dob.day))
            )
        return None

    def save(self, *args, **kwargs):
        if self.picture:
            self.compress_image()  # Apply compression if necessary
        super().save(*args, **kwargs)

    @property
    def age(self):
        return self.calculate_age()
    







# import uuid
# from django.db import models
# from django.utils.timezone import now
# from django.db.models import Sum

# class ReviewType(models.Model):
#     """Defines the type of review (Teaching, Non-Teaching, Clinical)"""
#     CATEGORY_CHOICES = [
#         ("non_teaching", "Non-Teaching Staff Review"),
#         ("teaching", "Teaching Staff Review"),
#         ("clinical", "Clinical Staff Review"),
#     ]
#     name = models.CharField(max_length=100, unique=True, db_index=True)
#     category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, db_index=True)

#     def __str__(self):
#         return self.name

# class ReviewerRole(models.Model):
#     """Defines roles of reviewers (HOD, AM, HR)"""
#     name = models.CharField(max_length=100, unique=True, db_index=True)  # e.g., HOD, AM, HR

#     def __str__(self):
#         return self.name

# class GlobalReviewChoice(models.Model):
#     """Predefined choices that apply to all questions"""
#     choice_text = models.CharField(max_length=255)
#     score = models.PositiveIntegerField(db_index=True)

#     def __str__(self):
#         return f"{self.choice_text} ({self.score})"

# class ReviewQuestion(models.Model):
#     """Standardized questions applicable to all reviews"""
#     question_text = models.TextField()
    
#     def __str__(self):
#         return self.question_text

# class ReviewQuestionChoice(models.Model):
#     """Through model for Question & Choices to optimize ManyToMany"""
#     question = models.ForeignKey(ReviewQuestion, on_delete=models.CASCADE, related_name="question_choices")
#     choice = models.ForeignKey(GlobalReviewChoice, on_delete=models.CASCADE, related_name="choice_questions")

#     class Meta:
#         unique_together = ("question", "choice")

# class StaffReview(models.Model):
#     """Each staff member receives three reviews (one per reviewer)"""
#     uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
#     staff = models.ForeignKey("staff.StaffProfile", on_delete=models.CASCADE, related_name="reviews", db_index=True)
#     review_type = models.ForeignKey(ReviewType, on_delete=models.CASCADE, related_name="reviews", db_index=True)
#     created_at = models.DateTimeField(default=now)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"Review for {self.staff.name} ({self.review_type.name})"

#     def total_review_score(self):
#         """Optimized total review score using aggregation"""
#         return self.individual_reviews.aggregate(total_score=Sum("answers__choice__score"))["total_score"] or 0

# class IndividualReview(models.Model):
#     """Each reviewer (HOD, AM, HR) gives their own review for a staff"""
#     staff_review = models.ForeignKey(StaffReview, on_delete=models.CASCADE, related_name="individual_reviews", db_index=True)
#     reviewer = models.ForeignKey("staff.StaffProfile", on_delete=models.CASCADE, related_name="given_reviews", db_index=True)
#     reviewer_role = models.ForeignKey(ReviewerRole, on_delete=models.CASCADE, db_index=True)
#     created_at = models.DateTimeField(default=now, db_index=True)

#     def __str__(self):
#         return f"{self.reviewer.name} ({self.reviewer_role.name}) - {self.staff_review.staff.name}"

#     def total_score(self):
#         """Optimized total score calculation using aggregation"""
#         return self.answers.aggregate(total_score=Sum("choice__score"))["total_score"] or 0

# class ReviewAnswer(models.Model):
#     """Each review consists of multiple question-answer pairs"""
#     individual_review = models.ForeignKey(IndividualReview, on_delete=models.CASCADE, related_name="answers", db_index=True)
#     question = models.ForeignKey(ReviewQuestion, on_delete=models.CASCADE, db_index=True)
#     choice = models.ForeignKey(GlobalReviewChoice, on_delete=models.CASCADE, db_index=True)

#     def __str__(self):
#         return f"{self.individual_review.reviewer.name} - {self.question.question_text}: {self.choice.choice_text} ({self.choice.score})"

#     class Meta:
#         unique_together = ("individual_review", "question")

# # Get total review score for a staff member
# staff_review = StaffReview.objects.prefetch_related("individual_reviews__answers__choice").get(id=some_id)
# total_score = staff_review.total_review_score()

# # Get individual review score (e.g., HOD's review)
# individual_review = IndividualReview.objects.prefetch_related("answers__choice").get(id=some_id)
# hod_score = individual_review.total_score()
