#!/bin/bash

. /kb/deployment/user-env.sh

python ./scripts/prepare_deploy_cfg.py ./deploy.cfg ./work/config.properties

if [ -f ./work/token ] ; then
  export KB_AUTH_TOKEN=$(<./work/token)
fi

if [ $# -eq 0 ] ; then
  sh ./scripts/start_server.sh
elif [ "${1}" = "test" ] ; then
  echo "Run Tests"
  make test
elif [ "${1}" = "async" ] ; then
  sh ./scripts/run_async.sh
elif [ "${1}" = "init" ] ; then
  echo "Initialize module"
  mkdir -p /data/metaphlan2
  cd /data/metaphlan2

  echo "downloading https://bitbucket.org/biobakery/metaphlan2/downloads/mpa_v20_m200_marker_info.txt.bz2"
  if [ -s "/data/metaphlan2/mpa_v20_m200_marker_info.txt" ];
  then
    echo "mpa_v20_m200_marker_info exists"
  else
    wget -c https://bitbucket.org/biobakery/metaphlan2/downloads/mpa_v20_m200_marker_info.txt.bz2
    bzip2 -d mpa_v20_m200_marker_info.txt.bz2
  fi
  if [ -s "/data/metaphlan2/mpa_v20_m200_marker_info.txt" ] ; then
    echo "DATA DOWNLOADED SUCCESSFULLY"
    touch /data/__READY__
  else
    echo "Init failed"
  fi

elif [ "${1}" = "bash" ] ; then
  bash
elif [ "${1}" = "report" ] ; then
  export KB_SDK_COMPILE_REPORT_FILE=./work/compile_report.json
  make compile
else
  echo Unknown
fi
