from lib import *
import sqlite3
import sys

template = 'lib/cards.template'

db = sqlite3.connect('csci_courses.sqlite3')
c = db.cursor()
c.execute('''
    select name from courses
    where name like 'CSCI 3%' or name like 'CSCI 4%'
    order by name
    ''')

courses = [x[0] for x in c.fetchall()]
print(render(template, {'courses': courses}))
