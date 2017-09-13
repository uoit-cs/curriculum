from lib import *
import sqlite3

db = sqlite3.connect('courses.sqlite3')
c = db.cursor()
c.execute('''
    select name, desc from T 
    where name like 'CSCI 3%' or name like 'CSCI 4%'
    order by name
    ''')

courses = c.fetchall()
print(render('courses.template', {'courses': courses}))
