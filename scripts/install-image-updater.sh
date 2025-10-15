#!/bin/bash

echo "🚀 Installing ArgoCD Image Updater..."

# 1. Helm repository 추가 및 업데이트
echo "📦 Adding Argo Helm repository..."
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update

# 2. ArgoCD Image Updater 설치
echo "⚙️ Installing ArgoCD Image Updater..."
helm install argocd-image-updater argo/argocd-image-updater \
  --namespace argocd \
  --set config.argocd.serverAddress="argocd-server.argocd.svc.cluster.local:443" \
  --set config.log.level=info \
  --create-namespace

# 3. 설치 상태 확인
echo "✅ Checking installation status..."
kubectl get pods -n argocd -l app.kubernetes.io/name=argocd-image-updater

echo ""
echo "🎉 ArgoCD Image Updater installation completed!"
echo ""
echo "📋 Next steps:"
echo "1. Create Git credentials:"
echo "   kubectl -n argocd create secret generic git-credentials \\"
echo "     --from-literal=username=<GITHUB_USERNAME> \\"
echo "     --from-literal=password=<GITHUB_TOKEN>"
echo ""
echo "2. Create Docker registry credentials:"
echo "   kubectl -n argocd create secret docker-registry docker-creds \\"
echo "     --docker-server=docker.io \\"
echo "     --docker-username=<DOCKER_USERNAME> \\"
echo "     --docker-password=<DOCKER_PASSWORD> \\"
echo "     --docker-email=<EMAIL>"
echo ""
echo "3. Check Image Updater logs:"
echo "   kubectl logs -n argocd -l app.kubernetes.io/name=argocd-image-updater"
