import requests
import bs4
from bs4 import BeautifulSoup
import re
import os
import jinja2

# Build URLS

HOST = "http://calendar.uoit.ca"

def URL(s):
    return os.path.join(HOST, re.sub(r'\s+', "", s))

def clear_text(s):
    return s.replace('\xa0', ' ')

class Restful(object):
    def __init__(self, url):
        self.url = url
        self.data = dict()

    def fetch(self):
        r = requests.get(URL(self.url))
        self.soup = BeautifulSoup(r.text, 'lxml')
        return self

    def info(self, **K):
        self.data.update(K)
        return self

    def get(self, k):
        return self.data.get(k)

    def parse(self):
        raise(Exception('Not implemented'))

class Course(Restful):
    def parse(self):
        h3 = self.soup.find('h3')
        self.data['name'] = h3.get_text().replace('\xa0', ' ')
        for i, x in enumerate(h3.next_siblings):
            if isinstance(x, bs4.element.Tag): 
                tagname = x.name
                text = x.get_text().strip()
                if tagname == 'hr':
                    self.data['description'] = str(x.next_sibling)
                elif text.startswith("Credit hours"):
                    self.data['credit_hours'] = str(x.next_sibling.strip())
                elif text.startswith("Lecture hours"):
                    self.data['lecture_hours'] = str(x.next_sibling.strip())
                elif text.startswith("Laboratory hours"):
                    self.data['laboratory_hours'] = str(x.next_sibling.strip())
        return self

def course_href(catoid, coid):
    return '''
            ajax/preview_course.php
            ?catoid=%s
            &coid=%s
            &show
           ''' % (catoid, coid)

class Program(Restful):
    def parse(self):
        self.courses = []
        for li in self.soup.find_all('li', class_='acalog-course'):
            a = li.find("a")
            name = a.get_text()
            code = a['onclick']
            m = re.search(r'\((.*)\)', code)
            if m:
                args = [x.strip(" '") for x in m.group(1).split(",")]
                if len(args) == 4:
                    (catoid, coid, _, display) = args
                    href = course_href(catoid, coid)
                    self.courses.append(Course(href).info(name=clear_text(name)))
        return self


class Faculty(Restful):
    def _get_degrees(self):
        degrees = []
        for h3 in self.soup.find_all('h3'):
            if h3.get_text() == 'Programs':
                for x in h3.next_siblings:
                    try:
                        if x.name == 'strong':
                            y = x.next_sibling
                            if y.name == 'ul':
                                yield (x, y)
                    except:
                        continue

    def parse(self):
        self.programs = []
        for strong, ul in self._get_degrees():
            degree = strong.get_text()
            for a in ul.find_all('a'):
                name = a.get_text()
                href = a['href']
                self.programs.append(
                        Program(href).info(name=name, degree=degree))
        return self

class Calendar(Restful):
    def __init__(self):
        super().__init__('content.php ?catoid=12 &navoid=447')
    def parse(self):
        self.faculties = []
        for a in self.soup.find_all('a'):
            text = a.get_text()
            if text.startswith("Faculty"):
                href = a['href']
                self.faculties.append(Faculty(href).info(name=text))
        return self

class CourseListing(Restful):
    def __init__(self, prefix='CSCI'):
        self.url = '''content.php
                    ?filter[27]=%s
                    &filter[29]=
                    &filter[course_type]=-1
                    &filter[keyword]=
                    &filter[32]=1
                    &filter[cpage]=1
                    &cur_cat_oid=12
                    &expand=
                    &navoid=441
                    &search_database=Filter''' % prefix
    def parse(self):
        self.courses = []
        for a in self.soup.find_all('a'):
            try:
                href = a['href']
                if href.startswith('preview_course'):
                    m = re.search(r'catoid=(\d+)&coid=(\d+)', href)
                    if m:
                        url = course_href(m.group(1), m.group(2))
                        name = clear_text(a.get_text())
                        self.courses.append(Course(url).info(name=name))
            except:
                pass
        return self

def render(path, context):
    path, filename = os.path.split(path)
    return jinja2.Environment(loader=jinja2.FileSystemLoader(path or "./")
            ).get_template(filename).render(context)


