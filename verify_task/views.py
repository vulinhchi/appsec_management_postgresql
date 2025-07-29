from django.shortcuts import render, get_object_or_404, redirect
from appsec_task.models import AppSecTask
from django.contrib import messages
from .forms import VerifyTaskForm
from .models import AppSecTask, VerifyTask
from appsec_task.views import sync_status, send_outlook_email, send_assigned_mail_and_notification
from django.contrib.auth.decorators import login_required
from pentest_task.models import Notification
from task_manager.decorators import require_groups
from django.contrib.auth.models import User
from django.conf import settings



status_colors = {
        "Not Started": "bg-info",
        "In Progress": "bg-warning text-dark",
        "Done": "bg-success",
        "Cancel": "bg-danger text-dark",
    }


@login_required
@require_groups(['Pentester', 'Leader', 'Manager'])
def list_verify_tasks(request):
    # tasks = VerifyTask.objects.all()
    tasks = VerifyTask.objects.select_related("appsec_task").all()
    status_choices = VerifyTask._meta.get_field('status').choices 
    return render(request, 'verify_task/list_verify_tasks.html', {
        'tasks': tasks,
        "status_colors": status_colors,
        "status_choices":status_choices,
         })


@login_required
@require_groups(['Pentester', 'Leader'])
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
            old_assignee = ""
           
            old_assignees = set([
                x.strip() for x in (old_assignee or "").split(",") if x.strip()
            ])

            new_assignees = set([
                x.strip() for x in (verify_task.PIC_ISM or "").split(",") if x.strip()
            ])

            # Gửi noti cho những người mới được thêm vào
            added_users = new_assignees - old_assignees

            removed_users = old_assignees - new_assignees
            for username in added_users:
                try:
                    user = User.objects.get(username=username)
                    
                    send_assigned_mail_and_notification(
                        verify_task, 
                        user, 
                        "verify",
                        "New Verify Task Assigned",
                        "AppSecTool - New Verify Task Assigned",
                        f"You are assigned to verify task '{verify_task.name}'")

                except User.DoesNotExist:
                    continue
            for username in removed_users:
                try:
                    user = User.objects.get(username=username)
                    send_assigned_mail_and_notification(
                        verify_task,
                        user,
                        "verify", 
                        "New Verify Task Rmoved", 
                        "AppSecTool - New Verify Task Removed", 
                        f"You're no longer assigned to this task '{verify_task.name}', so there's no need to continue following it.")

                except User.DoesNotExist:
                    continue

            return redirect("verify_task:list_verify_tasks")
    else:
        form = VerifyTaskForm(initial={"name": appsec_task.name, "description": appsec_task.description})  # Gán trước vào form


    return render(request, "verify_task/create_verify_task.html", {"form": form, "appsec_task": appsec_task, 'usernames': form.usernames_json})


@login_required
@require_groups(['Pentester', 'Leader'])
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

            # old_assignees = set([x.strip() for x in old_assignee.split(",") if x.strip()])
            # new_assignees = set([x.strip() for x in verify_task.PIC_ISM.split(",") if x.strip()])
            old_assignees = set([
                x.strip() for x in (old_assignee or "").split(",") if x.strip()
            ])

            new_assignees = set([
                x.strip() for x in (verify_task.PIC_ISM or "").split(",") if x.strip()
            ])

            # Gửi noti cho những người mới được thêm vào
            added_users = new_assignees - old_assignees

            # 🔹 Người bị gỡ khỏi assign
            removed_users = old_assignees - new_assignees
            for username in added_users:
                try:
                    user = User.objects.get(username=username)
                    
                    send_assigned_mail_and_notification(
                        verify_task, 
                        user, 
                        "verify",
                        "New Verify Task Assigned",
                        "AppSecTool - New Verify Task Assigned",
                        f"You are assigned to verify task '{verify_task.name}'")

                except User.DoesNotExist:
                    continue
            for username in removed_users:
                try:
                    user = User.objects.get(username=username)
                    send_assigned_mail_and_notification(
                        verify_task,
                        user,
                        "verify", 
                        "New Verify Task Rmoved", 
                        "AppSecTool - New Verify Task Removed", 
                        f"You're no longer assigned to this task '{verify_task.name}', so there's no need to continue following it.")

                except User.DoesNotExist:
                    continue

            # return redirect("verify_task:list_verify_tasks")
            messages.success(request, f"Task Verify '{appsec_task.name}' was updated.")
            return redirect(request.META.get('HTTP_REFERER', '/'))
    else:
        form = VerifyTaskForm(instance=task, initial={"name": appsec_task.name, "description": appsec_task.description})  # Gán trước vào form

    return render(request, "verify_task/edit_verify_task.html", {"form": form, "task": task, "appsec_task": appsec_task, 'usernames': form.usernames_json})


@login_required
@require_groups(['Pentester', 'Leader'])
def view_verify_task(request, verify_task_id):
    task = get_object_or_404(VerifyTask, id=verify_task_id)
    appsec_task = task.appsec_task
    # form = VerifyTaskForm(instance=task)  # Form chỉ để hiển thị, không cho phép chỉnh sửa
    return render(request, "verify_task/view_verify_task.html", {"form": task, "appsec_task": appsec_task})


@login_required
@require_groups(['Pentester', 'Leader'])
def delete_verify_task(request, verify_task_id):
    verify_task = get_object_or_404(VerifyTask, id=verify_task_id)

    if request.method == "POST":
        verify_task.delete()
    return redirect('verify_task:list_verify_tasks') 


@login_required
@require_groups(['Pentester', 'Leader'])
def my_task_view(request):
    username = request.user.username.strip().lower()  # normalize username

    # Lấy tất cả các task có PIC_ISM không rỗng
    all_tasks = VerifyTask.objects.exclude(PIC_ISM__isnull=True).exclude(PIC_ISM__exact="")

    def user_in_pic(pic_ism, username):
        users = [u.strip().lower() for u in pic_ism.split(",") if u.strip()]
        return username in users

    # Lọc lại danh sách task
    my_tasks = [task for task in all_tasks if user_in_pic(task.PIC_ISM, username)]
    status_choices = VerifyTask._meta.get_field('status').choices 
    return render(request, 'verify_task/my_tasks.html', 
        {'tasks': my_tasks,
        "status_choices":status_choices,
        })

    
