from django.shortcuts import render, get_object_or_404, redirect
from appsec_task.models import AppSecTask
from django.contrib import messages
from .forms import VerifyTaskForm
from .models import AppSecTask, VerifyTask
from appsec_task.views import sync_status 
from django.contrib.auth.decorators import login_required
from pentest_task.models import Notification

status_colors = {
        "Not Started": "bg-info",
        "In Progress": "bg-warning text-dark",
        "Done": "bg-success",
        "Cancel": "bg-danger text-dark",
    }

def list_verify_tasks(request):
    # tasks = VerifyTask.objects.all()
    tasks = VerifyTask.objects.select_related("appsec_task").all()
    return render(request, 'verify_task/list_verify_tasks.html', {'tasks': tasks,"status_colors": status_colors })


@login_required
def create_verify_task(request, appsec_task_id):
    appsec_task = get_object_or_404(AppSecTask, id=appsec_task_id)

    if request.method == "POST":
        form = VerifyTaskForm(request.POST)
        if form.is_valid():
            verify_task = form.save(commit=False)
            verify_task.appsec_task = appsec_task 
            verify_task.name = appsec_task.name
            sync_status(appsec_task.id)
            verify_task.save()
            # Gửi noti nếu có người được assign
            if verify_task.PIC_ISM:
                Notification.objects.create(
                    user=verify_task.PIC_ISM,
                    message=f"You are assigned to Verify task:: {verify_task.name}",
                )
            return redirect("verify_task:list_verify_tasks")
    else:
        form = VerifyTaskForm(initial={"name": appsec_task.name, "description": appsec_task.description})  # Gán trước vào form


    return render(request, "verify_task/create_verify_task.html", {"form": form, "appsec_task": appsec_task})


@login_required
def edit_verify_task(request, verify_task_id):
    task = get_object_or_404(VerifyTask, id=verify_task_id)
    old_assignee = task.PIC_ISM
    appsec_task = task.appsec_task  # Lấy AppSecTask liên kết
    if request.method == "POST":
        form = VerifyTaskForm(request.POST, instance=task)
        if form.is_valid():
            verify_task = form.save(commit=False)
            verify_task.appsec_task = appsec_task 
            sync_status(appsec_task.id)
            verify_task.save()

            new_assignee = verify_task.PIC_ISM

            if new_assignee != old_assignee and new_assignee:
                Notification.objects.create(
                    user=new_assignee,
                    message=f"You are assigned to Verify task: {verify_task.name}",
                )
            return redirect("verify_task:list_verify_tasks")
    else:
        form = VerifyTaskForm(instance=task, initial={"name": appsec_task.name, "description": appsec_task.description})  # Gán trước vào form

    return render(request, "verify_task/edit_verify_task.html", {"form": form, "task": task, "appsec_task": appsec_task})


@login_required
def view_verify_task(request, verify_task_id):
    task = get_object_or_404(VerifyTask, id=verify_task_id)
    appsec_task = task.appsec_task
    # form = VerifyTaskForm(instance=task)  # Form chỉ để hiển thị, không cho phép chỉnh sửa
    return render(request, "verify_task/view_verify_task.html", {"form": task, "appsec_task": appsec_task})


# 🔴 Delete Verify Task
@login_required
def delete_verify_task(request, verify_task_id):
    verify_task = get_object_or_404(VerifyTask, id=verify_task_id)

    if request.method == "POST":
        verify_task.delete()
    return redirect('verify_task:list_verify_tasks') 


@login_required
def my_task_view(request):
    my_tasks = VerifyTask.objects.filter(PIC_ISM=request.user)
    return render(request, 'verify_task/my_tasks.html', {'tasks': my_tasks})
    
