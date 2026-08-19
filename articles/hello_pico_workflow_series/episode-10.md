---
title: "🐳 Gate 4: Containerizing for Minikube"
series: "Hello Pico Workflow"
part: 10
organization: "the-software-s-journey"
tags: [open-engineering, pico, docker, minikube, kubernetes]
---

## 🐳 Gate 4: Containerizing for Minikube

Here's a mistake worth naming before it happens: if your development machine is Apple Silicon/macOS (as mine is), do **not** copy your locally built extension straight into a Kubernetes container. The wheel from the last episode was built for your machine's own architecture and operating system — it will not run correctly inside a Linux container. The fix is to build the PyO3 wheel *inside* the Docker build itself, on Linux, from source, every time:

```dockerfile
FROM python:3.13-slim AS builder
RUN apt-get update \
 && apt-get install -y curl build-essential \
 && curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"
RUN pip install maturin uv
WORKDIR /app
COPY . .
RUN maturin build --release
FROM python:3.13-slim
WORKDIR /app
COPY --from=builder /app/target/wheels /wheels
RUN pip install /wheels/*.whl
COPY python ./python
ENV PYTHONPATH=/app/python
CMD [
  "uvicorn",
  "manifold.app:app",
  "--host",
  "0.0.0.0",
  "--port",
  "8080"
]
```

Two stages, and the reasoning behind each is worth spelling out. The `builder` stage installs Rust and Maturin fresh, inside a Linux image, and runs the exact same `maturin build --release` from Episode 9 — but this time the resulting wheel is genuinely a Linux artifact, correct for wherever this container eventually runs. The final stage starts from a clean `python:3.13-slim` image, copies over only the built wheel (not the Rust toolchain, not the source tree), installs it, adds the Python-side `manifold` package, and sets `uvicorn` as the entrypoint — the same command we ran locally back in Episode 6, now baked into the image itself.

With the Dockerfile ready, it's time to actually start the cluster this whole thing will run on:

```bash
minikube start \
  --driver=docker \
  --cpus=6 \
  --memory=12288
```

Twelve gigabytes and six CPUs is a reasonable starting allowance, because before this course is done, Minikube will be running Crossplane, the Crossplane templating function, the Manifold/Pico deployment itself, Mosquitto, and Home Assistant — all on top of Kubernetes's own overhead. Confirm it's up:

```bash
kubectl get nodes
```

Expected:

```
NAME       STATUS   ROLES
minikube   Ready    control-plane
```

Now build the image directly into Minikube's own image store, skipping an external registry entirely:

```bash
minikube image build \
  -t open-engineering/hello-pico:0.1.0 \
  .
```

Verify it landed:

```bash
minikube image ls | grep hello-pico
```

See it listed, and that's **Gate 4**: a proper Linux OCI artifact exists inside the exact runtime environment that will eventually schedule it — no registry push, no architecture mismatch, just a correctly-built image sitting right where Kubernetes can find it.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| The multi-stage Dockerfile | Full source (Rust and Python) | Build the wheel on Linux inside the container, then install it into a clean runtime image | A self-contained, Linux-native OCI image running Manifold | Minikube's image store |
| `minikube start` | CPU and memory allocation for the local cluster | Provision a Kubernetes control plane locally | A running `minikube` node, ready for workloads | Every subsequent `kubectl`/Crossplane step in this series |
| `minikube image build` | The Dockerfile and full build context | Build the image directly inside Minikube's own runtime | `open-engineering/hello-pico:0.1.0`, available with no registry needed | Gate 4, and the Deployment we'll define a few episodes from now |

Next stop: installing Crossplane itself, and the templating function that will turn our declarative Pico into real Kubernetes resources.
