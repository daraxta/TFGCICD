#!/bin/bash
kubectl --namespace tekton-pipelines port-forward svc/tekton-dashboard 8082:9097 --address 0.0.0.0 &>/dev/null &
kubectl --namespace argocd port-forward svc/argocd-server 8081:80 --address 0.0.0.0 &>/dev/null &
kubectl port-forward svc/el-github-pr 9000:8080 &>/dev/null &
ngrok http 9000
