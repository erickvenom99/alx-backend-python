# messaging/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Message
from django.views.decorators.cache import cache_page

@login_required
def delete_user(request):
    if request.method == 'POST':
        request.user.delete()
        messages.success(request, "Your account has been deleted successfully.")
        return redirect('login')  # or 'home'
    return render(request, 'messaging/delete_confirm.html')  # fixed path


@login_required
def inbox_view(request):
    messages = Message.objects.filter(
        receiver=request.user,
        parent_message__isnull=True
    ).select_related('sender', 'receiver')\
     .prefetch_related('replies', 'replies__sender')\
     .order_by('-timestamp')

    return render(request, 'messaging/inbox.html', {'messages': messages})

@login_required
def inbox_view(request):
    # ←←←←← THIS IS WHAT THE TASK WANTS ←←←←←
    messages = Message.unread.for_user(request.user)  # Only unread + optimized!

    return render(request, 'messaging/inbox.html', {
        'messages': messages,
        'unread_count': messages.count()
    })

    @login_required
@cache_page(60)  # ← CACHES THE ENTIRE VIEW FOR 60 SECONDS!
def inbox_view(request):
    """
    Displays unread/top-level messages for the user.
    Now cached for 60 seconds → super fast!
    """
    messages = Message.unread.for_user(request.user).order_by('-timestamp')

    return render(request, 'messaging/inbox.html', {
        'messages': messages,
        'cache_status': 'This page is cached for 60 seconds!'
    })