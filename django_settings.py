"""=============================================================
~/tickettracker2/django_settings.py
 Created: 10 Jun 2020 14:19:09


 DESCRIPTION:

 This little script is intended to work with emacs virtualenv and
 django on windows.  While django comes with a command line utility
 (./manage.py shell), the resultant shell does not work properly on
 windows machine when used inside of emacs.  This script is intended
 to allow you to open a standard python prompt in emacs and then
 import all of your regular django settings and objects.

 To use it,
 activate an emacs virtualenv -> M-x virtualenv-activate <Return> /venv/

 next start a python interpreter (usual by sending region of beging code)
 then at the python command prompt 'import django_settings'

 as a bonus, all of your model will aready be imported as A, meaning
 that you can run queries like so:

 rs = A.<model>.objects.all()
 rs2 = A.<model2>.objects.filter(foo=bar)

NOTE - the current working directory should be the root of your django
project (where manage.py and this file are).  If you open a shell and
are unable to import django_settings or your models, you may have to
move the working directory up one level:

os.getcwd()
os.chdir(os.path.split(os.getcwd())[0])
os.chdir(c:/1work/Python/djcode/fn_portal)

 A. Cottrill
=============================================================

"""

import sys
import os

SETTINGS_FILE = "main.settings.local"
# SETTINGS_FILE = "main.settings.append_data_remote"

# add the current directory to path so that we can find our settings files:
sys.path.append(os.path.dirname(__file__))

# SECRET should be set when virtualenv as activated.  Just incase its not
os.environ["SECRET_KEY"] = "\xb1>\xf3\x10\xd3p\x07\x8fS\x94'\xe3g\xc6cZ4\xb0R"

# taken from manage.py
os.environ.setdefault("DJANGO_SETTINGS_MODULE", SETTINGS_FILE)

# from: http://sontek.net/blog/detail/tips-and-tricks-for-the-python-interpreter
if "DJANGO_SETTINGS_MODULE" in os.environ:
    # from django.db.models.loading import get_models
    import django
    from django.apps import apps
    from django.test.client import Client
    from django.test.utils import setup_test_environment, teardown_test_environment
    from django.conf import settings as S

    django.setup()

    class DjangoModels(object):
        """Loop through all the models in INSTALLED_APPS and import them."""

        def __init__(self):
            for m in apps.get_models():
                setattr(self, m.__name__, m)

    A = DjangoModels()
    C = Client()
