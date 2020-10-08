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
  mkdir -p /data/mpa_latest
  cd /data
  echo "downloading https://edge-dl.lanl.gov/EDGE/dev/edge_dev_metaphlan3DB.tgz"

  if [ -s "/data/mpa_latest/mpa_v30_CHOCOPhlAn_201901.pkl" ];
  then
    echo "mpa_v20_m200.1.pkl exists"
  else
    wget -q https://edge-dl.lanl.gov/EDGE/dev/edge_dev_metaphlan3DB.tgz
    tar -xvf edge_dev_metaphlan3DB.tgz
#    echo "copying to /data"
#    cp -r database/mpa_latest/ /data/

    chmod -R 777 /data/
    echo "ls /data/metaphlan3"
    ls -la /data/mpa_latest
    echo "removing database/ and edge_dev_metaphlan3DB.tgz"
#    rm -r database/
    rm edge_dev_metaphlan3DB.tgz
  fi

  if [ -s "/data/mpa_latest/mpa_v30_CHOCOPhlAn_201901.1.bt2" -a -s "/data/mpa_latest/mpa_v30_CHOCOPhlAn_201901.rev.1.bt2" -a -s "/data/mpa_latest/mpa_v30_CHOCOPhlAn_201901.rev.2.bt2"  -a -s "/data/mpa_latest/mpa_v30_CHOCOPhlAn_201901.pkl" ] ; then
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
