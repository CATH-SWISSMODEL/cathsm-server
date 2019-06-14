
# https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-centos-7

sudo yum install python36 git redis nginx

sudo systemctl start redis
sudo systemctl enable redis

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



# run tests
cd $APPDIR/cathapi
pytest


sudo cp $APPDIR/deploy/etc/systemd/system/gunicorn.service /etc/systemd/system/

sudo systemctl start gunicorn
sudo systemctl enable gunicorn
