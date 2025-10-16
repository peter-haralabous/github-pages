from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView

switcher = login_required(TemplateView.as_view(template_name="pages/switcher.html"))
