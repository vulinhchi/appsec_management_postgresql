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
            'is_pentest_task', 'is_verify_task', 'component', 'pentest_vendor'
        ]
        widgets = {
            'PIC_ISM': forms.TextInput(attrs={'readonly': 'readonly'}),
        }

    def clean(self):
        """Kiểm tra lỗi khi nhập dữ liệu từ form."""
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        if not name:
            self.add_error("name", "This field is required.")

        # Remove PIC_ISM if someone tries to inject it via form submission
        if 'PIC_ISM' in self.changed_data:
            cleaned_data['PIC_ISM'] = self.instance.PIC_ISM  # giữ nguyên giá trị cũ
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        # luôn giữ lại giá trị cũ của PIC_ISM
        instance.PIC_ISM = self.instance.PIC_ISM
        if commit:
            instance.save()
        return instance

        

class ShareCostDetailsForm(forms.ModelForm):
    class Meta:
        model = ShareCostDetails
        fields = ['project_code', 'owner', 'cost_mm', 'cost_dolla' , 'month_pay', 'pay_status', 'note']
        

class SecurityExceptionForm(forms.ModelForm):
    class Meta:
        model = SecurityException
        exclude = ['appsec_task']
        # fields = '__all__'
        widgets = {
            'exception_date': forms.DateInput(attrs={'type': 'date'}),
            'exception_create': forms.DateInput(attrs={'type': 'date'}),
        }

