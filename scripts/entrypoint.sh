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

  echo "downloading https://edge-dl.lanl.gov/EDGE/dev/edge_dev_metaphlan2DB.tgz"

  if [ -s "/data/metaphlan2/mpa_v20_m200.pkl" ];
  then
    echo "mpa_v20_m200.1.pkl exists"
  else
    wget -q https://edge-dl.lanl.gov/EDGE/dev/edge_dev_metaphlan2DB.tgz
    tar -xvf edge_dev_metaphlan2DB.tgz
    cp -r database/metaphlan2/ /data/metaphlan2/
    rm -r database/
  fi

  if [ -s "/data/metaphlan2/mpa_v20_m200_marker_info.txt" -a -s "/data/metaphlan2/mpa_v20_m200.pkl" -a -s "/data/metaphlan2/mpa_v20_m200.1.bt2" ] ; then
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
