from distutils.core import setup

setup(
    name='Quest',
    version='0.1.0',
    packages=['quest','quest.test','quest.query','quest.web'],
    package_data={'quest.web': ['*.conf', '*.js']},
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    homepage="https://github.com/gabebw/quest",
    long_description=open('README.txt').read(),
    # Can't require mysql-python :(
    requires=['sqlalchemy (>=0.6.5)', 'sqlparse', 'cherrypy (>=3.1)']
)
