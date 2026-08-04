import string
import random
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _, gettext as _t

class District(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return _t(self.name)

class PradeshiyaSabha(models.Model):
    name = models.CharField(max_length=150)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='sabhas')

    class Meta:
        unique_together = ('name', 'district')
        verbose_name = "Pradeshiya Sabha"
        verbose_name_plural = "Pradeshiya Sabhas"

    def __str__(self):
        return f"{self.name} ({self.district.name})"

class Wasama(models.Model):
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=50, blank=True, help_text="Grama Niladhari Division Code, e.g. GN 600")
    pradeshiya_sabha = models.ForeignKey(PradeshiyaSabha, on_delete=models.CASCADE, related_name='wasamas')

    class Meta:
        unique_together = ('name', 'pradeshiya_sabha')
        verbose_name = "Wasama"
        verbose_name_plural = "Wasamas"

    def __str__(self):
        code_str = f" - {self.code}" if self.code else ""
        return f"{self.name}{code_str} ({self.pradeshiya_sabha.name})"

class OfficerProfile(models.Model):
    ROLE_CHOICES = (
        ('OFFICER', 'Officer'),
        ('ADMIN', 'Administrator'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='OFFICER')
    assigned_district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True, related_name='officers')
    assigned_pradeshiya_sabha = models.ForeignKey(PradeshiyaSabha, on_delete=models.SET_NULL, null=True, blank=True, related_name='officers')
    assigned_wasama = models.ForeignKey(Wasama, on_delete=models.SET_NULL, null=True, blank=True, related_name='officers')

    def __str__(self):
        role_label = self.get_role_display()
        return f"{self.user.username} ({role_label})"

class Complaint(models.Model):
    CATEGORY_CHOICES = (
        ('WATER_SUPPLY', _('Water Supply Issues')),
        ('IRRIGATION', _('Irrigation Issues')),
        ('ROAD_BRIDGE_DAMAGE', _('Road & Bridge Damage')),
        ('WASTE_MGMT', _('Waste Management Issues')),
        ('ELECTRICITY_SUPPLY', _('Electricity Supply Issues')),
        ('DRAINAGE_FLOOD', _('Drainage & Flood Issues')),
        ('LAND_ISSUES', _('Land Issues')),
        ('HOUSING_ISSUES', _('Housing Issues')),
        ('HEALTHCARE_SHORTAGE', _('Healthcare Shortages')),
        ('EDUCATION_FACILITIES', _('School & Educational Facility Shortages')),
        ('TRANSPORT_ISSUES', _('Transport Issues')),
        ('EMPLOYMENT_ISSUES', _('Employment Shortages')),
        ('AGRICULTURE_ISSUES', _('Agricultural Issues')),
        ('WILDLIFE_CONFLICT', _('Human-Wildlife Conflict (Elephants, Monkeys, etc.)')),
        ('ENVIRONMENT_POLLUTION', _('Environmental Pollution')),
        ('ILLEGAL_MINING_LOGGING', _('Illegal Sand, Stone & Timber Mining')),
        ('NARCOTICS_CRIME', _('Narcotics & Crime')),
        ('NOISE_POLLUTION', _('Noise Pollution')),
        ('STREET_LIGHTING', _('Faulty Street Lighting')),
        ('PUBLIC_SAFETY', _('Public Safety Issues')),
        ('MARKET_COST_LIVING', _('Market & Cost of Living Issues')),
        ('CORRUPTION_IRREGULARITIES', _('Irregularities & Corruption')),
        ('PUBLIC_LAND_ENCROACHMENT', _('Encroachment of Public Lands')),
        ('STRAY_ANIMALS', _('Animal Waste & Stray Animals Issues')),
        ('TELECOM_INTERNET', _('Internet & Telecom Service Issues')),
        ('OTHER', _('Other')),
    )

    STATUS_CHOICES = (
        ('PENDING', _('Pending')),
        ('IN_PROGRESS', _('In Progress')),
        ('RESOLVED', _('Resolved')),
        ('REJECTED', _('Rejected')),
    )

    reference_number = models.CharField(max_length=50, unique=True, editable=False)
    citizen_name = models.CharField(max_length=150)
    citizen_email = models.EmailField()
    citizen_phone = models.CharField(max_length=15)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='OTHER')
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    district = models.ForeignKey(District, on_delete=models.PROTECT, related_name='complaints')
    pradeshiya_sabha = models.ForeignKey(PradeshiyaSabha, on_delete=models.PROTECT, related_name='complaints')
    wasama = models.ForeignKey(Wasama, on_delete=models.PROTECT, related_name='complaints')
    
    evidence_file = models.FileField(upload_to='complaint_evidence/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reference_number} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.reference_number:
            year = timezone.now().strftime("%Y")
            chars = string.ascii_uppercase + string.digits
            while True:
                ref = f"CCMS-{year}-{''.join(random.choices(chars, k=5))}"
                if not Complaint.objects.filter(reference_number=ref).exists():
                    self.reference_number = ref
                    break
        super().save(*args, **kwargs)

class ComplaintRemark(models.Model):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='remarks')
    officer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='remarks')
    remark = models.TextField()
    status_from = models.CharField(max_length=20)
    status_to = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Remark on {self.complaint.reference_number} by {self.officer.username if self.officer else 'System'}"
