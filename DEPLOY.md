
## Docker environment

Remove any system docker software (if installed):

```sh
sudo yum remove docker docker-compose docker-common
```

Install latest `docker`:

```sh
# https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-centos-7
curl -fsSL https://get.docker.com/ | sh
sudo systemctl start docker
sudo systemctl enable docker
```

Install latest `docker-compose`:

```sh
# https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-compose-on-centos-7
sudo curl -L "https://github.com/docker/compose/releases/download/1.23.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

Get the `cathsm-server` code:

```sh
CATHSM_BRANCH=v0.0.1
CATHSM_ENV=production
sudo mkdir cathsm-server-${CATHSM_ENV}
sudo chown ucbcisi:users cathsm-server-${CATHSM_ENV}
git clone --branch=${CATHSM_BRANCH} https://github.com/CATH-SWISSMODEL/cathsm-server.git cathsm-server-${CATHSM_ENV}
```

Build `docker-compose`:

```sh
cd cathsm-server-${CATHSM_ENV}
cp .env.example .env
vim .env
sudo docker-compose -f docker-compose.yml build
```

Run `docker-compose`:

```sh
cd cathsm-server-${CATHSM_ENV}
sudo docker-compose -f docker-compose.yml run
```

## Post install

* Add Django group `API User` with the following permissions:

```
admin | log entry | Can view log entry  
auth | group | Can view group  
auth | permission | Can view permission  
auth | user | Can view user  
authtoken | Token | Can add Token  
authtoken | Token | Can change Token  
authtoken | Token | Can delete Token  
authtoken | Token | Can view Token  
contenttypes | content type | Can view content type  
select_template_api | select template alignment | Can add select template alignment  
select_template_api | select template alignment | Can change select template alignment  
select_template_api | select template alignment | Can delete select template alignment  
select_template_api | select template alignment | Can view select template alignment  
select_template_api | select template hit | Can add select template hit  
select_template_api | select template hit | Can change select template hit  
select_template_api | select template hit | Can delete select template hit  
select_template_api | select template hit | Can view select template hit  
select_template_api | select template task | Can add select template task  
select_template_api | select template task | Can change select template task  
select_template_api | select template task | Can delete select template task  
select_template_api | select template task | Can view select template task  
sessions | session | Can add session  
sessions | session | Can change session  
sessions | session | Can delete session  
sessions | session | Can view session
```

* Add Django users for general functionality:
  * `apitest` - see `cathsm-client/tests/api1_test.py`
  * `apiuser` - see `cathsm-server/frontend/src/components/WorkFlow.js`

## Manual deployment

The following steps are now deprecated (since the deployment has been moved to `docker-compose`), however
the notes are being left here for reference.

```sh
# https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-centos-7

sudo yum install python36 git redis nginx postgresql  postgresql-contrib postgresql-devel

sudo systemctl start redis postgresql nginx
sudo systemctl enable redis postgresql nginx

APPDIR=/opt/cath-swissmodel-api
#SRCDIR=$APPDIR
SRCDIR=/cath/homes2/ucbcisi/git/cath-swissmodel-api

sudo mkdir -p $APPDIR
sudo chown ucbcisi:users $APPDIR
git clone https://github.com/CATH-SWISSMODEL/cath-swissmodel-api.git $APPDIR

cd $APPDIR/cathapi
python3 -m venv venv
. venv/bin/activate
pip install --upgrade pip
pip install -r requirements-to-freeze.txt

# django requires sqlite3 >= v3.8 (CentOS 7 is currently 3.7)
# https://stackoverflow.com/questions/55485858/using-sqlite3-with-django-2-2-and-python-3-6-7-on-centos7
wget http://www6.atomicorp.com/channels/atomic/centos/7/x86_64/RPMS/atomic-sqlite-sqlite-3.8.5-3.el7.art.x86_64.rpm
sudo yum localinstall atomic-sqlite-sqlite-3.8.5-3.el7.art.x86_64.rpm
sudo mv /lib64/libsqlite3.so.0.8.6{,-3.17}
sudo cp /opt/atomic/atomic-sqlite/root/usr/lib64/libsqlite3.so.0.8.6 /lib64

# install apps
# mafft
sudo rpm -Uvh ~/git/cath-swissmodel-api/deploy/files/mafft-7.427-gcc_fc6.x86_64.rpm
# blast
sudo yum install perl-Archive-Tar perl-Digest-MD5 perl-List-MoreUtils
sudo rpm -Uvh ~/git/cath-swissmodel-api/deploy/files/ncbi-blast-2.9.0+-1.x86_64.rpm
# cath-tools
sudo cp ~/git/cath-swissmodel-api/deploy/files/cath-tools-v0.16.2/* /usr/bin

# setup django
cd $APPDIR/cathapi
./manage.py makemigrations
./manage.py migrate
./manage.py createsuperuser
./manage.py collectstatic

# setup celery worker
# users/groups/dir
sudo useradd -N -M --system -s /bin/bash celery
sudo groupadd celery
sudo usermod -a -G celery celery
sudo mkdir /opt/celery
sudo chown celery:celery /opt/celery

sudo mkdir /var/{log,run}/celery
sudo chown celery:celery /var/{log,run}/celery

# daemon
sudo cp $SRCDIR/deploy/etc/conf.d/celery /etc/conf.d/
sudo cp $SRCDIR/deploy/etc/systemd/system/celery /etc/systemd/system/
sudo systemctl daemon-reload


# setup nginx
sudo cp $SRCDIR/deploy/etc/nginx/nginx.conf /etc/nginx/

# http://docs.gunicorn.org/en/stable/deploy.html


sudo semanage permissive -a httpd_t


# run tests
cd $APPDIR/cathapi
pytest


sudo cp $APPDIR/deploy/etc/systemd/system/gunicorn.service /etc/systemd/system/

sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```
