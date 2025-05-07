from django import forms
from .models import AppSecTask, ShareCostDetails, SecurityException

class AppSecTaskForm(forms.ModelForm):
    class Meta:
        model = AppSecTask
        fields = [
            'name', 'description', 'status', 
            'PIC_ISM', 
            'environment_prod', 'owner', 'mail_loop', 'chat_group', 'link_ticket', 
            'link_sharepoint', 'is_internet', 'is_newapp', 'checklist_type', 'sharecost',
            'is_pentest_task', 'is_verify_task', 'component'
        ]
    def clean(self):
        """Kiểm tra lỗi khi nhập dữ liệu từ form."""
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        if not name:
            self.add_error("name", "This field is required.")
        return cleaned_data
        

class ShareCostDetailsForm(forms.ModelForm):
    class Meta:
        model = ShareCostDetails
        fields = ['pic', 'project_code', 'owner', 'cost_mm', 'cost_dolla' , 'month_pay', 'pay_status', 'note']


class SecurityExceptionForm(forms.ModelForm):
    class Meta:
        model = SecurityException
        exclude = ['appsec_task']
        # fields = '__all__'
        widgets = {
            'exception_date': forms.DateInput(attrs={'type': 'date'}),
            'exception_create': forms.DateInput(attrs={'type': 'date'}),
        }

