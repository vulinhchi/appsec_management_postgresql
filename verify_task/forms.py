from django import forms
from .models import VerifyTask
from django.contrib.auth.models import User, Group

class VerifyTaskForm(forms.ModelForm):
    PIC_ISM_select = forms.MultipleChoiceField(
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control',
            'id': 'id_PIC_ISM_select'
        })
    )
    class Meta:
        model = VerifyTask
        fields = ['PIC_ISM', 'PIC_ISM_select']  # `PIC_ISM` là hidden hoặc readonly
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'PIC_ISM': forms.Select(attrs={'class': 'form-control'}),  # Chọn từ dropdown list
        
        }
    def clean(self):
        """Kiểm tra lỗi khi nhập dữ liệu từ form."""
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        name = cleaned_data.get("name")
        if not name:
            self.add_error("name", "This 'name' field is required.")

        if start_date and end_date and start_date > end_date:
            self.add_error("end_date", "End date must be greater than or equal to start date.")
        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user_choices = [(user.username, user.username) for user in User.objects.all()]
        user_choices.insert(0, ('', '--- Choose PIC_ISM ---'))
        self.fields['PIC_ISM'].widget = forms.HiddenInput()

        # self.fields['PIC_ISM'].widget = forms.Select(choices=user_choices)

        pentester_group = Group.objects.get(name="Pentester")
        pentesters = User.objects.filter(groups=pentester_group)
        usernames = [(user.username, user.username) for user in pentesters]
        self.fields['PIC_ISM_select'].choices = usernames
        self.usernames_json = usernames
        # Nếu đang edit, hiển thị lại giá trị đã chọn
        if self.instance and self.instance.PIC_ISM:
            selected = self.instance.PIC_ISM.split(", ")
            self.initial['PIC_ISM_select'] = selected
        self.fields['PIC_ISM'].widget.attrs.update({
            'readonly': True,
            'class': 'form-control',
            'id': 'id_PIC_ISM'
        })