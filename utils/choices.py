class AcademicYearChoices:
    CHOICES = [
        ("2024-2025", "2024-2025"),
        ("2025-2026", "2025-2026"),
        ("2026-2027", "2026-2027"),
        ("2027-2028", "2027-2028"),
    ]


class DivisionChoices:
    CHOICES = [
        ("A", "A"),
        ("B", "B"),
        ("C", "C"),
        ("D", "D"),
        ("E", "E"),
        ("F", "F"),
        ("G", "G"),
        ("H", "H"),
        ("I", "I"),
        ("J", "J"),
        ("K", "K"),
        ("L", "L"),
    ]


class SectionChoices:
    CHOICES = [
        ("KG", "KG"),
        ("LP", "LP"),
        ("UP", "UP"),
        ("HS", "HS"),
        ("HSS", "HSS"),
    ]

class ClassChoices:
    CHOICES = [
        ("1", "1"),
        ("2", "2"),
        ("3", "3"),
        ("4", "4"),
        ("5", "5"),
        ("6", "6"),
        ("7", "7"),
        ("8", "8"),
        ("9", "9"),
        ("10", "10"),
        ("+1", "+1"),
        ("+2", "+2"),
    ]

class DepartmentChoices:
    CHOICES = [
        ("Science", "Science"),
        ("Commerce", "Commerce"),
        ("Humanities", "Humanities"),
    ]


class BloodGroupChoices:
    CHOICES = [
        ("A+", "A+"),
        ("A-", "A-"),
        ("B+", "B+"),
        ("B-", "B-"),
        ("AB+", "AB+"),
        ("AB-", "AB-"),
        ("O+", "O+"),
        ("O-", "O-"),
    ]

class GenderChoices:
    CHOICES = [
        ("Male", "Male"),
        ("Female", "Female"),
        ("Other", "Other"),
    ]


class SubjectChoices:
    CHOICES = [
        ("English", "English"),
        ("Maths", "Mathematics"),
        ("Basic Science", "Basic Science"),
        ("Social Studies", "Social Studies"),
        ("Hindi", "Hindi"),
        ("Malayalam", "Malayalam"),
        ("Arabic", "Arabic"),
        ("Physics", "Physics"),
        ("Chemistry", "Chemistry"),
        ("Biology", "Biology"),
        ("Geography", "Geography"),
        ("History", "History"),
        ("IT", "Information Technology"),
        ("Business Studies", "Business Studies"),
        ("First Language Paper 1", "First Language Paper 1"),
        ("First Language Paper 2", "First Language Paper 2"),
        ("EVS", "Environmental Studies"),
        ("GK", "General Knowledge"),
        ("PT", "Physical Training"),

        #Modern Subjects
        ("MS", "Modern Studies"),
        ("Library", "Library"),
        ("NMMS", "NMMS"),
        ("WORKNEXPERIENCE", "Work Experience"),
    ]

class PaymentTypeChoices:
    CHOICES = [
        ("Online", "Online"),
        ("Offline", "Offline"),
        ("Cash", "Cash"),
        ("Cheque", "Cheque"),
        ("RTGS", "RTGS"),
        ("DD", "DD"),
        ("Bank Transfer", "Bank Transfer"),
        ("NEFT", "NEFT"),
        ("UPI", "UPI"),
        ("IMPS", "IMPS"),
        ("Card","Card"),
        ("POS","POS"),
    ]


