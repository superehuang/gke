#!/bin/bash


python3 etc/create_gke_infra_manifests.py

terraform init 
terraform apply -auto-approve 

gcloud container clusters get-credentials $(terraform output -raw kubernetes_cluster_name) --region $(terraform output -raw region)
kubectl create clusterrolebinding cluster-admin-binding  --clusterrole cluster-admin  --user $(gcloud config get-value account)
STATIC_MANIFEST_DIR=etc/output
kubectl apply -f "$STATIC_MANIFEST_DIR/crds.yaml"
kubectl wait --for=condition=Established -f "$STATIC_MANIFEST_DIR/crds.yaml"
kubectl apply -f "$STATIC_MANIFEST_DIR/olm.yaml"

while [[ $(kubectl get csv/packageserver -n olm -o 'jsonpath={..status.conditions[?(@.phase=="Succeeded")].phase}') != *"Succeeded"* ]]; do
    echo "waiting for OLM packageserver to be ready."
    sleep 5
done
kubectl rollout status -w deployment/packageserver --namespace=olm
kubectl apply -f "$STATIC_MANIFEST_DIR/infra-subscription.yaml"

while ! kubectl get crd/cbinfras.cloudbridge.business.facebook.com >/dev/null 2>&1; do
    echo "waiting for creating crd/cbinfras.cloudbridge.business.facebook.com."
    sleep 5

done
MANIFEST_DIR=etc/output
kubectl wait --for=condition=Established crd/cbinfras.cloudbridge.business.facebook.com
kubectl rollout status -w deployment/infra-operator-controller-manager --namespace=infra
kubectl apply -f "$MANIFEST_DIR/hub-subscription.yaml"
while ! kubectl get crd/hubs.cloudbridge.business.facebook.com >/dev/null 2>&1; do
    echo "waiting for creating crd/hubs.cloudbridge.business.facebook.com."
    sleep 5
done

kubectl wait --for=condition=Established crd/hubs.cloudbridge.business.facebook.com
kubectl rollout status -w deployment/hub-operator-controller-manager --namespace=cloudbridge

kubectl apply -f "$MANIFEST_DIR/capig-subscription.yaml"
while ! kubectl get crd/capigs.cloudbridge.business.facebook.com >/dev/null 2>&1; do
    echo "waiting for creating crd/capigs.cloudbridge.business.facebook.com."
    sleep 5
done

kubectl wait --for=condition=Established crd/capigs.cloudbridge.business.facebook.com
kubectl rollout status -w deployment/capig-operator-controller-manager --namespace=capig


kubectl apply -f "$MANIFEST_DIR/cluster-type.yaml"
kubectl apply -f "$MANIFEST_DIR/infra-instance.yaml"
while [[ $(kubectl get deployment.apps/hub -o 'jsonpath={.status.conditions[?(@.type=="Available")].status}') != "True" ]]; do
    echo "waiting for hub to be ready."
    sleep 5
done


while [[ $(kubectl get deployment.apps/capig -o 'jsonpath={.status.conditions[?(@.type=="Available")].status}') != "True" ]]; do
    echo "waiting for capig to be ready."
    sleep 5
done

sleep 60
external_ip=$(kubectl get svc/infra-ingressnginx-controller -o 'jsonpath={.status.loadBalancer.ingress[0].ip}')

echo 'Please Add A record: ' $external_ip, " to your domain"



