import logging

from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse

LOG = logging.getLogger(__name__)


class IndexView(View):
    """
    Serves the main index page
    """

    def get(self, request):
        LOG.info("IndexView.get")
        context = {}
        return render(request, 'index.html', context=context)
