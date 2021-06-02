from django.urls import include, path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

admin.autodiscover()

from tickets.views import TicketListView


urlpatterns = [
    # homepages
    path("", TicketListView.as_view(), name="home"),
    path("", TicketListView.as_view(), name="index"),
    path("admin/doc/", include("django.contrib.admindocs.urls")),
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("tickets/", include(("tickets.urls", "tickets"), namespace="tickets")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = (
        [path("__debug__/", include(debug_toolbar.urls))]
        + urlpatterns
        + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    )
