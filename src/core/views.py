from django.shortcuts import render
import logging,traceback
# Create your views here.

logger = logging.getLogger('django')
def home(request):
    logger.warning('request is processing')
    return render(request, 'project/base.html', {})