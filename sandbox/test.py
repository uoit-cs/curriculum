from lib import *

cal = Calendar().get().parse()

sci = [x for x in cal.faculties if 'Faculty of Science' in x['name']][0]
faculty = Faculty(sci['href']).get().parse()

cs = [x for x in faculty.programs if 'Computer Science' in x['name']][0]
prog = Program(cs['href']).get().parse()

c = prog.courses[0]
course = Course(c['href']).get().parse()
