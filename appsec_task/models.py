from django.db import models
from django.core.validators import MinValueValidator
from multiselectfield import MultiSelectField


class AppSecTask(models.Model):
    STATUS_CHOICES = [
        ('Not Start', 'Not Start'),
        ('In Progress', 'In Progress'),
        ('Done', 'Done'),
        ('Interrupt', 'Interrupt'),
        ('Cancel', "Cancel")
    ]
    INTERNET_CHOICES = [
        ('Internet', 'Internet'),
        ('Internal', 'Internal'),
    ]
    
    IS_NEWAPP_CHOICES = [
        ('New App', 'New App'),
        ('Old App', 'Old App'),
    ]
    
    CHECKLIST_TYPE_CHOICES = [
        ('Full Checklist', 'Full Checklist'),
        ('New Function Checklist', 'New Function Checklist'),
        ('No Checklist', 'No Checklist'),
    ]
    
    SHARE_COST_CHOICES = [
        ('Yes', 'Yes'),
        ('No', 'No'),
    ]
    COMPONENT_CHOICES = [
        ('Mobile Application', 'Mobile Application'),
        ('Web Application', 'Web Application'),
        ('API Application','API Application'),
        ('Desktop Application','Desktop Application'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    #plan
    status = models.CharField(max_length=50, null=True, blank=True, choices=STATUS_CHOICES, default='Not Start')
    PIC_ISM = models.CharField(max_length=100, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    # additional information
    environment_prod = models.CharField(max_length=100, null=True, blank=True)
    owner = models.CharField(max_length=250, null=True, blank=True)
    mail_loop = models.TextField(null=True, blank=True)
    chat_group = models.TextField(null=True, blank=True)
    link_ticket = models.URLField(null=True, blank=True)
    link_sharepoint = models.URLField(null=True, blank=True)
    is_internet = models.CharField(max_length=50, choices=INTERNET_CHOICES, default='Internet', null=True, blank=True)
    is_newapp = models.CharField(max_length=50, choices=IS_NEWAPP_CHOICES, default='New App', null=True, blank=True)
    checklist_type = models.CharField(max_length=200, choices=CHECKLIST_TYPE_CHOICES, default='Full Checklist', null=True, blank=True)
    sharecost = models.CharField(max_length=10, choices=SHARE_COST_CHOICES, default='No',null=True, blank=True)
    # component = models.CharField(max_length=200, choices=COMPONENT_CHOICES, default='Web Application',null=True, blank=True)
    component = MultiSelectField(choices=COMPONENT_CHOICES, blank=True, null=True)
    is_pentest_task = models.BooleanField(default=False)
    is_verify_task = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name


class ShareCostDetails(models.Model):
    PIC_CHOICES = [
        ('ISM', 'ISM'),
        ('SAS', 'SAS'),
        ('Other', 'Other'),
    ]
    
    PAY_CHOICES = [
        ('Done', 'Done'),
        ('Information Sent', 'Information Sent'),
        ('Not yet', 'Not yet'),
    ]
    
    appsec_task = models.ForeignKey('AppSecTask', on_delete=models.CASCADE, related_name='share_cost_details')
    pic = models.CharField(max_length=10, choices=PIC_CHOICES, default='ISM')
    project_code = models.CharField(max_length=50,null=True, blank=True)
    owner = models.CharField(max_length=100, null=True, blank=True)
    cost_mm = models.DecimalField(max_digits=100, validators=[MinValueValidator(0)], decimal_places=2, null=True, blank=True) # cost for ISM
    cost_dolla = models.DecimalField(max_digits=100, validators=[MinValueValidator(0)],decimal_places=2, null=True, blank=True) # cost for SAS
    month_pay = models.CharField(max_length=10, null=True, blank=True)  #month pay
    pay_status = models.CharField(max_length=20, choices=PAY_CHOICES, default='Not yet', null=True, blank=True)
    note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Cost Details for {self.appsec_task.name} ({self.project_code})"


class SecurityException(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('Closed', 'Closed'),
    ]

    LEVEL_CHOICES = [
        ('Critical', 'Critical'),
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
        ('Recommend', 'Recommend'),
    ]
    appsec_task = models.ForeignKey(AppSecTask, on_delete=models.CASCADE, related_name='exceptions')
    vulnerability = models.CharField(max_length=255)
    overview = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Open')

    exploitability_level = models.CharField(max_length=50, choices=LEVEL_CHOICES, blank=True, null=True)
    exploitability = models.TextField(blank=True, null=True)

    impact_level = models.CharField(max_length=50, choices=LEVEL_CHOICES, blank=True, null=True)
    impact = models.TextField(blank=True, null=True)

    risk_level = models.CharField(max_length=50, choices=LEVEL_CHOICES, blank=True, null=True)
    risk = models.TextField(blank=True, null=True)

    remediation = models.TextField(blank=True, null=True)
    reason_of_exception = models.TextField(blank=True, null=True)

    exception_date = models.DateField(blank=True, null=True)
    exception_create = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"[{self.vulnerability}] Exception for {self.appsec_task}"





