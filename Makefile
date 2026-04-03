# Pin versions in docs/VERSION-PINS.md; bump intentionally before course dates.
CLUSTER_NAME ?= aire-prep
NS ?= aire-prep
KIND_CONFIG ?= cluster/kind-config.yaml

.PHONY: cluster-up cluster-down install-metrics-server install-ingress install-cert-manager \
	install-prometheus install-otel-jaeger apply-apps build-fake-llm load-fake-llm argocd-install help

help:
	@echo "Targets: cluster-up cluster-down install-* apply-apps argocd-install"

cluster-up:
	kind create cluster --config $(KIND_CONFIG)
	kubectl config use-context kind-$(CLUSTER_NAME)
	kubectl create namespace $(NS) --dry-run=client -o yaml | kubectl apply -f -
	@echo "Cluster ready. Context: kind-$(CLUSTER_NAME)"

cluster-down:
	kind delete cluster --name $(CLUSTER_NAME)

install-metrics-server:
	kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
	kubectl rollout status deployment/metrics-server -n kube-system --timeout=120s
	# kind: kubelet certs do not include node IP SANs; without this, scraping fails with x509 errors.
	kubectl patch deployment metrics-server -n kube-system --type='json' \
		-p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'
	kubectl rollout status deployment/metrics-server -n kube-system --timeout=120s
	@echo "Verify: kubectl top nodes"

# ingress-nginx — version pinned via Helm repo
install-ingress:
	helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
	helm repo update
	helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
		-n ingress-nginx --create-namespace \
		-f helm/ingress-nginx-values.yaml \
		--wait --timeout 5m

install-cert-manager:
	helm repo add jetstack https://charts.jetstack.io
	helm repo update
	helm upgrade --install cert-manager jetstack/cert-manager \
		-n cert-manager --create-namespace \
		--set installCRDs=true \
		--wait --timeout 5m

install-prometheus:
	helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
	helm repo update
	helm upgrade --install kube-prometheus prometheus-community/kube-prometheus-stack \
		-n monitoring --create-namespace \
		-f helm/kube-prometheus-values.yaml \
		--wait --timeout 15m

install-otel-jaeger:
	kubectl apply -k manifests/observability/

build-fake-llm:
	docker build -t fake-llm:prep apps/fake-llm

load-fake-llm: build-fake-llm
	kind load docker-image fake-llm:prep --name $(CLUSTER_NAME)

apply-apps: load-fake-llm
	kubectl apply -k manifests/apps/

argocd-install:
	@echo "See docs/ARGOCD.md — run documented helm install, then kubectl apply -k gitops/argocd/applications/"
