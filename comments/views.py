from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import render, get_object_or_404

from .forms import CommentForm
from .models import Comments

# Create your views here.

def comment_delete(request, id):
    #obj = get_object_or_404(Comments, id=id)
    obj = Comments.objects.get(id=id)
    try:
        obj = Comments.objects.get(id=id)
    except:
        raise Http404

    if obj.user != request.user:
        # messages.error(request,"You do not have permission to view this.")
        # raise Http404
        response = HttpResponse("You do not have permission to do this.")
        response.status_code = 403
        return response
        #return render(request, "confirm_delete.html", context, status_code=403)

    if request.method == "POST":
        parent_obj_url = obj.content_object.get_absolute_url()
        obj.delete()
        messages.success(request, "This has been deleted.")
        return HttpResponseRedirect(parent_obj_url)
    context = {
        "object":obj
    }
    return render(request, "confirm_delete.html", context)


def comment_thread(request, id):
    #obj = get_object_or_404(Comments, id=id)
    #obj = Comments.objects.get(id=id)
    try:
        obj = Comments.objects.get(id=id)
    except:
        raise Http404

    if not obj.is_parent:
        obj = obj.parent

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