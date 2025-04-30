from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.shortcuts import redirect
from pentest_task.models import PentestTask, Vulnerability, AffectedURL
from verify_task.models import VerifyTask
from .models import AppSecTask, ShareCostDetails, SecurityException
from .forms import AppSecTaskForm, ShareCostDetailsForm, SecurityExceptionForm
from django.contrib import messages
from django.db.models import Q, Min, Max
#import, export file
import pandas as pd
import xlsxwriter
from django.http import HttpResponse
from io import BytesIO
import traceback
from datetime import datetime, date
from collections import defaultdict
import openpyxl
import calendar
import json
from django.contrib.auth.decorators import login_required
from task_manager.decorators import require_groups



# from bson.decimal128 import Decimal128
# from django.db.models.functions import ExtractMonth, ExtractYear
# from django.db.models import Count


def safe_str(value):
    return "" if pd.isna(value) or value is None else str(value).strip()

def safe_int(value):
    try:
        return int(value) if not pd.isna(value) and str(value).strip().isdigit() else None
    except ValueError:
        return None


def safe_date(val):
    try:
        if pd.isna(val):
            return None
        if isinstance(val, (datetime, date, pd.Timestamp)):
            return val.date() if isinstance(val, pd.Timestamp) else val
        return pd.to_datetime(str(val)).date()
    except Exception as e:
        # print(f"❌ safe_date error: {e}, val: {val}")
        messages.error(request,f"❌ safe_date error: {e}, val: {val}")
        return None


@login_required
@require_groups(['Pentester', 'Leader'])
def create_appsec_task(request):
    if request.method == "POST":
        form = AppSecTaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('appsec_task:list_appsec_tasks')
    else:
        form = AppSecTaskForm()

    return render(request, 'appsec_task/create_appsec_task.html', {'form': form})


@login_required
@require_groups(['Pentester', 'Leader'])
def edit_appsec_task(request, task_id):
    task = get_object_or_404(AppSecTask, id=task_id)
    if request.method == "POST":
        form = AppSecTaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect("appsec_task:list_appsec_tasks")
    else:
        form = AppSecTaskForm(instance=task)
    return render(request, "appsec_task/edit_appsec_task.html", {"form": form, "task": task})


@login_required
@require_groups(['Pentester', 'Leader'])
def delete_appsec_task(request, task_id):
    task = get_object_or_404(AppSecTask, id=task_id)
    if request.method == "POST":
        task.delete()
    return redirect('appsec_task:list_appsec_tasks') 


@login_required
@require_groups(['Pentester', 'Leader', 'Manager'])
def view_appsec_task(request, task_id):
    task = get_object_or_404(AppSecTask, id=task_id)
    return render(request, "appsec_task/view_appsec_task.html", {"form": task})


@login_required
@require_groups(['Pentester', 'Leader','Manager'])
def list_appsec_tasks(request):
    # tasks = AppSecTask.objects.all()
    tasks = AppSecTask.objects.prefetch_related("pentest_tasks", "verify_tasks").all()
    for task in tasks:
        sync_status(task.id)
    return render(request, 'appsec_task/list_appsec_tasks.html', {'tasks': tasks})
   

@login_required
@require_groups(['Pentester', 'Leader'])
def import_appsec_tasks(request):
    if request.method == "POST" and request.FILES.get("task_file"):
        file = request.FILES["task_file"]
        verify_names = set()
        try:
            xls = pd.ExcelFile(file)

            # Sheet 1: VERIFY TASK
            verify_df = pd.read_excel(xls, sheet_name="Verify Request 2025 (All)")
            for _, row in verify_df.iterrows():
                appsec_name = safe_str(row.get("name"))
                if not appsec_name:
                    print("⚠️ Bỏ qua dòng vì không có appsec_name:", row.to_dict())
                    continue

                # Nếu AppSecTask đã tồn tại thì bỏ qua tạo VerifyTask
                if AppSecTask.objects.filter(name=appsec_name).exists():
                    print(f"⚠️ AppSecTask '{appsec_name}' đã tồn tại, bỏ qua tạo VerifyTask và PentestTask.")
                    continue

                verify_names.add(appsec_name)  
                appsec_task, _ = AppSecTask.objects.get_or_create(name=appsec_name, defaults={
                    'name':safe_str(row.get("name")),
                    'description':safe_str(row.get("description")),
                    'owner': safe_str(row.get("owner")),
                    'environment_prod': safe_str(row.get("environment_prod")),
                    'link_sharepoint': safe_str(row.get("link_sharepoint")),
                    'link_ticket': safe_str(row.get("link_ticket")),
                    'mail_loop': safe_str(row.get("mail_loop")),
                    'chat_group': safe_str(row.get("chat_group")),
                    'is_internet': safe_str(row.get("is_internet")),
                    'is_newapp': safe_str(row.get("is_newapp")),
                    'checklist_type': safe_str(row.get("checklist_type")),
                    'sharecost': safe_str(row.get("sharecost")),
                })
              
                VerifyTask.objects.create(
                    appsec_task=appsec_task, # gắn appsec_task object
                    name=appsec_name,
                    description=safe_str(row.get("description")),
                    
                    PIC_ISM=safe_str(row.get("PIC_ISM")),
                    status=safe_str(row.get("status")),
                    start_date=safe_date(row.get("start_date")),
                    end_date=safe_date(row.get("end_date")),
                )

            # Sheet 2: PENTEST TASK
            pentest_df = pd.read_excel(xls, sheet_name="Pentest Request 2025")
            for _, row in pentest_df.iterrows():
                appsec_name = safe_str(row.get("name"))
                if not appsec_name or appsec_name not in verify_names:
                    continue  # ✅ bỏ qua nếu tên không có trong verify sheet

                try:
                    # Bỏ qua nếu AppSecTask đã tồn tại (đã bị skip ở bước trên)
                    if not AppSecTask.objects.filter(name=appsec_name).exists():
                        print(f"⚠️ AppSecTask '{appsec_name}' không được tạo từ verify sheet, bỏ qua PentestTask.")
                        continue

                    appsec_task = AppSecTask.objects.get(name=appsec_name)
                except AppSecTask.DoesNotExist:
                    print(f"❌ Không tìm thấy AppSecTask tên: {appsec_name}")
                    continue

                if not appsec_name:
                    continue

               
                PentestTask.objects.create(
                    appsec_task=appsec_task, # gắn appsec_task object
                    name=appsec_name,
                    description=safe_str(row.get("description")),
                    
                    environment_test=safe_str(row.get("environment_test")),
                    status=safe_str(row.get("status")),
                    ref=safe_str(row.get("ref")),

                    number_of_apis=safe_int(row.get("number_of_apis")),
                    effort_working_days=safe_int(row.get("effort_working_days")),
                    #scope chưa có info, nên để trống
                    PIC_ISM=safe_str(row.get("PIC_ISM")),
                    start_date=safe_date(row.get("start_date")),
                    end_date=safe_date(row.get("end_date")),
                    start_retest=safe_date(row.get("start_retest")),
                    end_retest=safe_date(row.get("end_retest")),
                    component=safe_str(row.get("component")),
                    
                    
                )

            messages.success(request, "Tasks imported successfully from both sheets!")
        except Exception as e:
            messages.error(request, f"❌ Lỗi tạo VerifyTask: {e}, row: {row.to_dict()}")
            traceback.print_exc()
            # messages.error(request, f"Error importing file: {e}")
        return redirect("appsec_task:list_appsec_tasks")


@login_required
@require_groups(['Pentester', 'Leader', 'Manager'])
def export_appsec_tasks(request):
    # sẽ là export everify, all task, sharecost, vuln, exception
    # Lấy tất cả verify_task + pentest_task
    verify_tasks = VerifyTask.objects.select_related("appsec_task").all()
    pentest_tasks = PentestTask.objects.select_related("appsec_task").all()
    vulnerabilities = Vulnerability.objects.select_related("pentest_task").all()  
    security_exceptions = SecurityException.objects.select_related("appsec_task").all()

    # Sheet 1: Verify Request 2025 (All)
    verify_data = []
    for task in verify_tasks:
        verify_data.append({
            "name": task.appsec_task.name if task.appsec_task else "",
            "description": task.description,
            "owner": task.appsec_task.owner if task.appsec_task else "",
            "environment_prod": task.appsec_task.environment_prod if task.appsec_task else "",
            "PIC_ISM": task.PIC_ISM,
            "status": task.status,
            "start_date": task.start_date,
            "end_date": task.end_date,

            "link_sharepoint": task.appsec_task.link_sharepoint if task.appsec_task else "",
            "link_ticket": task.appsec_task.link_ticket if task.appsec_task else "",
            "mail_loop": task.appsec_task.mail_loop if task.appsec_task else "",
            "chat_group": task.appsec_task.chat_group if task.appsec_task else "",
            "is_internet": task.appsec_task.is_internet if task.appsec_task else "",
            "is_newapp": task.appsec_task.is_newapp if task.appsec_task else "",
            "checklist_type": task.appsec_task.checklist_type if task.appsec_task else "",
            
        })
    verify_df = pd.DataFrame(verify_data)

    # Sheet 2: Pentest Request 2025
    pentest_data = []
    for task in pentest_tasks:
        pentest_data.append({
            "name": task.appsec_task.name if task.appsec_task else "",
            "description": task.description,
            "owner": task.appsec_task.owner if task.appsec_task else "",
            "environment_prod": task.appsec_task.environment_prod if task.appsec_task else "",
            "environment_test": task.environment_test,
            
            "PIC_ISM": task.PIC_ISM,
            "status": task.status,
            "start_date": task.start_date,
            "end_date": task.end_date,
            "start_retest": task.start_retest,
            "end_retest": task.end_retest,
            "ref": task.ref,
            "number_of_apis": task.number_of_apis,
            "effort_working_days": task.effort_working_days,
            
            "link_sharepoint": task.appsec_task.link_sharepoint if task.appsec_task else "",
            "link_ticket": task.appsec_task.link_ticket if task.appsec_task else "",
            "mail_loop": task.appsec_task.mail_loop if task.appsec_task else "",
            "chat_group": task.appsec_task.chat_group if task.appsec_task else "",
            "is_internet": task.appsec_task.is_internet if task.appsec_task else "",
            "is_newapp": task.appsec_task.is_newapp if task.appsec_task else "",
            "checklist_type": task.appsec_task.checklist_type if task.appsec_task else "",
            "component": task.component,
            "sharecost": task.appsec_task.sharecost,
        })
    pentest_df = pd.DataFrame(pentest_data)

    # Sheet 3: Vulnerability
    vuln_data = []
    for vuln in vulnerabilities:
        vuln_data.append({
            "task_name": vuln.pentest_task.name if vuln.pentest_task else "",
            "environment_test": vuln.pentest_task.environment_test if vuln.pentest_task else "",
            "name_vuln": vuln.name_vuln,
            "ref": vuln.ref,
            "risk_rating": vuln.risk_rating,
            "notify_date":vuln.notify_date,
            "status": vuln.status,
            "PIC": vuln.pentest_task.PIC_ISM,
            "component": vuln.pentest_task.component,
            "is_internet": vuln.pentest_task.appsec_task.is_internet if vuln.pentest_task.appsec_task else "",
            "is_newapp": vuln.pentest_task.appsec_task.is_newapp if vuln.pentest_task.appsec_task else "",
            "checklist_type": vuln.pentest_task.appsec_task.checklist_type if vuln.pentest_task.appsec_task else "",
            
        })
    vuln_df = pd.DataFrame(vuln_data)

    # Sheet 4: Exception
    exception_data = []
    for exception in security_exceptions:
        exception_data.append({
            "task_name": exception.appsec_task.name if exception.appsec_task else "",
            "environment_prod": exception.appsec_task.environment_prod if exception.appsec_task else "",
            "vulnerability": exception.vulnerability,
            "risk_level": exception.risk_level,
            "status": exception.status,
            "exception_create":exception.exception_create,
            "exception_date":exception.exception_date,
            "owner":exception.appsec_task.owner,

            "PIC_ISM": exception.appsec_task.PIC_ISM,
            "mail_loop": exception.appsec_task.mail_loop if exception.appsec_task else "",
            "link_sharepoint": exception.appsec_task.link_sharepoint if exception.appsec_task else "",
        })
    exception_df = pd.DataFrame(exception_data)

    # Tạo file Excel với 2 sheet
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        verify_df.to_excel(writer, sheet_name="Verify Request 2025 (All)", index=False)
        pentest_df.to_excel(writer, sheet_name="Pentest Request 2025", index=False)
        vuln_df.to_excel(writer, sheet_name="Vulnerability", index=False) 
        exception_df.to_excel(writer, sheet_name="Exception", index=False) 


    output.seek(0)
    response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=ISM AppSec FollowUp 2025.xlsx'
    return response



def sync_status(appsec_task_id):
    appsec_task = get_object_or_404(AppSecTask, id=appsec_task_id)
    pentest_task = appsec_task.pentest_tasks.first()
    verify_task = appsec_task.verify_tasks.first()

    def is_active(status):
        return status not in ["Not Start", "Done", "Cancel", "Interrupt"]

    def is_not_active(status):
        return status in ["In Progress", "Reported", "Retest"]

    # ==== Đồng bộ status ====
    if pentest_task and verify_task:
        pt_status = pentest_task.status
        vt_status = verify_task.status

        if pt_status == "Cancel" or vt_status == "Cancel":
            appsec_task.status = "Cancel"
        elif pt_status == "Interrupt" or vt_status == "Interrupt":
            appsec_task.status = "Interrupt"
        elif pt_status == "Done" and vt_status == "Done":
            appsec_task.status = "Done"
        elif pt_status == "Not Start" and vt_status == "Not Start":
            appsec_task.status = "Not Start"
        elif is_not_active(pt_status) or is_not_active(vt_status):
            appsec_task.status = "In Progress"
            
        else: 
            appsec_task.status = "In Progress"
        # Đồng bộ ngày
        start_dates = [d for d in [verify_task.start_date, pentest_task.start_date, pentest_task.start_retest] if d]
        end_dates = [d for d in [verify_task.end_date, pentest_task.end_date, pentest_task.end_retest] if d]

        if start_dates:
            appsec_task.start_date = min(start_dates)
        if end_dates:
            appsec_task.end_date = max(end_dates)

       

    elif pentest_task and not verify_task:
        appsec_task.status = pentest_task.status
        appsec_task.start_date = pentest_task.start_date
        appsec_task.end_date = pentest_task.end_date
        

    elif verify_task and not pentest_task:
        appsec_task.status = verify_task.status
        appsec_task.start_date = verify_task.start_date
        appsec_task.end_date = verify_task.end_date
        
    # Đồng bộ PIC_ISM, loại bỏ trùng lặp
    pic_set = set()
    if pentest_task and pentest_task.PIC_ISM:
        pic_set.add(pentest_task.PIC_ISM.strip())
    if verify_task and verify_task.PIC_ISM:
        pic_set.add(verify_task.PIC_ISM.strip())

    appsec_task.PIC_ISM = ", ".join(sorted(pic_set)) if pic_set else None

    appsec_task.pentest_task = pentest_task
    appsec_task.verify_task = verify_task
    appsec_task.save()


@login_required
@require_groups(['Leader', 'Manager'])
def add_sharecost(request, appsec_task_id):
    appsec_task = get_object_or_404(AppSecTask, id=appsec_task_id)
    if request.method == 'POST':
        form = ShareCostDetailsForm(request.POST)
        if form.is_valid():
            share_cost = form.save(commit=False)
            share_cost.appsec_task = appsec_task
            share_cost.save()
            messages.success(request, "Sharecost created successfully.")
            return redirect('appsec_task:list_sharecost')
    else:
        form = ShareCostDetailsForm()
    return render(request, 'appsec_task/add_share_cost.html', {'form': form, 'appsec_task': appsec_task})


@login_required
@require_groups(['Leader', 'Manager'])
def edit_sharecost(request, appsec_task_id, sharecost_id):
    appsec_task = get_object_or_404(AppSecTask, id=appsec_task_id)
    sharecost = get_object_or_404(ShareCostDetails, id=sharecost_id, appsec_task=appsec_task)

    # sharecost = get_object_or_404(ShareCostDetails, id=sharecost_id)
    # if sharecost.appsec_task.id != appsec_task_id:
    #     raise PermissionDenied("Sharecost không thuộc về Appsec Task này.")

    # appsec_task = sharecost.appsec_task  # Lấy AppSecTask liên kết
    
    if request.method == "POST":
        form = ShareCostDetailsForm(request.POST, instance=sharecost)
        if form.is_valid():
            share_cost = form.save(commit=False)
            share_cost.appsec_task = appsec_task
            share_cost.save()
            
            return redirect("appsec_task:list_sharecost")
    else:
        form = ShareCostDetailsForm(instance=sharecost)
    return render(request, "appsec_task/add_share_cost.html", {"form": form, "task": sharecost, "appsec_task":appsec_task})


@login_required
@require_groups(['Leader', 'Manager'])
def view_sharecost(request, appsec_task_id, sharecost_id):
    sharecost = get_object_or_404(ShareCostDetails, id=sharecost_id)
    if sharecost.appsec_task.id != appsec_task_id:
        raise PermissionDenied("Sharecost không thuộc về Appsec Task này.")

    appsec_task = sharecost.appsec_task
    return render(request, 'appsec_task/view_share_cost.html', {'form': sharecost, "appsec_task":appsec_task})


@login_required
@require_groups(['Leader', 'Manager'])
def delete_sharecost(request, appsec_task_id, sharecost_id):
    task = get_object_or_404(ShareCostDetails, id=sharecost_id)
    if task.appsec_task.id != appsec_task_id:
        raise PermissionDenied("Sharecost không thuộc về Appsec Task này.")

    if request.method == "POST":
        task.delete()
    return redirect('appsec_task:list_appsec_tasks') 


@login_required
@require_groups(['Leader', 'Manager'])
def list_sharecost(request):
    tasks = ShareCostDetails.objects.all()
    return render(request, 'appsec_task/list_sharecost.html', {'tasks': tasks})


@login_required
@require_groups(['Leader', 'Manager'])
def export_sharecost_excel(request):
    # Lấy các filter hiện tại từ query params
    queryset = ShareCostDetails.objects.all()

    # Tạo workbook Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "ShareCost Report"

    # Header
    headers = ["Task Name", "Sharecost?", "PIC", "Project Code", "Owner", "Cost (MM)",  "Cost Dolla", "Month Pay", "Pay Status", "Note",]
    ws.append(headers)

    # Data rows
    for obj in queryset:
        ws.append([
            obj.appsec_task.name if obj.appsec_task else "",  # lấy tên task
            obj.appsec_task.sharecost,
            obj.pic,
            obj.project_code,
            obj.owner,
            float(obj.cost_mm.to_decimal()) if obj.cost_mm else 0,
            float(obj.cost_dolla.to_decimal()) if obj.cost_dolla else 0,
            obj.month_pay,
            obj.pay_status,
            obj.note,
            
        ])

    # Trả file về client
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = 'attachment; filename=sharecost_report.xlsx'
    wb.save(response)
    return response


@login_required
@require_groups(['Pentester', 'Leader', 'Manager'])
def all_exceptions(request):
    exceptions = SecurityException.objects.all()
    return render(request, 'appsec_task/all_exceptions.html', {'exceptions': exceptions})


@login_required
@require_groups(['Pentester', 'Leader', 'Manager'])
def exception_list(request, appsec_task_id):
    task = get_object_or_404(AppSecTask, id=appsec_task_id)
    exceptions = SecurityException.objects.filter(appsec_task=task)
    return render(request, 'appsec_task/list_exception.html', {'exceptions': exceptions, 'appsec_task': task})


@login_required
@require_groups(['Pentester', 'Leader', 'Manager'])
def exception_create(request, appsec_task_id):
    task = get_object_or_404(AppSecTask, id=appsec_task_id)
    if request.method == 'POST':
        form = SecurityExceptionForm(request.POST)
        if form.is_valid():
            exception = form.save(commit=False)
            exception.appsec_task = task
            exception.save()
            messages.success(request, "Exception created successfully.")
            return redirect('appsec_task:exception_list', appsec_task_id=task.id)
    else:
        form = SecurityExceptionForm()
    return render(request, 'appsec_task/create_exception.html', {'form': form, 'appsec_task': task})


@login_required
@require_groups(['Pentester', 'Leader', 'Manager'])
def exception_edit(request, appsec_task_id, pk):
    task = get_object_or_404(AppSecTask, id=appsec_task_id)
    exception = get_object_or_404(SecurityException, pk=pk, appsec_task=task)
    if request.method == 'POST':
        form = SecurityExceptionForm(request.POST, instance=exception)
        if form.is_valid():
            exception = form.save(commit=False)
            exception.appsec_task = task
            exception.save()
            messages.success(request, "Exception created successfully.")
            return redirect('appsec_task:exception_list', appsec_task_id=task.id)

    else:
        form = SecurityExceptionForm(instance=exception)
    return render(request, 'appsec_task/create_exception.html', {'form': form, 'appsec_task': task})


@login_required
@require_groups(['Pentester', 'Leader', 'Manager'])
def exception_delete(request, appsec_task_id, pk):
    task = get_object_or_404(AppSecTask, id=appsec_task_id)
    exception = get_object_or_404(SecurityException, pk=pk, appsec_task=task)
    if request.method == 'POST':
        exception.delete()
        messages.success(request, "Exception deleted successfully.")
        return redirect('appsec_task:exception_list', appsec_task_id=task.id)
    return render(request, 'appsec_task/exception_confirm_delete.html', {'exception': exception, 'appsec_task': task})


@login_required
@require_groups(['Pentester', 'Leader', 'Manager'])
def exception_detail(request, appsec_task_id, pk):
    task = get_object_or_404(AppSecTask, id=appsec_task_id)
    exception = get_object_or_404(SecurityException, pk=pk, appsec_task=task)
    return render(request, 'appsec_task/view_exception.html', {'form': exception, 'appsec_task': task})


#dashboard hiển thị:
def get_vuln_stats(selected_year):
    current_year = selected_year
    vuln_stats = {
        'labels': [],
        'affected_apps': [],
        'critical_open': [],
        'critical_close': [],
        'high_open': [],
        'high_close': [],
        'medium_open': [],
        'medium_close': [],
        'total_all': [],
        'total_closed': [],
    }

    for month in range(1, 13):
        vuln_stats['labels'].append(f'{month}')
        start_date = date(current_year, month, 1)
        last_day = calendar.monthrange(current_year, month)[1]
        end_date = date(current_year, month, last_day)

        base_filter = {
            'notify_date__gte': start_date,
            'notify_date__lte': end_date,
            'notify_date__isnull': False
        }

        tasks = Vulnerability.objects.filter(**base_filter).only('pentest_task_id')
        unique_task_ids = set(str(v.pentest_task_id) for v in tasks if v.pentest_task_id)
        vuln_stats['affected_apps'].append(len(unique_task_ids))

        def count_vulns(risk, status):
            return Vulnerability.objects.filter(
                **base_filter,
                risk_rating__iexact=risk,
                status__iexact=status
            ).count()

        total_all = (
            count_vulns('Critical', 'Closed') +
            count_vulns('High', 'Closed') +
            count_vulns('Medium', 'Closed') +
            count_vulns('Critical', 'Open') +
            count_vulns('High', 'Open') +
            count_vulns('Medium', 'Open')
        )
        total_closed = (
            count_vulns('Critical', 'Closed') +
            count_vulns('High', 'Closed') +
            count_vulns('Medium', 'Closed')
        )

        vuln_stats['critical_open'].append(count_vulns('Critical', 'Open'))
        vuln_stats['critical_close'].append(count_vulns('Critical', 'Closed'))
        vuln_stats['high_open'].append(count_vulns('High', 'Open'))
        vuln_stats['high_close'].append(count_vulns('High', 'Closed'))
        vuln_stats['medium_open'].append(count_vulns('Medium', 'Open'))
        vuln_stats['medium_close'].append(count_vulns('Medium', 'Closed'))
        vuln_stats['total_all'].append(total_all)
        vuln_stats['total_closed'].append(total_closed)

    return vuln_stats



def get_affected_url_stats(selected_year):
    affected_urls = AffectedURL.objects.select_related('vulnerability').all()

    monthly_totals = defaultdict(int)
    monthly_closed = defaultdict(int)

    for au in affected_urls:
        vuln = au.vulnerability
        if not vuln or not vuln.notify_date:
            continue
        if vuln.notify_date.year != selected_year:
            continue

        month = vuln.notify_date.month
        monthly_totals[month] += 1

        if vuln.status and vuln.status.lower() == 'closed':
            monthly_closed[month] += 1

    affected_labels = list(range(1, 13))
    affected_total = [monthly_totals.get(month, 0) for month in affected_labels]
    affected_closed = [monthly_closed.get(month, 0) for month in affected_labels]

    return {
        "affected_labels_json": json.dumps(affected_labels),
        "affected_total_json": json.dumps(affected_total),
        "affected_closed_json": json.dumps(affected_closed),

        "affected_labels": affected_labels,
        "affected_total": affected_total,
        "affected_closed": affected_closed,
    }


def get_exception_stats(selected_year):
    exceptions = SecurityException.objects.filter(
        exception_create__isnull=False,
        exception_create__year=selected_year
    )

    monthly_total = defaultdict(int)
    monthly_closed = defaultdict(int)

    for exception in exceptions:
        month = exception.exception_create.month
        monthly_total[month] += 1
        if exception.status.lower() == 'closed':
            monthly_closed[month] += 1

    labels = list(range(1, 13))  # 1 đến 12 tháng
    total_data = [monthly_total.get(month, 0) for month in labels]
    closed_data = [monthly_closed.get(month, 0) for month in labels]

    return {
        "exception_labels_json": json.dumps(labels),
        "exception_total_json": json.dumps(total_data),
        "exception_closed_json": json.dumps(closed_data),

        "exception_labels": labels,
        "exception_total": total_data,
        "exception_closed": closed_data,
    }

    
def task_timeline(current_year):
    pentest_all = PentestTask.objects.filter(start_date__year=current_year)
    retest_all = PentestTask.objects.filter(start_retest__year=current_year)
    verify_all = VerifyTask.objects.filter(start_date__year=current_year)

    def serialize_task(task, task_type):
        data = {
            "name": task.name,
            "pic": task.PIC_ISM,
            "start": task.start_date.strftime("%Y-%m-%d") if task.start_date else "",
            "end": task.end_date.strftime("%Y-%m-%d") if task.end_date else "",
            "type": task_type,
        }

        if task_type == "retest":
            data["start"] = task.start_retest.strftime("%Y-%m-%d") if task.start_retest else ""
            data["end"] = task.end_retest.strftime("%Y-%m-%d") if task.end_retest else ""

        return data

    pentest_retest_tasks = [
        *[serialize_task(task, "pentest") for task in pentest_all],
        *[serialize_task(task, "retest") for task in retest_all],
    ]
    verify_tasks = [serialize_task(task, "verify") for task in verify_all]

    return {
        "pentest_tasks_json": json.dumps(pentest_retest_tasks),
        "verify_tasks_json": json.dumps(verify_tasks),
    }


@login_required
@require_groups(['Pentester', 'Leader', 'Manager'])
def dashboard(request):
    # current_year = datetime.now().year
    year_param = request.GET.get("year")  # Lấy giá trị từ URL: ?year=2024
    try:
        current_year = int(year_param)
    except (TypeError, ValueError):
        current_year = datetime.now().year

    # Tạo danh sách năm từ 2020 đến hiện tại (có thể tùy chỉnh theo dữ liệu bạn có)
    years = list(range(2023, datetime.now().year + 1))


    pentest_counts = defaultdict(int)
    verify_counts = defaultdict(int)

    pentest_tasks = PentestTask.objects.filter(start_date__year=current_year)
    verify_tasks = VerifyTask.objects.filter(start_date__year=current_year)

    for task in pentest_tasks:
        if task.start_date and hasattr(task.start_date, 'month'):
            month = f"{task.start_date.month:02d}"
            pentest_counts[month] += 1

    for task in verify_tasks:
        if task.start_date and hasattr(task.start_date, 'month'):
            month = f"{task.start_date.month:02d}"
            verify_counts[month] += 1

    # List tháng cố định
    months = [f"{i:02d}" for i in range(1, 13)]
    task_stats = [
        {
            "month": month,
            "pentest": pentest_counts.get(month, 0),
            "verify": verify_counts.get(month, 0),
        }
        for month in months
    ]
    # lấy các info về Critical, High, Medium với status là Open và Closed
    vuln_stats = get_vuln_stats(current_year)
    
    # lấy info tổng lỗi Critical+High+Meidum với status là Open và Closed
    # combined_vuln_stats = list(zip(vuln_stats['labels'], vuln_stats['total_all'], vuln_stats['total_closed']))
    combined_vuln_stats = list(zip(
        vuln_stats['labels'],
        vuln_stats['total_all'],
        vuln_stats['total_closed']
    ))

    affected_url_stats = get_affected_url_stats(current_year)
    affected_stats_combined = list(zip(
        affected_url_stats["affected_labels"],
        affected_url_stats["affected_total"],
        affected_url_stats["affected_closed"]
    ))
    
    exception_stats = get_exception_stats(current_year)
    exception_stats_combined = list(zip(
        exception_stats["exception_labels"],
        exception_stats["exception_total"],
        exception_stats["exception_closed"]
    ))
    timeline_stats = task_timeline(current_year)
    
    context = {
        "years": years,
        "selected_year": current_year,
        "task_stats": task_stats,
        "pentest_labels": months,
        "pentest_data": [item["pentest"] for item in task_stats],
        "verify_data": [item["verify"] for item in task_stats],
        # hiẻn thị trong table
        "vuln_stats_combined": combined_vuln_stats,

        #hiển thị trong vulnChart
        "vuln_stats": vuln_stats,

        #hiển thị trong vulnChart2, sẽ hiện info sát với table hơn
        "vuln_labels_json": json.dumps(vuln_stats['labels']),
        "vuln_total_json": json.dumps(vuln_stats['total_all']),
        "vuln_closed_json": json.dumps(vuln_stats['total_closed']),

        "affected_stats_combined": affected_stats_combined,
        # Hiển thị số lượng affected_url
        "affected_labels_json": affected_url_stats["affected_labels_json"],
        "affected_total_json": affected_url_stats["affected_total_json"],
        "affected_closed_json": affected_url_stats["affected_closed_json"],

        "exception_stats_combined": exception_stats_combined,

        # Dành cho chart 
        "exception_labels_json": exception_stats["exception_labels_json"],
        "exception_total_json": exception_stats["exception_total_json"],
        "exception_closed_json": exception_stats["exception_closed_json"],
        "pentest_tasks_json": timeline_stats["pentest_tasks_json"],
        "verify_tasks_json": timeline_stats["verify_tasks_json"]

    }

    return render(request, "appsec_task/dashboard.html", context)


