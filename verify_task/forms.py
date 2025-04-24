from django import forms
from .models import VerifyTask

class VerifyTaskForm(forms.ModelForm):
    class Meta:
        model = VerifyTask
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
    def clean(self):
        """Kiểm tra lỗi khi nhập dữ liệu từ form."""
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        name = cleaned_data.get("name")
        if not name:
            self.add_error("name", "This field is required.")

        if start_date and end_date and start_date > end_date:
            self.add_error("end_date", "End date must be greater than or equal to start date.")
        return cleaned_data

