#!/bin/bash
#
# Usage:
#   $ sudo deploy.sh <action> <release>
#
# action:  { init | update }
# release: { dev | staging | prod }

CATHPY_LATEST_TAG="0.0.1"
CATHAPI_LATEST_TAG="0.0.1"

CATHPY_SOURCE="https://github.com/UCL/cathpy.git"
CATHPY_TAG=${CATHPY_TAG:-$CATHPY_LATEST_TAG}

CATHAPI_SOURCE="https://github.com/CATH-SWISSMODEL/cath-swissmodel-api.git"

HTTP_BASE=/etc/httpd
VHOSTS_BASE=/var/www/vhosts/
DEBUG_FLAG=0

if [[ $# -eq 0 ]]; then
    echo "usage: $0 <action> <release>"
    exit 0
fi

ACTION="$1"
RELEASE="$2"

case "$RELEASE" in
    dev)
        CATHAPI_TAG=${CATHAPI_TAG:-"HEAD"}
        ;;
    staging)
        CATHAPI_TAG=${CATHAPI_TAG:-$CATHAPI_LATEST_TAG}
        ;;
    prod)
        CATHAPI_TAG=${CATHAPI_TAG:-$CATHAPI_LATEST_TAG}
        ;;
    *)
        echo "unknown release type: $RELEASE (expected < dev | staging | prod >)"
        exit 1
esac

BASEDIR=$VHOSTS_BASE/cathapi-${RELEASE}
USER=$(who am i)

CATHPY_DIR=$BASEDIR/cathpy
CATHAPI_DIR=$BASEDIR/cath-swissmodel-api

echo "# USER           $USER"
echo "# ACTION         $ACTION"
echo "# RELEASE        $RELEASE"
echo "# BASEDIR        $BASEDIR"
echo "# CATHPY_SOURCE  $CATHPY_SOURCE"
echo "# CATHPY_TAG     $CATHPY_TAG"
echo "# CATHPY_DIR     $CATHPY_DIR"
echo "# CATHAPI_SOURCE $CATHAPI_SOURCE"
echo "# CATHAPI_TAG    $CATHAPI_TAG"
echo "# CATHAPI_DIR    $CATHAPI_DIR"

update_code() {
    echo "Updating CATHAPI code [tag: $CATHAPI_TAG] from $GIT_SOURCE ..."
    (set -x; git clone --branch $CATHAPI_TAG $CATHAPI_SOURCE $CATHAPI_DIR)
    echo "  ... done"
    echo 

    echo "Updating CATHPY code [tag: $CATHPY_TAG] from $CATHPY_SOURCE ..."
    (set -x; git clone --branch $CATHPY_TAG $CATHPY_SOURCE $CATHPY_DIR)
    echo "  ... done"
    echo 
}

update_web() {
    echo "Updating web config (requires sudo) ... "
    (set -x; sudo rsync -av $CATHAPI_DIR/deploy/httpd/ $HTTP_BASE/)
    echo "  ... done"
    echo
}

update() {
    update_code()
    update_web()

    echo "Restarting httpd (requires sudo) ... "
    (set -x; sudo systemctl restart httpd)
    echo "  ... done"
    echo
}

# do one-off stuff
init() {

    echo "Making sure app dir '$BASEDIR' exists and is owned by $USER ... (requires sudo)"
    (set -x; sudo mkdir -p $BASEDIR && chown -R $USER:users $BASEDIR)
    echo "  ... done"
    echo 

    update_code()
    update_web()

    echo "Setting up httpd service (requires sudo) ... "
    (set -x; sudo systemctl enable httpd && systemctl start httpd)
    echo "  ... done"
    echo

    # generate secret key
    echo "Generating Django secret key ... " 
    DJANGO_SECRET_KEY=`openssl rand -base64 48`
    if [ $? -ne 0 ]; then
        echo "Error creating secret key."
        exit 3
    fi
    echo $DJANGO_SECRET_KEY > $APPDIR/cathapi/secret_key.txt
    echo "  ... done"
    echo


}

case "$ACTION" in
    init)
        echo "Initialising deployment ..."
        init()
        ;;
    update)
        echo "Updating existing deployment ..."
        update()
        ;;
    info)
        ;;
    *)
        echo "Error: unknown action '$ACTION'"
        exit 2
        ;;
esac

echo "DONE"
