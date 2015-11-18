TileJet Server (tilejet-server)
==================

## Description

This repository contains a Django server for running TileJet.  This application provides a Django interface for managing an in-memory tile cache and translator.  The application acts like a proxy and translates between tile schemas if possible.  For example, you can service tiles in TMS, TMS-Flipped, and Bing formats while only saving tiles on disk in one format when using `tilejet-server` as a proxy/cache.  The goal is to create a server that uses heuristics and branch prediction to provide extremely responsive caches.

This library was initially developed through the [Imagery to the Crowd Initiative](http://mapgive.state.gov/ittc/).

### CyberGIS
The [Humanitarian Information Unit](https://hiu.state.gov/Pages/Home.aspx) has been developing a sophisticated geographic computing infrastructure referred to as the CyberGIS. The CyberGIS provides highly available, scalable, reliable, and timely geospatial services capable of supporting multiple concurrent projects.  The CyberGIS relies on primarily open source projects, such as PostGIS, GeoServer, GDAL, GeoGit, OGR, and OpenLayers.  The name CyberGIS is dervied from the term geospatial cyberinfrastructure.

### Imagery to the Crowd
The [Imagery to the Crowd Initiative](http://mapgive.state.gov/ittc/) (or IttC) is a core initiative of the [Humanitarian Information Unit](https://hiu.state.gov/Pages/Home.aspx).  Through IttC, HIU publishes high-resolution commercial satellite imagery, purchased by the United States Government, in a web-based format that can be easily mapped by volunteers.  These imagery services are used by volunteers to add baseline geographic data into [OpenStreetMap](http://www.openstreetmap.org/), such as roads and buildings.  The imagery processing pipeline is built from opensource applications, such as TileCache and GeoServer.  All tools developed by HIU for ITTC, are also open source, such as this repo.  More information can be found at [http://mapgive.state.gov/ittc/](http://mapgive.state.gov/ittc/).

## Provision

Before you begin the installation process, you'll need to provision a virtual or physical machine.  TileJet Server will run on [Amazon Web Services (AWS)](#aws-machines), [Vagrant](#vagrant-machines), and almost any type of virtual machine.

Most VMs, AMIs, boxes, etc. of Ubuntu 14.04.X won't be 100% up to date when provisioned.  Although not necessary, you should upgrade all your packages as soon as you SSH into the machine for the first time and before you begin the installation process.  In Ubuntu that is: `sudo apt-get update; sudo apt-get upgrade;`.

### AWS Machines
If you are provisioning an instance using Amazon Web Services, we recommend you use the baseline Ubuntu 14.04 LTS AMI managed by Ubuntu/Canonical.  You can lookup the most recent ami code on this page: [https://cloud-images.ubuntu.com/releases/trusty/release/](https://cloud-images.ubuntu.com/releases/trusty/release/).  Generally speaking, you should use the 64-bit EBS-SSD AMI for TileJet Server.

### Vagrant Machines

If you are installing TileJet Server on a Vagrant VM it is a good idea to assert the correct locale through the following code block.  Most other builds, such as the Amazon AWS Ubuntu images, do not need this step as they are configured properly.  See issue 985 for explanation at [https://github.com/GeoNode/geonode/issues/985](https://github.com/GeoNode/geonode/issues/985).

```shell
export LANGUAGE=en_US.UTF-8
export LANG=en_US.UTF-8
export LC_ALL=en_US.UTF-8

locale-gen en_US.UTF-8
dpkg-reconfigure locales
```

## Installation

As root (`sudo su -`), execute the following commands:

```
apt-get update
apt-get install -y curl vim git nginx
apt-get install -y memcached zlib1g-dev libjpeg-dev rabbitmq-server
apt-get install -y python-dev python-pip
apt-get install -y zookeeperd
apt-get install -y supervisor
# Install Python Virtual Environment libraries
pip install virtualenvwrapper paver
```

Then, as ubuntu, clone this repo with commands like the following.

```
cd ~
git clone https://github.com/tilejet/tilejet-server.git tilejet-server.git
```

### Virtual Environment

Make virtual environment `tilejet`.

```
# Add Virtual Environment Setup to ~/.bash_aliases
echo 'export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python' >> ~/.bash_aliases
echo 'export WORKON_HOME=~/.venvs' >> ~/.bash_aliases
echo 'source /usr/local/bin/virtualenvwrapper.sh'>> ~/.bash_aliases
echo 'export PIP_DOWNLOAD_CACHE=$HOME/.pip-downloads' >> ~/.bash_aliases
# Make TileJet Virtual Environment
source ~/.bash_aliases
mkvirtualenv tilejet
workon tilejet
````
Then, as root, then install python packages with:
```
cd tilejet-server.git
pip install -r requirements.txt
```

If there are any issues with celery be correctly configured, run pip install for the following packages from https://github.com/tilejet/celery/blob/umemcache/requirements/dev.txt manually.

```
workon tilejet
pip install https://github.com/celery/py-amqp/zipball/master
pip install https://github.com/celery/billiard/zipball/master
pip install https://github.com/celery/kombu/zipball/master
```

or if upgrading:

```
workon tilejet
pip install https://github.com/celery/py-amqp/zipball/master --upgrade
pip install https://github.com/celery/kombu/zipball/master --upgrade
pip install https://github.com/celery/billiard/zipball/master --upgrade
```

The requirements.txt file will install a fork of celery that works with unmemcache.

### MongoDB

Then, as root (`sudo su -`), install MongoDB with the following based on http://docs.mongodb.org/manual/tutorial/install-mongodb-on-ubuntu/

```
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | tee /etc/apt/sources.list.d/mongodb.list
apt-get update
apt-get install -y mongodb-org

# Pin Current Version of MongoDB
echo "mongodb-org hold" | sudo dpkg --set-selections
echo "mongodb-org-server hold" | sudo dpkg --set-selections
echo "mongodb-org-shell hold" | sudo dpkg --set-selections
echo "mongodb-org-mongos hold" | sudo dpkg --set-selections
echo "mongodb-org-tools hold" | sudo dpkg --set-selections`
```

Exit as root user.  Then, update SITEURL (e.g., http://hiu-maps.net/) in `tilejetserver/settings.py`:

```
vim tilejet-server.git/tilejetserver/settings.py
```

### NGINX

Create directory for static files for NGINX and copy over static files.

```
sudo mkdir -p /var/www/tilejet/static
sudo chown -R ubuntu:ubuntu /var/www/tilejet
workon tilejet
export DJANGO_SETTINGS_MODULE="tilejetserver.settings"
python manage.py collectstatic
```

Also change the root for NGINX to point to `/var/www`.

### Kafka

As root(`sudo su -`):

```
cd /opt
wget 'http://apache.cs.utah.edu/kafka/0.8.2.0/kafka_2.10-0.8.2.0.tgz' -O 'kafka_2.10-0.8.2.0.tgz'
tar -xzvf kafka_2.10-0.8.2.0.tgz
echo 'PATH="$PATH:/opt/kafka_2.10-0.8.2.0/bin"' >> /etc/profile.d/kafka.sh
source /etc/profile.d/kafka.sh
```

## Usage

The application can be run through the Django built-in development server or Gnuicron ([http://gunicorn.org/](http://gunicorn.org/)).

There is a [supervisord.conf configuration file](https://github.com/tilejet/tilejet-server/blob/master/supervisord.conf) that should automate some of this process in a full production environment.  It is configured for vagrant, but can be easily configured for other users.

First, as root, clear the RabbitMQ cache of messages with:

```
rabbitmqctl stop_app
rabbitmqctl reset
rabbitmqctl start_app
```


You first need to start 3 memcached instances with the following commands  The settings.py assumes the default cache is running on port 11211, the cache for the tiles is running on port 11212, and the cache for Celery results is running on port 11213.

```
memcached -vv -m 128 -p 11211 -d
memcached -vv -m 1024 -p 11212 -d
memcached -vv -m 128 -p 11213 -d
```

Start MongoDB if it does not start automatically with:

```
sudo service mongod start
```

Then, prepare the server.

```
cd tilejet-server.git
python manage.py syncdb
```

If `syncdb` asks if you would like to create an admin user, do it. 

Then start a Celery worker with:

```
cd tilejet-server.git
celery -A tilejetserver worker -P gevent --loglevel=error --concurrency=40 -n worker1.%h
```

To run the application using the Django built-in development server, execute the following:

```
python manage.py runserver [::]:8000
```

To run the application using Gnuicorn, execute the following:

```
gunicorn --workers=4 --worker-class gevent -b 0.0.0.0:8000 tilejetserver.wsgi
or
gunicorn --workers=4 --worker-class gevent -b unix:///tmp/gunicorn.sock --error-logfile error.log tiljetserver.wsgi
```

You can learn more about gunicron configuration at [http://docs.gunicorn.org/en/develop/configure.html](http://docs.gunicorn.org/en/develop/configure.html).

### Heuristics

You can enable a variety of heuristics / branch prediction via the settings.py file.  The `nearby` heuristic caches all tiles at the same level within the radius distance (distance 1 --> 3*3 tiles, distance 2 = 25 tiles, distance 3 = 25 tiles).  The `up` heuristic caches all tiles parent to a requested tile.  The `down` heuristic caches tiles that are `children` to the requested tile within the depth and minZoom/maxZoom range.  For instance, if you request a tile at 14 and have a depth of 2, all the children tiles from 14 to 16 will be requested.

```
TILEJET = {
    'name': 'TileJet Server',
    'cache': {
        'memory': {
            'enabled': True,
            'size': 1000,
            'minZoom': 0,
            'maxZoom': 14
        }
    },
    'heuristic': {
        'down': {
            'enabled': True,
            'depth': 1,
            'minZoom': 0,
            'maxZoom': 18
        },
        'up': {
            'enabled': True
        },
        'nearby': {
            'enabled': True,
            'radius': 2
        }
    }
}
```

## Contributing

TBD

## License

### Latest Code

Copyright (c) 2015, Patrick Dufour
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of tilejet-server nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

### Previous Code

All commits on and before October 2, 2015 are considered government work and are entirely in the public domain.  That code is preserved under the USG branch at [https://github.com/tilejet/tilejet-server/commits/usg](https://github.com/tilejet/tilejet-server/commits/usg).
