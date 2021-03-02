# complete_project.wsgi is configured to live in projects/complete_project/deploy.
# If you move this file you need to reconfigure the paths below.

import os
import sys

# redirect sys.stdout to sys.stderr for bad libraries like geopy that uses
# print statements for optional import exceptions.
sys.stdout = sys.stderr

from os.path import abspath, dirname, join
from site import addsitedir

from django.core.handlers.wsgi import WSGIHandler

sys.path.insert(0, abspath(join(dirname(__file__), "../")))
sys.path.insert(0, abspath(join(dirname(__file__), "../../")))

os.environ["DJANGO_SETTINGS_MODULE"] = "mysite.settings2"

application = WSGIHandler()
