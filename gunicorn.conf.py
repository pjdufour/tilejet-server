import os

# Development
bind = '0.0.0.0:8080'
workers = 4
# Production
#bind = 'unix:///tmp/gunicorn.sock'
#workers = 5
#
worker_class = 'gevent'
#worker_class = 'egg:gunicorn#gevent'
# Logging
loglevel = 'info'
acces_logfile = "access.log"
error_logfile = "error.log"
#enable_stdio_inheritance = True
timeout = 360
