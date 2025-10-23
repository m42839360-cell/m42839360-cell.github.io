# Roboblog Helm Chart

A Helm chart for deploying the Roboblog Jekyll-based blog on Kubernetes with automated builds.

## Architecture

This chart deploys:

1. **PersistentVolumeClaim**: Shared storage for the built `_site` directory
2. **CronJob**: Periodically builds the Jekyll site and writes to shared volume
3. **Deployment**: Runs nginx pods serving static files from the shared volume
4. **Service**: Exposes the nginx web server
5. **Ingress** (optional): Provides external access to the blog

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- Docker image built from the repository Dockerfile
- PersistentVolume provisioner support in the underlying infrastructure

## Building the Docker Image

Before installing the chart, build and push the Docker image:

```bash
# Build the image
docker build -t roboblog:latest .

# Tag for your registry (example)
docker tag roboblog:latest your-registry/roboblog:latest

# Push to registry
docker push your-registry/roboblog:latest
```

## Installing the Chart

```bash
# Install with default values
helm install my-roboblog ./roboblog-chart

# Install with custom values
helm install my-roboblog ./roboblog-chart \
  --set image.repository=your-registry/roboblog \
  --set image.tag=latest

# Install with custom values file
helm install my-roboblog ./roboblog-chart -f custom-values.yaml
```

## Uninstalling the Chart

```bash
helm uninstall my-roboblog
```

## Configuration

The following table lists the configurable parameters and their default values.

| Parameter | Description | Default |
|-----------|-------------|---------|
| `image.repository` | Docker image repository | `roboblog` |
| `image.tag` | Docker image tag | `latest` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |
| `persistence.enabled` | Enable persistence | `true` |
| `persistence.size` | PVC size | `1Gi` |
| `persistence.storageClass` | Storage class | `""` |
| `cronjob.enabled` | Enable CronJob | `true` |
| `cronjob.schedule` | CronJob schedule | `"0 * * * *"` (hourly) |
| `nginx.replicaCount` | Number of nginx replicas | `2` |
| `nginx.image.repository` | Nginx image | `nginx` |
| `nginx.image.tag` | Nginx image tag | `1.25-alpine` |
| `service.type` | Service type | `ClusterIP` |
| `service.port` | Service port | `80` |
| `ingress.enabled` | Enable ingress | `false` |
| `ingress.className` | Ingress class | `""` |
| `ingress.hosts` | Ingress hosts | `[{host: roboblog.example.com}]` |

## Examples

### Enable Ingress with TLS

```yaml
# custom-values.yaml
ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: blog.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: blog-tls
      hosts:
        - blog.example.com
```

```bash
helm install my-roboblog ./roboblog-chart -f custom-values.yaml
```

### Change Build Schedule

Build every 6 hours:

```bash
helm install my-roboblog ./roboblog-chart \
  --set cronjob.schedule="0 */6 * * *"
```

### Use LoadBalancer Service

```bash
helm install my-roboblog ./roboblog-chart \
  --set service.type=LoadBalancer
```

### Manual Build Trigger

To trigger a build immediately without waiting for the CronJob:

```bash
kubectl create job --from=cronjob/my-roboblog-builder my-roboblog-manual-build
```

## Monitoring

### Check Build Status

```bash
# View CronJob
kubectl get cronjob

# View recent jobs
kubectl get jobs

# View build logs
kubectl logs -l app.kubernetes.io/component=builder
```

### Check Website Status

```bash
# View deployment
kubectl get deployment

# View pods
kubectl get pods

# View service
kubectl get svc

# Port forward to access locally
kubectl port-forward svc/my-roboblog 8080:80
# Then visit http://localhost:8080
```

### Check Storage

```bash
# View PVC
kubectl get pvc

# View PV
kubectl get pv
```

## Troubleshooting

### Site Not Loading

1. Check if the initial build has completed:
   ```bash
   kubectl get jobs
   ```

2. Trigger a manual build if needed:
   ```bash
   kubectl create job --from=cronjob/my-roboblog-builder manual-build
   ```

3. Check build logs for errors:
   ```bash
   kubectl logs -l app.kubernetes.io/component=builder
   ```

### Build Failures

Check the CronJob logs:
```bash
kubectl describe cronjob my-roboblog-builder
kubectl logs -l app.kubernetes.io/component=builder --tail=50
```

### Storage Issues

Check PVC status:
```bash
kubectl describe pvc my-roboblog-site
```

## Upgrading

```bash
helm upgrade my-roboblog ./roboblog-chart
```

## License

Same as the parent project.
