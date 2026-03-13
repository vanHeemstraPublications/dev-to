---
title: "Welcome to Container Harbour! 🚢 Ep.8"
published: false
description: "Episode 8: Sealed Cargo Manifests — ConfigMaps and Secrets. Because writing your database password in your Docker image is absolutely something that has happened and we must never speak of it again."
tags: [kubernetes, beginners, devops, tutorial]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/welcome-to-container-harbour-episode-08.png"
series: "Welcome to Container Harbour!"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 8: Sealed Cargo Manifests — ConfigMaps and Secrets 🔐

### The Incident That Shall Not Be Named (But I'm Going to Name It) 😬

A junior developer — not me, definitely not me, I was definitely not 24 years old at the time — hardcoded a database password into a Docker image. And pushed that Docker image to a PUBLIC container registry.

The password was `admin123`. On a PRODUCTION database.

The database was exposed to the internet.

I'm not saying what happened next. I'm saying that particular company now has a very thorough secrets management policy. And a new database. And new passwords. And possibly new management.

THIS is why ConfigMaps and Secrets exist. Let me show you how to do it properly. 🎯

---

## The SIPOC of Configuration 🗂️

| | | Detail |
|---|---|---|
| **Supplier** | Who creates config and secrets? | Platform teams, CI/CD pipelines, Vault, External Secrets Operator |
| **Input** | What goes in? | Key-value pairs, files, connection strings, passwords, certificates |
| **Process** | What happens? | Kubernetes stores them, Pods mount or reference them at runtime |
| **Output** | What comes out? | Apps get their config without baking it into the image |
| **Consumer** | Who uses the config? | Pods — as environment variables or mounted files |

---

## The Golden Rule: Keep Config OUT of Images 📦

Your Docker image should contain **code**. Not **configuration**. Never **secrets**.

Why? Because:

1. **Images travel.** They get pushed to registries. Maybe public ones.
2. **Images are immutable.** Want to change a setting? Rebuild the whole image? Every time? Really?
3. **Images are layered.** Even if you delete a secret in a later layer, it's still in the earlier layer. In history. Forever.

The harbour rule: the freight container carries the **goods**. The shipping manifest (separate document, sealed) carries the **instructions and access codes**. Not mixed together.

```
❌ WRONG:                        ✅ RIGHT:
                                 
Dockerfile:                      Dockerfile:
  ENV DB_PASSWORD=admin123         # No passwords here!
  COPY app .                       COPY app .
  CMD python app.py                CMD python app.py
                                 
  "Password is IN the image"     ConfigMap: DB_HOST=db.internal
  "Image is on Docker Hub"       Secret: DB_PASSWORD=<encrypted>
  "Everyone can pull it"         "Config is separate, secret is encrypted"
  "Oh no."                       "Image is clean and shareable" ✅
```

---

## ConfigMaps: The Unsealed Cargo Manifest 📋

ConfigMaps hold **non-sensitive** configuration. Things you don't mind people seeing:

- Database hostnames
- Feature flags
- Log levels
- API URLs
- Application settings

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: web-app-config
  namespace: production
data:
  # Simple key-value pairs
  LOG_LEVEL: "info"
  API_URL: "https://api.harbour.io/v2"
  DB_HOST: "postgres.production.svc.cluster.local"
  DB_PORT: "5432"
  DB_NAME: "harbour_db"
  MAX_CONNECTIONS: "100"
  FEATURE_NEW_UI: "true"

  # You can even store entire config files!
  nginx.conf: |
    server {
      listen 80;
      location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
      }
    }

  app-config.json: |
    {
      "environment": "production",
      "logLevel": "info",
      "apiTimeout": 30,
      "retryCount": 3
    }
```

```bash
kubectl apply -f configmap.yaml

# See it
kubectl get configmaps
kubectl describe configmap web-app-config

# Or the short way
kubectl get cm web-app-config -o yaml
```

---

## Using ConfigMaps: Two Ways to Inject Config 💉

### Method 1: Environment Variables

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-app
  template:
    metadata:
      labels:
        app: web-app
    spec:
      containers:
      - name: web-app
        image: my-app:latest

        env:
        # Inject a specific key from ConfigMap
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: web-app-config
              key: LOG_LEVEL

        - name: DATABASE_HOST
          valueFrom:
            configMapKeyRef:
              name: web-app-config
              key: DB_HOST

        # OR: inject ALL keys from ConfigMap as env vars at once
        envFrom:
        - configMapRef:
            name: web-app-config
            # This gives your container: LOG_LEVEL, API_URL, DB_HOST, etc.
```

### Method 2: Mounted as Files (great for config files!)

```yaml
spec:
  containers:
  - name: web-app
    image: my-app:latest
    volumeMounts:
    - name: config-volume
      mountPath: /etc/config          # ConfigMap files appear here
    - name: nginx-config
      mountPath: /etc/nginx/nginx.conf
      subPath: nginx.conf             # Mount a specific key as a specific file

  volumes:
  - name: config-volume
    configMap:
      name: web-app-config            # All keys become files in /etc/config/
  - name: nginx-config
    configMap:
      name: web-app-config
      items:
      - key: nginx.conf               # Only mount this specific key
        path: nginx.conf
```

```bash
# Verify your app got the config:
kubectl exec -it web-app-abc123 -- env | grep LOG_LEVEL
# LOG_LEVEL=info

kubectl exec -it web-app-abc123 -- cat /etc/config/app-config.json
# {"environment": "production", "logLevel": "info", ...}
```

---

## Secrets: The SEALED Cargo Manifest 🔐

Secrets work exactly like ConfigMaps but for **sensitive data**:

- Database passwords
- API keys
- TLS certificates
- OAuth tokens
- Anything that makes your security team nervous

```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: web-app-secrets
  namespace: production
type: Opaque
data:
  # Values MUST be base64 encoded
  DB_PASSWORD: cGFzc3dvcmQxMjM=          # "password123" in base64
  API_KEY: c3VwZXJzZWNyZXRhcGlrZXk=      # "supersecretapikey" in base64
  JWT_SECRET: bXlqd3RzZWNyZXQ=           # "myjwtsecret" in base64

# OR use stringData (plain text -- Kubernetes encodes it automatically)
stringData:
  DB_PASSWORD: "password123"              # Kubernetes converts to base64 for you
  API_KEY: "supersecretapikey"
```

```bash
# Generate base64 values yourself:
echo -n "password123" | base64
# cGFzc3dvcmQxMjM=

echo -n "cGFzc3dvcmQxMjM=" | base64 --decode
# password123

# Apply the secret
kubectl apply -f secret.yaml

# See it (values are base64 encoded, not shown in plain text)
kubectl get secret web-app-secrets -o yaml
# data:
#   DB_PASSWORD: cGFzc3dvcmQxMjM=   <- encoded, not visible as plaintext
#   API_KEY: c3VwZXJzZWNyZXRhcGlrZXk=

# Decode a specific value:
kubectl get secret web-app-secrets -o jsonpath='{.data.DB_PASSWORD}' | base64 --decode
# password123
```

---

## Using Secrets in Pods: Same Pattern as ConfigMaps 💉

```yaml
spec:
  containers:
  - name: web-app
    image: my-app:latest

    env:
    # Inject specific secret values as env vars
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: web-app-secrets
          key: DB_PASSWORD

    - name: API_KEY
      valueFrom:
        secretKeyRef:
          name: web-app-secrets
          key: API_KEY

    # Mount TLS certificates as files:
    volumeMounts:
    - name: tls-certs
      mountPath: /etc/ssl/app
      readOnly: true

  volumes:
  - name: tls-certs
    secret:
      secretName: app-tls-secret      # Created by cert-manager (Episode 7!)
```

```bash
# Verify a secret is available inside the Pod (never log it in production!)
kubectl exec -it web-app-abc123 -- sh -c 'echo "DB_PASSWORD length: ${#DB_PASSWORD}"'
# DB_PASSWORD length: 11
# (We checked the length without printing the actual value. Smart.) 🧠
```

---

## The Dark Truth About Kubernetes Secrets 😬

I need to be honest with you. Kubernetes Secrets are **base64 encoded, not encrypted** by default.

Base64 is NOT encryption. It's encoding. Anyone with access to etcd — or anyone who can run `kubectl get secret` — can decode your secrets trivially.

```bash
# This is all it takes to decode a "secret":
echo "cGFzc3dvcmQxMjM=" | base64 --decode
# password123
```

So what DO Kubernetes Secrets give you?

1. **Separation** — credentials are not baked into images or code
2. **RBAC control** — you can restrict who can `get` Secrets (Episode 10!)
3. **Encryption at rest** — if you configure it (see below)
4. **Integration** — standard mounting and env injection pattern

For proper secret encryption, you have options:

### Option 1: Encryption at Rest (built into Kubernetes)

```yaml
# encryption-config.yaml (applied to the API Server)
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
- resources:
  - secrets
  providers:
  - aescbc:
      keys:
      - name: key1
        secret: <32-byte-base64-key>   # Generated with: head -c 32 /dev/urandom | base64
  - identity: {}
```

Managed Kubernetes clusters (AKS, EKS, GKE) support encryption at rest — enable it in your cluster settings.

### Option 2: External Secrets Operator (the production choice) 🏆

Store secrets in a proper vault (Azure Key Vault, AWS Secrets Manager, HashiCorp Vault), then sync them into Kubernetes Secrets automatically:

```yaml
# First install External Secrets Operator via Helm, then:

apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: web-app-secrets
spec:
  refreshInterval: 1h                    # Re-sync from vault every hour
  secretStoreRef:
    name: azure-keyvault
    kind: ClusterSecretStore

  target:
    name: web-app-secrets                # Creates this Kubernetes Secret
    creationPolicy: Owner

  data:
  - secretKey: DB_PASSWORD               # Kubernetes Secret key name
    remoteRef:
      key: production-db-password        # Azure Key Vault secret name
  - secretKey: API_KEY
    remoteRef:
      key: api-service-key
```

The actual secret values live in Azure Key Vault (or wherever). Kubernetes only ever sees them briefly. If someone dumps etcd — no useful secrets. This is the enterprise approach. 🏰

---

## Immutable ConfigMaps and Secrets: The Frozen Manifest 🧊

Once a ConfigMap or Secret is set, you might want to prevent changes. Mark it immutable:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: stable-config
data:
  ENVIRONMENT: "production"
  REGION: "eu-west"
immutable: true      # Nobody changes this. Not even Dave.
```

```bash
kubectl apply -f stable-config.yaml

# Try to update it:
kubectl edit configmap stable-config
# error: ConfigMap "stable-config" is immutable and cannot be updated

# To change it: delete and recreate
kubectl delete configmap stable-config
kubectl apply -f updated-stable-config.yaml
```

Immutable ConfigMaps also improve performance — Kubernetes stops watching them for changes, reducing load on the API Server in clusters with many ConfigMaps. 🚀

---

## The Full Picture: ConfigMap + Secret + Pod Together 🎯

```yaml
# Full example: app that needs both config and secrets
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-service
  namespace: production
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-service
  template:
    metadata:
      labels:
        app: api-service
    spec:
      containers:
      - name: api
        image: my-company/api-service:2.1.0
        ports:
        - containerPort: 8080

        # All ConfigMap values as env vars:
        envFrom:
        - configMapRef:
            name: web-app-config

        # Specific secret values:
        env:
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: web-app-secrets
              key: DB_PASSWORD
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: web-app-secrets
              key: API_KEY

        # Config FILE from ConfigMap:
        volumeMounts:
        - name: app-config-file
          mountPath: /app/config
          readOnly: true
        - name: tls-certs
          mountPath: /app/certs
          readOnly: true

      volumes:
      - name: app-config-file
        configMap:
          name: web-app-config
          items:
          - key: app-config.json
            path: config.json
      - name: tls-certs
        secret:
          secretName: app-tls-secret
```

---

## The Harbourmaster's Log — Entry 8 📋

*Conducted a security audit today. Found three containers with passwords baked into environment variables in the Dockerfile. Found one container with the word "password" literally in its image name. Found Dave.*

*Implemented ConfigMaps for all non-sensitive configuration. Migrated all secrets to Kubernetes Secrets with RBAC restrictions (Episode 10 is coming). Set up External Secrets Operator syncing from Azure Key Vault.*

*The security team sent a congratulatory Slack message. This has also never happened before.*

*Dave asked if he could store his lunch preferences in a ConfigMap.*

*I said no. But I thought about it.* 🎩

---

## Your Mission, Should You Choose to Accept It 🎯

1. Create a ConfigMap with:
   - `APP_ENV=production`
   - `LOG_LEVEL=info`
   - A full JSON config file as a key

2. Create a Secret with:
   - A fake database password
   - A fake API key

3. Create a Deployment that:
   - Injects ALL ConfigMap values as environment variables
   - Injects specific Secret values as environment variables
   - Mounts the JSON config file from ConfigMap at `/app/config/settings.json`

4. Verify it works:

```bash
# Exec into a pod and check:
kubectl exec -it <pod-name> -- env | grep APP_ENV
kubectl exec -it <pod-name> -- cat /app/config/settings.json
kubectl exec -it <pod-name> -- sh -c 'echo "Secret length: ${#DB_PASSWORD}"'
```

**Bonus:** Mark your ConfigMap as `immutable: true` and try to update it. Marvel at the error message.

---

## Next Time on "Welcome to Container Harbour" 🎬

In **Episode 9**, we tackle one of the most misunderstood topics in Kubernetes — **Persistent Volumes and Storage**. Because Pods are ephemeral (they die all the time, remember?) but your database really, REALLY needs its data to survive. The warehouse that outlasts any individual freight container. 🏭

---

*P.S. — The first developer to hardcode a production password into a Docker image and push it to Docker Hub didn't get fired. They got a new company policy named after the incident and a permanent entry in the post-mortem hall of fame. The password was changed within 4 minutes of discovery, which is actually impressive. The image had 847 pulls before they caught it. Less impressive.* 😬

---

**🎯 Key Takeaways:**

- **NEVER** bake secrets into Docker images. Not even for testing. Especially not for testing.
- **ConfigMaps** = non-sensitive config (hostnames, feature flags, log levels, config files)
- **Secrets** = sensitive data (passwords, API keys, certs). base64 encoded by default, NOT encrypted.
- Two injection methods: **env vars** (good for simple values) or **volume mounts** (good for files)
- `envFrom` = inject ALL ConfigMap/Secret keys as env vars at once. Very convenient.
- Kubernetes Secrets are base64, not encrypted — configure encryption at rest or use External Secrets Operator for production
- **External Secrets Operator** + Azure Key Vault/AWS Secrets Manager = the real enterprise solution 🏰
- `immutable: true` = freeze a ConfigMap or Secret. Prevents accidental changes. Boosts performance.
- RBAC (Episode 10) controls who can READ Secrets. Use it aggressively. 🔒
