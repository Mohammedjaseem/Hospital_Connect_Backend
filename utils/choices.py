from django.db import models

class AcademicYearChoices(models.IntegerChoices):
    YEAR_2024_2025 = 1, "2024-2025"
    YEAR_2025_2026 = 2, "2025-2026"
    YEAR_2026_2027 = 3, "2026-2027"
    YEAR_2027_2028 = 4, "2027-2028"

class DivisionChoices(models.IntegerChoices):
    A = 1, "A"
    B = 2, "B"
    C = 3, "C"
    D = 4, "D"
    E = 5, "E"
    F = 6, "F"
    G = 7, "G"
    H = 8, "H"
    I = 9, "I"
    J = 10, "J"
    K = 11, "K"
    L = 12, "L"

class SectionChoices(models.IntegerChoices):
    KG = 1, "KG"
    LP = 2, "LP"
    UP = 3, "UP"
    HS = 4, "HS"
    HSS = 5, "HSS"

class ClassChoices(models.IntegerChoices):
    CLASS_1 = 1, "1"
    CLASS_2 = 2, "2"
    CLASS_3 = 3, "3"
    CLASS_4 = 4, "4"
    CLASS_5 = 5, "5"
    CLASS_6 = 6, "6"
    CLASS_7 = 7, "7"
    CLASS_8 = 8, "8"
    CLASS_9 = 9, "9"
    CLASS_10 = 10, "10"
    CLASS_PLUS1 = 11, "+1"
    CLASS_PLUS2 = 12, "+2"

class DepartmentChoices(models.IntegerChoices):
    SCIENCE = 1, "Science"
    COMMERCE = 2, "Commerce"
    HUMANITIES = 3, "Humanities"

class BloodGroupChoices(models.IntegerChoices):
    A_POS = 1, "A+"
    A_NEG = 2, "A-"
    B_POS = 3, "B+"
    B_NEG = 4, "B-"
    AB_POS = 5, "AB+"
    AB_NEG = 6, "AB-"
    O_POS = 7, "O+"
    O_NEG = 8, "O-"

class GenderChoices(models.IntegerChoices):
    MALE = 1, "Male"
    FEMALE = 2, "Female"
    OTHER = 3, "Other"

class PaymentTypeChoices(models.IntegerChoices):
    ONLINE = 1, "Online"
    OFFLINE = 2, "Offline"
    CASH = 3, "Cash"
    CHEQUE = 4, "Cheque"
    RTGS = 5, "RTGS"
    DD = 6, "DD"
    BANK_TRANSFER = 7, "Bank Transfer"
    NEFT = 8, "NEFT"
    UPI = 9, "UPI"
    IMPS = 10, "IMPS"
    CARD = 11, "Card"
    POS = 12, "POS"

# Helper function to get human-readable values from integer choices
def get_choice_label(choices, value):
    """Returns the label for a given integer choice."""
    return dict(choices.choices).get(value, "Unknown")

# Example Usage:
# print(get_choice_label(BloodGroupChoices, 1))  # Output: "A+"