from django import forms
from .models import Complaint, Feedback, User, RegistrationRequest

from django import forms
from .models import Complaint

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = [
            'category',
            'preferred_resolution_department',
            'zone',
            'station',
            'building',
            'floor_room',
            'equipment_id',
            'priority',
            'contact_number',
            'nature_of_issue',
            'media_upload',
            'acknowledgment',
            'location',
            'description',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'acknowledgment': forms.CheckboxInput(),
            'media_upload': forms.ClearableFileInput(attrs={'accept': 'image/*,video/*'}),
        }

class ComplaintUpdateForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['status', 'resolution_remarks']
        widgets = {
            'resolution_remarks': forms.Textarea(attrs={'rows': 4}),
        }

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['rating', 'comments']
        widgets = {
            'comments': forms.Textarea(attrs={'rows': 4}),
        }

class OfficerAssignmentForm(forms.ModelForm):
    assigned_user = forms.ModelChoiceField(queryset=User.objects.none())

    def __init__(self, *args, assignment_type='officer', category_first_word=None, **kwargs):
        super().__init__(*args, **kwargs)
        if assignment_type == 'officer':
            self.fields['assigned_user'].queryset = User.objects.filter(is_officer=True)
            self.fields['assigned_user'].label = 'Select New Officer'
        else:
            queryset = User.objects.filter(is_staff=True)
            if category_first_word:
                queryset = queryset.filter(username__icontains=category_first_word)
            self.fields['assigned_user'].queryset = queryset
            self.fields['assigned_user'].label = 'Select New Staff'

    class Meta:
        model = Complaint
        fields = ['assigned_user']

from django import forms
from .models import ComplaintCategory

class RegistrationRequestForm(forms.ModelForm):
    department = forms.ChoiceField(choices=[], required=True)

    class Meta:
        model = RegistrationRequest
        fields = ['full_name', 'email', 'phone', 'department', 'role', 'address', 'qualifications', 'experience']
        widgets = {
            'role': forms.Select(choices=RegistrationRequest.ROLE_CHOICES),
            'address': forms.Textarea(attrs={'rows': 3}),
            'qualifications': forms.Textarea(attrs={'rows': 3}),
            'experience': forms.TextInput(attrs={'placeholder': 'e.g., 5 years'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categories = ComplaintCategory.objects.all()
        choices = [('', '---------')] + [(cat.name, cat.name) for cat in categories]
        self.fields['department'].choices = choices
