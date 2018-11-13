import sys
import urllib.parse
from pathlib import Path
from types import SimpleNamespace

from challenges.conf import Conf
from django.http import HttpResponse, Http404
from django.template.loader import get_template
from django.conf import settings

def _get_challenge(dir):
    parent = str(dir.parent)
    sys.path += [parent]
    sys.argv = ['', dir.name]
    conf = Conf()
    conf.root = parent
    conf.parse_arguments()
    challenge = conf.get_challenge()

    def set_names(challenge):
        docstring = challenge.__doc__
        lines = docstring.splitlines()
        if lines[0].strip() != "" and lines[1].strip() == "":
            challenge.name = lines[0].strip()
        else:
            challenge.name = dir.name
        challenge.classname = challenge.__class__.__name__
        challenge.doc = docstring

    set_names(challenge)
    return challenge


def challenge(request, path):
    path = urllib.parse.unquote(path)
    base = Path(settings.BASE_DIR) / 'private' / 'challenges'
    dir = (base / path).absolute()
    # only accept paths below base
    if not str(dir).startswith(str(base)):
        raise Http404
    if dir.is_dir():
        challenge = _get_challenge(dir)
        template = get_template('django_challenges_adapter/challenge.html')
        return HttpResponse(template.render({'challenge': challenge}, request))
    else:
        raise Http404


def index(request):
    base = Path(settings.BASE_DIR) / 'private' / 'challenges'
    directories = []
    for dir in base.iterdir():
        if not dir.is_dir():
            continue
        directory = SimpleNamespace()
        directories.append(directory)
        directory.name = str(dir.name).replace('_', ' ')
        url_part_1 = urllib.parse.quote(dir.name)
        directory.directories = []
        for dir2 in dir.iterdir():
            if not dir2.is_dir():
                continue
            directory2 = SimpleNamespace()
            directory.directories.append(directory2)
            directory2.name = str(dir2.name).replace('_', ' ')
            url_part_2 = urllib.parse.quote(dir2.name)
            directory2.directories = []
            for dir3 in dir2.iterdir():
                if not dir3.is_dir():
                    continue
                directory3 = SimpleNamespace()
                directory2.directories.append(directory3)
                directory3.name = str(dir3.name).replace('_', ' ')
                url_part_3 = urllib.parse.quote(dir3.name)
                directory3.url = Path(url_part_1) / url_part_2 / url_part_3
    template = get_template('django_challenges_adapter/index.html')
    return HttpResponse(template.render({'directories': directories}, request))
