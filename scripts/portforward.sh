#!/bin/bash

while true; do

    lsof -i:9090 && port=1 || port=0
    
    if [ $port -eq 0 ]; then
    
        kubectl port-forward service/pythonapp -n argocd 9090:5000 --address 0.0.0.0

    else
        echo 'Recargando'
    fi

done
