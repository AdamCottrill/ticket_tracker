from main.settings.base import *

SECRET_KEY = get_env_variable("SECRET_KEY")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "%s/db/tickettracker.db" % PROJECT_ROOT,
    }
}


MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

INSTALLED_APPS += (
    "debug_toolbar",
    #    'django_extensions',
)

INTERNAL_IPS = ("127.0.0.1",)  # added for debug toolbar
DEBUG_TOOLBAR_CONFIG = {
    "INTERCEPT_REDIRECTS": False,
}
