from lib import *
import sqlite3

listing = CourseListing('CSCI').fetch().parse()

db = sqlite3.connect('csci_courses.sqlite3')
c = db.cursor()
c.execute('drop table if exists courses')
c.execute('create table courses (name primary key)')

for course in listing.courses:
    print(course.get('name'))
    c.execute("insert into courses values(?)", [course.get('name')])

db.commit()

