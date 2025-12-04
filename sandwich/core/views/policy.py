from django.conf import settings
from django.http import Http404
from django.shortcuts import render
from django.views.decorators.cache import cache_page

from sandwich.core.service.policy_service import PolicyService

# Cache for one year in production, these files do not change, but no caching in debug mode
cache_duration = 60 * 60 * 24 * 365 if not settings.DEBUG else 0


@cache_page(cache_duration)
def policy_detail(request, slug):
    lang_info = PolicyService.get_by_slug(slug)
    if not lang_info:
        msg = "Policy not found"
        raise Http404(msg)
    content = PolicyService.get_content_by_slug(slug)
    policy = {
        "label": lang_info.label,
        "content": content,
        "slug": lang_info.slug,
    }
    return render(request, "policy_detail.html", {"policy": policy})
