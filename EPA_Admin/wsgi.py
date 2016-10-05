
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "EPA_Admin.settings")
BASE_PATH = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/..")
if BASE_PATH not in sys.path:
    sys.path.append(BASE_PATH)

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
