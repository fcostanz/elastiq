#
# celery.py -- by Dario Berzano <dario.berzano@cern.ch>
#
# Celery plugin for elastiq.
#

import logging
import time
from elastiq import robust_cmd, gethostbyname
import xml.etree.ElementTree as ET
import sys
from celery import Celery
import socket

try:
  # Python 2.6
  from xml.etree.ElementTree import ParseError as XmlParseError
except ImportError:
  # Python 2.7+
  from xml.parsers.expat import ExpatError as XmlParseError

app = 0

def init(cf):
  """Initializes the plugin by getting a dictionary corresponding to our
  configuration. Beware: it might be None."""

  logging.debug("Celery plugin initialized")
  
  global app
  
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  amqp='localhost'

  if (sock.connect_ex((amqp,5672)) == 0):
    app = Celery(broker='amqp://guest@'+amqp+':5672//')
  else:
    logging.error("RabbitMQ server "+amqp+":5672 is not accessible")
    logging.error("Terminating..")
    sys.exit()

def poll_queue(): 
  """Polls Celery for the number of inserted (i.e., "waiting") jobs.
  Returns the number of inserted jobs on success, or None on failure.
  """

  ret = robust_cmd(['sudo', 'rabbitmqctl', 'list_queues', '-q'], max_attempts=2)
  if ret is None or 'output' not in ret:
    return None

  jobs=0
  for queue in ret['output'].split('\n'):
    if len(queue.split('\t')) > 1:
      if (queue.split('\t')[0].find("celery") > -1):
        jobs+=int(queue.split('\t')[1])

  return jobs

def poll_status(current_workers_status, valid_ipv4s=None):
  """Polls Celery for the list of workers with the number of running jobs
  per worker. Returns an array of hosts, each one of them has a parameter that
  indicates the number of running jobs."""

  global app

  i=app.control.inspect()

  stats=i.stats()
  active=i.active()

  workers_status = {}

  if (active == None):
    return workers_status	

  for host,info in active.iteritems():    
    activity='Busy'
    if (len(active[host]) == 0):
      activity='Idle'

    # If we have a list of valid IPv4 addresses, check if it matches.
    if valid_ipv4s is not None:
      try:
        ip = gethostbyname(host)
        if ip not in valid_ipv4s:
          logging.debug("Poll status: %s ignored (no matching VM)" % host)
          continue
      except Exception:
        logging.debug("Poll status: %s ignored (cannot resolve IP)" % host)
        continue

    # Here we have host and activity. Activity might be, for instance,
    # 'Idle' or 'Busy'. We only check for 'Idle'
    idle = (activity == 'Idle')

    if host in workers_status:
      # Update current entry ('jobs' key is there always)
      if not idle:
        workers_status[host]['jobs'] = workers_status[host]['jobs'] + 1
    else:
      # Entry not yet present
      workers_status[host] = {}
      if idle:
        workers_status[host]['jobs'] = 0
      else:
        workers_status[host]['jobs'] = 1
     
    logging.debug("Found: %s is %s" % (host,activity))
  
  # At this point we have the previous state and the current state saved
  # properly somewhere.
  # Browse the new list for all workers with zero jobs, check if they already
  # had zero jobs in the previous call, in case they're not, update the time

  check_time = time.time()

  for host,info in workers_status.iteritems():
    if host in current_workers_status and \
      current_workers_status[host]['jobs'] == info['jobs']:
      workers_status[host]['unchangedsince'] = current_workers_status[host]['unchangedsince']
    else:
      workers_status[host]['unchangedsince'] = check_time

  # Returns the new status
  return workers_status





'''







import logging
import time
from elastiq import robust_cmd, gethostbycondorname
import xml.etree.ElementTree as ET
try:
  # Python 2.6
  from xml.etree.ElementTree import ParseError as XmlParseError
except ImportError:
  # Python 2.7+
  from xml.parsers.expat import ExpatError as XmlParseError


def init(cf):
  """Initializes the plugin by getting a dictionary corresponding to our
  configuration. Beware: it might be None."""

  logging.debug("HTCondor plugin initialized")


def poll_queue(): 
  """Polls HTCondor for the number of inserted (i.e., "waiting") jobs.
  Returns the number of inserted jobs on success, or None on failure.
  """

  ret = robust_cmd(['condor_q', '-attributes', 'JobStatus', '-long'], max_attempts=5)
  if ret and 'output' in ret:
    return ret['output'].count("JobStatus = 1")

  return None


def poll_status(current_workers_status, valid_ipv4s=None):
  """Polls HTCondor for the list of workers with the number of running jobs
  per worker. Returns an array of hosts, each one of them has a parameter that
  indicates the number of running jobs."""

  ret = robust_cmd(['condor_status', '-xml', '-attributes', 'Activity,Machine'], max_attempts=2)
  if ret is None or 'output' not in ret:
    return None

  workers_status = {}

  try:

    xdoc = ET.fromstring(ret['output'])
    #xdoc = ET.fromstring("this is clearly invaild XML")
    for xc in xdoc.findall("./c"):

      # List of the parameters to search for. XML structure is, for each job
      # slot:
      # <c>
      #   <a n="MyType">Machine</a>
      #   <a n="Machine">host.name</a>
      #   <a n="Activity">Idle</a>
      # </c>
      params = {
        'MyType': None,
        'Machine': None,
        'Activity': None
      }

      for xa in xc.findall("./a"):
        n = xa.get("n")
        if n is None:
          continue
        for k in params:
          if n == k:
            xs = xa.find("./s")
            if xs is not None:
              params[n] = xs.text

      # Do we have all the needed parameters?
      valid = True
      for k,v in params.iteritems():
        if v is None:
          valid = False
          break
      if valid == False:
        continue

      # If it is not a machine, skip it
      if params['MyType'] != 'Machine':
        continue

      # Simpler variables
      host = params['Machine']
      activity = params['Activity']
      logging.debug("Found: %s is %s" % (host,activity))

      # If we have a list of valid IPv4 addresses, check if it matches.
      if valid_ipv4s is not None:
        try:
          ip = gethostbycondorname(host)
          if ip not in valid_ipv4s:
            logging.debug("Poll status: %s ignored (no matching VM)" % host)
            continue
        except Exception:
          logging.debug("Poll status: %s ignored (cannot resolve IP)" % host)
          continue

      # Here we have host and activity. Activity might be, for instance,
      # 'Idle' or 'Busy'. We only check for 'Idle'

      idle = (activity == 'Idle')

      if host in workers_status:
        # Update current entry ('jobs' key is there always)
        if not idle:
          workers_status[host]['jobs'] = workers_status[host]['jobs'] + 1
      else:
        # Entry not yet present
        workers_status[host] = {}
        if idle:
          workers_status[host]['jobs'] = 0
        else:
          workers_status[host]['jobs'] = 1

  except XmlParseError as e:
    logging.error("Invalid XML: %s" % e)
    return None

  # At this point we have the previous state and the current state saved
  # properly somewhere.
  # Browse the new list for all workers with zero jobs, check if they already
  # had zero jobs in the previous call, in case they're not, update the time

  check_time = time.time()

  for host,info in workers_status.iteritems():
    if host in current_workers_status and \
      current_workers_status[host]['jobs'] == info['jobs']:
      workers_status[host]['unchangedsince'] = current_workers_status[host]['unchangedsince']
    else:
      workers_status[host]['unchangedsince'] = check_time

  # Returns the new status
  return workers_status
'''
