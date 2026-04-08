---
title: "Welcome to Container Harbour! 🚢 Ep.7"
part: 7
published: false
description: "Episode 7: The Customs Office — Ingress Controllers and Routing Rules. One gate to rule them all, with TLS, path routing, and zero tolerance for confusion."
tags: [kubernetes, beginners, devops, tutorial]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/welcome-to-container-harbour-episode-07.png"
series: "Welcome to Container Harbour!"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 7: The Customs Office — Ingress and Smart Traffic Routing 🛃

### We Had SEVENTEEN LoadBalancers. SEVENTEEN. 😱

I worked at a company once where every microservice had its own LoadBalancer Service. Seventeen microservices. Seventeen cloud load balancers. Seventeen public IP addresses.

You know how much that cost per month?

I'm not going to tell you because it's embarrassing and also I wasn't paying for it personally but I FELT it in my SOUL every time I looked at the cloud bill.

Our cloud architect walked in one Monday morning, opened the billing dashboard, made a sound like a kettle boiling, and then just quietly asked: "Has anyone heard of Ingress?"

We had not heard of Ingress.

By Friday we had one load balancer.

Let me save you from that Monday morning. 🎯

---

## The SIPOC of Ingress 🗂️

| | | Detail |
|---|---|---|
| **Supplier** | Who defines the routing rules? | You, platform engineers, Helm chart developers |
| **Input** | What comes in? | HTTP/HTTPS traffic from the outside world |
| **Process** | What does Ingress do? | Reads routing rules → matches host/path → forwards to correct Service |
| **Output** | What comes out? | Traffic routed to the right backend Service |
| **Consumer** | Who gets served? | External users hitting your APIs, websites, services |

---

## The Problem: Many Services, One Entrance 🌊

You have three services:

- `web-frontend` — your React app at `app.harbour.io`
- `api-service` — your backend API at `app.harbour.io/api`
- `admin-panel` — your admin interface at `admin.harbour.io`

Without Ingress: **three LoadBalancers**. Three public IPs. Three monthly charges. Three DNS records. Three TLS certificates to manage. It's a mess of harbour gates.

With Ingress: **one LoadBalancer**. One public IP. One TLS termination point. The Ingress Controller is the one smart Customs Office at the entrance — it reads the incoming ship's manifest (host header, path) and routes it to the right internal berth.

```
BEFORE INGRESS:                     AFTER INGRESS:
                                    
Internet                            Internet
   |                                    |
   |-- LoadBalancer 1 -> web-frontend   |-- LoadBalancer (ONE) --|
   |-- LoadBalancer 2 -> api-service    |                        |
   |-- LoadBalancer 3 -> admin-panel    |       🛃 Ingress       |
                                        |   (/app -> frontend)   |
THREE load balancers 💸                 |   (/api -> api)         |
THREE public IPs 💸                     |   (admin.* -> admin)   |
THREE TLS certs 💸                      |                        |
                                        |--> web-frontend Service |
                                        |--> api-service Service  |
                                        |--> admin-panel Service  |
                                        
                                    ONE load balancer ✅
                                    ONE public IP ✅
                                    ONE TLS cert (wildcard!) ✅
```

---

## The Two Parts of Ingress: Rules + Controller 🔧

Here's something that confuses EVERYONE at first. There are TWO separate things:

1. **Ingress Resource** — the YAML rules. "Traffic to `/api` goes to `api-service`." Just a config file.
2. **Ingress Controller** — the software that READS those rules and actually does the routing.

Kubernetes doesn't include an Ingress Controller by default. You install one separately. The most popular is **nginx-ingress-controller** but there's also Traefik, HAProxy, Contour, and more.

Think of it like this: the Ingress Resource is the **Customs rulebook**. The Ingress Controller is the **actual Customs Officer** reading the rulebook and acting on it. The rulebook is useless without the officer. The officer has nothing to do without the rulebook.

```bash
# Install nginx-ingress-controller (with Helm -- the Kubernetes package manager)
helm upgrade --install ingress-nginx ingress-nginx \
  --repo https://kubernetes.github.io/ingress-nginx \
  --namespace ingress-nginx --create-namespace

# With minikube:
minikube addons enable ingress

# Verify the controller is running
kubectl get pods -n ingress-nginx
# NAME                                        READY   STATUS
# ingress-nginx-controller-5d88495688-abcde   1/1     Running

# The controller creates ONE LoadBalancer Service to receive all traffic:
kubectl get svc -n ingress-nginx
# NAME                      TYPE           EXTERNAL-IP
# ingress-nginx-controller  LoadBalancer   20.123.45.67   <- Your ONE public IP
```

---

## Path-Based Routing: One Domain, Many Destinations 🗺️

```yaml
# ingress-paths.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: harbour-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx     # Which Ingress Controller handles this
  rules:
  - host: app.harbour.io
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-frontend      # Traffic to app.harbour.io/ -> frontend
            port:
              number: 80
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-service       # Traffic to app.harbour.io/api -> API
            port:
              number: 8080
      - path: /static
        pathType: Prefix
        backend:
          service:
            name: static-files      # Traffic to app.harbour.io/static -> CDN service
            port:
              number: 80
```

```bash
kubectl apply -f ingress-paths.yaml

kubectl get ingress
# NAME              CLASS   HOSTS           ADDRESS         PORTS   AGE
# harbour-ingress   nginx   app.harbour.io  20.123.45.67    80      10s

kubectl describe ingress harbour-ingress
# Rules:
#   Host            Path    Backends
#   app.harbour.io
#                   /       web-frontend:80
#                   /api    api-service:8080
#                   /static static-files:80
```

```bash
# Test it (add to /etc/hosts for local testing):
echo "20.123.45.67 app.harbour.io" >> /etc/hosts

curl http://app.harbour.io/          # Goes to web-frontend
curl http://app.harbour.io/api/v1    # Goes to api-service
curl http://app.harbour.io/static/logo.png  # Goes to static-files
```

---

## Host-Based Routing: Different Domains, Same IP 🌐

```yaml
# ingress-hosts.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: multi-host-ingress
spec:
  ingressClassName: nginx
  rules:
  # Everything on app.harbour.io goes to the main app
  - host: app.harbour.io
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-frontend
            port:
              number: 80

  # Everything on admin.harbour.io goes to the admin panel
  - host: admin.harbour.io
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: admin-panel
            port:
              number: 3000

  # Everything on api.harbour.io goes to the API
  - host: api.harbour.io
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 8080
```

Three different domains. One load balancer. One public IP. The Customs Officer reads the `Host` header and routes accordingly. This is the move. 😎

---

## TLS: The X-Ray Machine at Customs 🔐

One Ingress, one TLS certificate, all your services served over HTTPS. You can even auto-provision certificates with **cert-manager** (integrates with Let's Encrypt — free certificates!).

```bash
# Install cert-manager
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager --create-namespace \
  --set installCRDs=true

# Create a ClusterIssuer (tells cert-manager HOW to get certificates)
```

```yaml
# cluster-issuer.yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@harbour.io
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
```

```yaml
# ingress-tls.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: secure-ingress
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"   # Auto-get a cert!
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - app.harbour.io
    - admin.harbour.io
    secretName: harbour-tls-secret     # cert-manager stores the cert here
  rules:
  - host: app.harbour.io
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-frontend
            port:
              number: 80
  - host: admin.harbour.io
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: admin-panel
            port:
              number: 3000
```

```bash
kubectl apply -f cluster-issuer.yaml
kubectl apply -f ingress-tls.yaml

# Watch cert-manager do its thing:
kubectl get certificate
# NAME                 READY   SECRET               AGE
# harbour-tls-secret   True    harbour-tls-secret   2m   <- Certificate issued!

# Your sites are now HTTPS. For FREE. Forever auto-renewed. 🎉
```

---

## Ingress Annotations: The Customs Officer's Special Instructions 📝

The nginx Ingress Controller supports DOZENS of annotations that customise behaviour. These are instructions written on the outside of the Ingress resource:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: advanced-ingress
  annotations:
    # Rate limiting: max 100 requests per minute per IP
    nginx.ingress.kubernetes.io/limit-rps: "100"

    # Redirect HTTP to HTTPS automatically
    nginx.ingress.kubernetes.io/ssl-redirect: "true"

    # Increase timeout for slow API endpoints
    nginx.ingress.kubernetes.io/proxy-read-timeout: "300"

    # Enable CORS (Cross-Origin Resource Sharing)
    nginx.ingress.kubernetes.io/enable-cors: "true"
    nginx.ingress.kubernetes.io/cors-allow-origin: "https://app.harbour.io"

    # Rewrite /api/v2 to /v2 before hitting the backend
    nginx.ingress.kubernetes.io/rewrite-target: /$2

    # Custom error pages
    nginx.ingress.kubernetes.io/custom-http-errors: "404,503"
    nginx.ingress.kubernetes.io/default-backend: error-pages-service

spec:
  ingressClassName: nginx
  rules:
  - host: api.harbour.io
    http:
      paths:
      - path: /api/v2(/|$)(.*)
        pathType: Prefix
        backend:
          service:
            name: api-v2-service
            port:
              number: 8080
```

---

## The Default Backend: When Nothing Matches 🚧

What happens when traffic arrives at the Ingress but doesn't match any rule? It goes to the **default backend** — usually a simple 404 page:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: harbour-ingress
spec:
  ingressClassName: nginx
  defaultBackend:
    service:
      name: custom-404-page         # Show a nice branded error page
      port:
        number: 80
  rules:
  - host: app.harbour.io
    # ... your rules ...
```

```yaml
# The custom 404 page service:
apiVersion: apps/v1
kind: Deployment
metadata:
  name: custom-404-page
spec:
  replicas: 1
  selector:
    matchLabels:
      app: error-page
  template:
    metadata:
      labels:
        app: error-page
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        volumeMounts:
        - name: error-html
          mountPath: /usr/share/nginx/html
      volumes:
      - name: error-html
        configMap:
          name: error-page-html
```

Classy 404. The Harbourmaster demands standards. 🎩

---

## Debugging Ingress: When Customs Is Confused 🔍

```bash
# Check if the Ingress has an address (if blank, controller isn't running)
kubectl get ingress
# If EXTERNAL-IP is blank: kubectl get svc -n ingress-nginx

# Check Ingress controller logs -- the Customs Officer's diary
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller --tail=50

# Describe the Ingress -- see events and backend resolution
kubectl describe ingress harbour-ingress

# Common problems:
# 1. "No endpoints available for service" -- your backend Service has no healthy Pods
#    Fix: kubectl get endpoints <service-name>

# 2. "Service not found" -- wrong service name in Ingress spec
#    Fix: kubectl get services -- check exact name and namespace

# 3. 502 Bad Gateway -- Ingress reached the Service but the Pod is broken
#    Fix: kubectl logs <pod-name> -- what's the app saying?

# 4. 404 from nginx -- rule didn't match
#    Fix: Check path, host header, pathType (Prefix vs Exact)
```

---

## The Harbourmaster's Log — Entry 7 📋

*Consolidated from 17 LoadBalancers to 1 Ingress. Cloud bill reduced by 84%.*

*The CFO sent a thank-you email. This has never happened before in my career.*

*I tried to explain how Ingress works. I said: "Imagine all ships entering through one Customs Office. The Customs Officer reads the ship's manifest and directs it to the right berth." The CFO nodded enthusiastically.*

*Then someone asked why the Ingress wasn't working for the staging environment.*

*The Customs Officer — I mean the nginx Ingress Controller — was not running in the staging namespace. It was only installed in production.*

*We installed it in staging. It worked.*

*Dave asked why we don't just open all the ports on all the Services. I told him that was the old way, and that the old way cost us 84% more than the new way.*

*Dave got very quiet.* 🎩

---

## Your Mission, Should You Choose to Accept It 🎯

Create a complete Ingress setup with THREE backend services:

1. Deploy three separate apps (use different nginx configs or simple echo servers):

```yaml
# Simple echo server Pod for testing
apiVersion: apps/v1
kind: Deployment
metadata:
  name: echo-frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: echo-frontend
  template:
    metadata:
      labels:
        app: echo-frontend
    spec:
      containers:
      - name: echo
        image: hashicorp/http-echo:latest
        args:
        - "-text=Hello from FRONTEND!"
        ports:
        - containerPort: 5678
```

2. Create Services for all three
3. Create ONE Ingress with:
   - `/` routing to frontend
   - `/api` routing to API service
   - `/admin` routing to admin service
4. Test all three paths work correctly

**Bonus:** Add rate limiting of 10 requests per second via annotation and test hitting it with a loop.

---

## Next Time on "Welcome to Container Harbour" 🎬

In **Episode 8**, we open the **sealed cargo manifests** — **ConfigMaps and Secrets**. Because your app needs configuration. And some of that configuration is a database password. And you absolutely cannot write that password in chalk on the side of a container for everyone to see.

The Harbourmaster is looking at you, Dave. 🎩

---

*P.S. — The nginx Ingress Controller processes HTTP traffic using the same NGINX web server that powers roughly 34% of all websites on the internet. So when you install it in your cluster, you're deploying the same technology that serves Netflix, Dropbox, and WordPress.com. Slightly different scale, but same software. You're basically running Netflix infrastructure. Tell your friends.* 🎬

---

**🎯 Key Takeaways:**

- **Ingress** = one entrance point, many backend destinations. One LoadBalancer to rule them all.
- **Ingress Resource** = the routing rules (YAML). **Ingress Controller** = the software that enforces them.
- Kubernetes does NOT include an Ingress Controller — you install one (nginx-ingress is most popular).
- **Path-based routing**: `app.io/api` -> api-service, `app.io/` -> frontend
- **Host-based routing**: `app.io` -> frontend, `admin.io` -> admin-panel. Same IP!
- **TLS**: cert-manager + Let's Encrypt = free auto-renewed HTTPS certificates. Zero excuses.
- **Annotations** customise NGINX behaviour: rate limits, CORS, redirects, timeouts
- **Default backend** handles unmatched traffic gracefully — no ugly nginx 404 errors
- Debugging order: check Ingress address → controller logs → describe → backend endpoints 🔍
