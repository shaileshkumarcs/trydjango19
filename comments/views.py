from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from .forms import CommentForm
from .models import Comments

# Create your views here.

def comment_thread(request, id):
    obj = get_object_or_404(Comments, id=id)
    content_object = obj.content_object   # Post that comment is on
    content_id = obj.content_object.id
    inital_data = {
        "content_type": obj.content_type,
        "object_id": obj.object_id,
    }


    form = CommentForm(request.POST or None, initial=inital_data)
    if form.is_valid():
        c_type = form.cleaned_data.get("content_type")
        content_type = ContentType.objects.get(model=c_type)
        obj_id = form.cleaned_data.get("object_id")
        parent_obj = None
        try:
            parent_id = int(request.POST.get('parent_id'))
        except:
            parent_id = None

        if parent_id:
            parent_qs = Comments.objects.filter(id=parent_id)
            if parent_qs.exists() and parent_qs.count() == 1:
                parent_obj = parent_qs.first()



        content_data = form.cleaned_data.get("content")

        new_comments, created = Comments.objects.get_or_create(
                        user = request.user,
                        content_type = content_type,
                        object_id = obj_id,
                        content = content_data,
                        parent = parent_obj,
                    )
        return HttpResponseRedirect(new_comments.content_object.get_absolute_url())
    context = {
        "comments": obj,
        "form" : form
    }
    return render(request, "comment_thread.html",context)