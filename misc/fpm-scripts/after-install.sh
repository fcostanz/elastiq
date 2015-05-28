#!/bin/bash

# add user 'elastiq'
homedir='/home/elastiq'
proguser='elastiq'
#useradd $proguser --shell /sbin/nologin --no-create-home --system --user-group --home-dir "${homedir}"
useradd $proguser --shell /sbin/nologin --system --user-group --home-dir "${homedir}" -m
r=$?
if [[ $r != 9 && $r != 0 ]] ; then
  exit 1
fi
mkdir -p "${homedir}"
chmod u=rwx,g=rwx,o=x "${homedir}"

# register process 'elastiq'
if which chkconfig > /dev/null 2>&1 ; then
  chkconfig --add elastiq
  r=$?
else
  update-rc.d elastiq defaults
  r=$?
fi
[[ $r == 0 ]] || exit $r

# configuration file perms
cf='/etc/elastiq.conf'
chown root:${proguser} "${cf}"
chmod u=rw,g=rw,o= "${cf}"

usermod -a -G rabbitmq elastiq

exit 0
