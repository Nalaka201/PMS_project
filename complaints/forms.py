from django import forms
from .models import Complaint, ComplaintRemark, District, PradeshiyaSabha, Wasama

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = [
            'citizen_name', 'citizen_email', 'citizen_phone', 
            'category', 'title', 'description', 
            'district', 'pradeshiya_sabha', 'wasama', 
            'evidence_file'
        ]
        widgets = {
            'citizen_name': forms.TextInput(attrs={
                'class': 'form-control glass-input', 'placeholder': 'Enter your full name'
            }),
            'citizen_email': forms.EmailInput(attrs={
                'class': 'form-control glass-input', 'placeholder': 'name@example.com'
            }),
            'citizen_phone': forms.TextInput(attrs={
                'class': 'form-control glass-input', 'placeholder': 'e.g. 0771234567'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select glass-input'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control glass-input', 'placeholder': 'Brief title of the complaint'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control glass-input', 'rows': 4, 'placeholder': 'Provide a detailed description of the issue...'
            }),
            'district': forms.Select(attrs={
                'class': 'form-select glass-input', 'id': 'id_district'
            }),
            'pradeshiya_sabha': forms.Select(attrs={
                'class': 'form-select glass-input', 'id': 'id_pradeshiya_sabha'
            }),
            'wasama': forms.Select(attrs={
                'class': 'form-select glass-input', 'id': 'id_wasama'
            }),
            'evidence_file': forms.FileInput(attrs={
                'class': 'form-control glass-input', 'accept': 'image/*,audio/*,video/*'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # On initial load, clear the queryset or adjust for sabha and wasama if district/sabha is not selected
        # because the frontend will populate them dynamically using AJAX.
        self.fields['pradeshiya_sabha'].queryset = PradeshiyaSabha.objects.none()
        self.fields['wasama'].queryset = Wasama.objects.none()

        if 'district' in self.data:
            try:
                district_id = int(self.data.get('district'))
                self.fields['pradeshiya_sabha'].queryset = PradeshiyaSabha.objects.filter(district_id=district_id)
            except (ValueError, TypeError):
                pass
        
        if 'pradeshiya_sabha' in self.data:
            try:
                sabha_id = int(self.data.get('pradeshiya_sabha'))
                self.fields['wasama'].queryset = Wasama.objects.filter(pradeshiya_sabha_id=sabha_id)
            except (ValueError, TypeError):
                pass

class OfficerRemarkForm(forms.ModelForm):
    status = forms.ChoiceField(
        choices=Complaint.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select modal-input'})
    )
    remark = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control modal-input', 'rows': 3, 'placeholder': 'Explain the reasoning for this status update...'
        })
    )

    class Meta:
        model = ComplaintRemark
        fields = ['remark']
