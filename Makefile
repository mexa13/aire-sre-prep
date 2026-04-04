# Pin versions in docs/VERSION-PINS.md; bump intentionally before course dates.
CLUSTER_NAME ?= aire-prep
NS ?= aire-prep
KIND_CONFIG ?= cluster/kind-config.yaml

.PHONY: cluster-up cluster-down install-platform bootstrap-lab \
	install-metrics-server install-ingress install-cert-manager \
	install-prometheus install-otel-jaeger install-argocd apply-argocd-apps \
	apply-apps build-fake-llm load-fake-llm argocd-install help

help:
	@echo "Targets: cluster-up cluster-down install-platform bootstrap-lab install-* install-argocd apply-apps"

cluster-up:
	kind create cluster --config $(KIND_CONFIG)
	kubectl config use-context kind-$(CLUSTER_NAME)
	kubectl create namespace $(NS) --dry-run=client -o yaml | kubectl apply -f -
	@echo "Cluster ready. Context: kind-$(CLUSTER_NAME)"

cluster-down:
	kind delete cluster --name $(CLUSTER_NAME)

# Everything except Argo and sample apps (correct order). Use after a fresh `cluster-up`.
install-platform:
	$(MAKE) install-metrics-server
	$(MAKE) install-ingress
	$(MAKE) install-cert-manager
	$(MAKE) install-prometheus
	$(MAKE) install-otel-jaeger

# Full lab stack on an empty cluster: platform + whoami/fake-llm. Argo: run install-argocd + apply-argocd-apps separately.
bootstrap-lab:
	$(MAKE) install-platform
	$(MAKE) apply-apps
	@echo "Done. Optional GitOps: make install-argocd && make apply-argocd-apps"

install-metrics-server:
	kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
	@# kind + upstream v0.8.x: without --kubelet-insecure-tls, kubelet scraping fails (x509 / no metrics).
	@# Do NOT wait for Ready before patching — the deployment may not become Available until scraping works.
	@n=0; until kubectl get deployment metrics-server -n kube-system >/dev/null 2>&1; do \
	  n=$$((n+1)); test $$n -le 60 || (echo "timeout waiting for metrics-server Deployment"; exit 1); \
	  sleep 1; \
	done
	@if kubectl get deployment metrics-server -n kube-system -o jsonpath='{.spec.template.spec.containers[0].args}' 2>/dev/null | grep -q kubelet-insecure-tls; then \
	  echo "metrics-server already patched for kind"; \
	else \
	  kubectl patch deployment metrics-server -n kube-system --type='json' \
	    -p='[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'; \
	fi
	kubectl rollout status deployment/metrics-server -n kube-system --timeout=180s
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

# Optional GitOps — same pattern as other Helm installs. Docs: UI login, repo URL in Application YAMLs.
install-argocd:
	helm repo add argo https://argoproj.github.io/argo-helm
	helm repo update
	helm upgrade --install argocd argo/argo-cd \
		-n argocd --create-namespace \
		-f helm/argocd-values.yaml \
		--wait --timeout 10m
	@echo "Admin password: kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d; echo"
	@echo "UI: kubectl port-forward svc/argocd-server -n argocd 8080:443  → https://localhost:8080 (user: admin)"

# Apply Argo Applications (edit repoURL in gitops/argocd/applications/*.yaml first; ensure fake-llm image is loaded).
apply-argocd-apps:
	kubectl apply -f gitops/argocd/applications/

# Backward-compatible alias
argocd-install: install-argocd
