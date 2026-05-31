from django import forms
import re
from .models import ContactSubmission


class ContactForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = ContactSubmission
        fields = ['full_name', 'phone', 'email', 'request_type', 'message']
        widgets = {
            'full_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Full Name',
                'required': True,
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Phone Number',
                'required': True,
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'Email Address',
                'required': True,
            }),
            'request_type': forms.Select(attrs={
                'class': 'form-select',
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Your Message (Optional)',
                'rows': 4,
            }),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '') or ''
        if not phone:
            return phone
        digits = re.sub(r'\D+', '', phone)
        if len(digits) < 7 or len(digits) > 20:
            raise forms.ValidationError('Enter a valid phone number.')
        return phone
