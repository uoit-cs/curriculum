from lib import *
import sqlite3

calendar = Calendar().fetch().parse()

fsci = [f for f in calendar.faculties \
        if f.get('name') == 'Faculty of Science'][0]

fsci.fetch().parse()

cs_progs = [p for p in fsci.programs \
            if p.get('name').startswith('Computer Science') \
               and p.get('degree').startswith('Bachelor of Science')]

courses = dict()

for cs in cs_progs:
    for c in cs.fetch().parse().courses:
        if not c.get('name') in courses:
            print(c.get('name'))
            c.fetch().parse()
            name = c.get('name')
            description = c.get('description')
            courses[name] = description

db = sqlite3.connect('courses.sqlite3')
c = db.cursor()
c.execute('drop table if exists T')
c.execute('create table T (name primary key, desc)')

for k,v in courses.items():
    c.execute("insert into T values(?,?)", (k,v))

db.commit()

