from django.shortcuts import render
import logging
import traceback
# Create your views here.

logger = logging.getLogger('django')


def home(request):
    logger.warning('request is processing')
    return render(request, 'project/base.html', {})


def handler404(request, exception):
    return render(request, 'snippets/404.html', status=404)


def handler500(request):
    return render(request, 'snippets/500.html', status=500)
