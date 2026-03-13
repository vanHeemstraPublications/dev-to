---
title: "Welcome to Container Harbour! 🚢 Ep.13"
published: false
description: "Episode 13: The Night Shift Nobody Talks About — Jobs and CronJobs. Some cargo only arrives on Tuesdays at 3am. Someone has to be there."
tags: [kubernetes, beginners, devops, tutorial]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/welcome-to-container-harbour-episode-13.png"
series: "Welcome to Container Harbour!"
canonical_url: ""
organization: "the-software-s-journey"
---

## Episode 13: The Night Shift Nobody Talks About 🌙

### The Cron Tab That Lived on ONE Server and Nobody Knew About It 😱

Every organisation has one. A server somewhere — maybe physical, maybe a VM, definitely not in source control — running a crontab that nobody dares touch. The person who set it up left in 2018. The crontab runs critical jobs: database backups, report generation, data imports, invoice processing.

One day the server goes down.

Nobody knows which jobs ran. Nobody knows which didn't. Nobody knows WHERE the scripts are. Nobody knows WHAT they do. There are no logs. There are no alerts. There is only silence. And then, two weeks later, an angry email from accounting asking why the monthly invoices didn't go out.

This is the Night Shift Problem.

Kubernetes Jobs and CronJobs are the solution. Version-controlled, monitored, retried, logged, and observable. The night shift crew, but organised. 🌙

---

## The SIPOC of Jobs and CronJobs 🗂️

| | | Detail |
|---|---|---|
| **Supplier** | Who triggers the job? | A schedule (CronJob) or a direct trigger (CI/CD, operator, human) |
| **Input** | What goes in? | The job spec: what to run, how many times, how many in parallel |
| **Process** | What happens? | Kubernetes runs Pod(s), monitors completion, retries on failure |
| **Output** | What comes out? | Successful completion (exit code 0) + logs + history |
| **Consumer** | Who cares about the result? | Monitoring systems, downstream systems, your sleep schedule |

---

## Jobs: Run Once, Run to Completion ✅

A **Job** creates Pods that run until they COMPLETE (exit code 0). Not until they're healthy and running forever — until they're DONE.

```yaml
# database-migration-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: run-migrations-v2-1-0
  namespace: production
spec:
  backoffLimit: 3             # Retry up to 3 times if it fails
  activeDeadlineSeconds: 300  # Kill the job if it takes more than 5 minutes
  ttlSecondsAfterFinished: 3600  # Delete job+pods 1 hour after completion

  template:
    spec:
      restartPolicy: OnFailure    # Retry the Pod if it fails (not Never!)
      containers:
      - name: migrations
        image: my-app:2.1.0
        command: ["python", "manage.py", "migrate"]
        env:
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: db-secrets
              key: DB_PASSWORD
```

```bash
kubectl apply -f database-migration-job.yaml

# Watch the job run
kubectl get jobs --watch
# NAME                      COMPLETIONS   DURATION   AGE
# run-migrations-v2-1-0     0/1           10s        10s
# run-migrations-v2-1-0     1/1           45s        45s   <- Done!

# See the Pod that ran it
kubectl get pods -l job-name=run-migrations-v2-1-0
# NAME                             STATUS      RESTARTS
# run-migrations-v2-1-0-abc123     Completed   0

# Get the logs!
kubectl logs job/run-migrations-v2-1-0
# Running migration 001_create_ships_table... OK
# Running migration 002_add_cargo_column... OK
# All migrations complete. 🎉
```

---

## Parallel Jobs: The Fleet of Night Shift Workers 🚢

Some jobs benefit from parallel execution:

```yaml
# parallel-image-processing.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: process-images
spec:
  completions: 20          # Need 20 successful completions total
  parallelism: 5           # Run 5 Pods in parallel at any time
  backoffLimit: 10

  template:
    spec:
      restartPolicy: OnFailure
      containers:
      - name: image-processor
        image: my-image-processor:latest
        env:
        - name: BATCH_SIZE
          value: "100"
```

```bash
kubectl apply -f parallel-image-processing.yaml

kubectl get pods -l job-name=process-images
# NAME                       STATUS
# process-images-abc123      Running     <- 5 running in parallel
# process-images-def456      Running
# process-images-ghi789      Running
# process-images-jkl012      Running
# process-images-mno345      Running
# process-images-pqr678      Completed   <- 3 already done!
# process-images-stu901      Completed
# process-images-vwx234      Completed

kubectl get jobs process-images
# NAME              COMPLETIONS   DURATION
# process-images    8/20          2m        <- 8 done, 12 remaining, 5 running
```

---

## CronJobs: The Scheduled Night Shift 📅

CronJobs create Jobs on a schedule. Kubernetes cron syntax is the same as Linux cron:

```
┌──────── minute (0-59)
│ ┌────── hour (0-23)
│ │ ┌──── day of month (1-31)
│ │ │ ┌── month (1-12)
│ │ │ │ ┌ day of week (0-7, where 0 and 7 are Sunday)
│ │ │ │ │
* * * * *
```

```yaml
# nightly-backup.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: nightly-database-backup
  namespace: production
spec:
  schedule: "0 2 * * *"              # Every day at 2:00am
  timeZone: "Europe/Amsterdam"        # Explicit timezone (Kubernetes 1.27+)
  successfulJobsHistoryLimit: 7       # Keep last 7 successful job records
  failedJobsHistoryLimit: 3           # Keep last 3 failed job records
  concurrencyPolicy: Forbid           # Don't start new job if previous is still running
  startingDeadlineSeconds: 300        # If job didn't start within 5m of schedule, skip it

  jobTemplate:
    spec:
      backoffLimit: 2
      activeDeadlineSeconds: 3600     # Max 1 hour to complete
      ttlSecondsAfterFinished: 86400  # Keep for 24h after completion

      template:
        spec:
          restartPolicy: OnFailure
          containers:
          - name: backup
            image: my-backup-tool:latest
            command:
            - /bin/sh
            - -c
            - |
              echo "Starting backup at $(date)"
              pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME | gzip > /backup/harbour-$(date +%Y%m%d).sql.gz
              echo "Backup complete: $(ls -lh /backup/)"
            env:
            - name: DB_HOST
              valueFrom:
                configMapKeyRef:
                  name: db-config
                  key: DB_HOST
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: db-secrets
                  key: DB_PASSWORD
            volumeMounts:
            - name: backup-storage
              mountPath: /backup
          volumes:
          - name: backup-storage
            persistentVolumeClaim:
              claimName: backup-pvc
```

```yaml
# More schedule examples:
schedule: "*/15 * * * *"     # Every 15 minutes
schedule: "0 * * * *"        # Every hour on the hour
schedule: "0 9 * * 1-5"      # 9am on weekdays (Monday-Friday)
schedule: "0 2 1 * *"        # 2am on the 1st of every month
schedule: "@daily"            # Once a day at midnight
schedule: "@weekly"           # Once a week on Sunday at midnight
```

---

## ConcurrencyPolicy: Managing the Night Crew 👷

| Policy | Behaviour | Use when |
|---|---|---|
| `Allow` | Run multiple jobs simultaneously (default) | Jobs are independent, faster is better |
| `Forbid` | Skip new job if previous is still running | Jobs must not overlap (DB operations) |
| `Replace` | Kill running job, start fresh | Latest data matters more than completing previous |

```yaml
spec:
  concurrencyPolicy: Forbid     # Nightly backup must not overlap with itself
```

---

## Manually Triggering a CronJob 🎯

Sometimes you need to run a CronJob RIGHT NOW, not wait for the schedule:

```bash
# Trigger a job from a CronJob immediately
kubectl create job --from=cronjob/nightly-database-backup manual-backup-20260311

# Watch it run
kubectl get jobs --watch

# Get logs
kubectl logs job/manual-backup-20260311
```

---

## Monitoring Jobs: The Night Shift Report 📋

```bash
# See all CronJobs and their last schedule time
kubectl get cronjobs
# NAME                     SCHEDULE    SUSPEND   ACTIVE   LAST SCHEDULE
# nightly-database-backup  0 2 * * *   False     0        6h
# weekly-report            0 9 * * 1   False     0        5d

# See last N jobs created by a CronJob
kubectl get jobs -l app=nightly-database-backup \
  --sort-by='.metadata.creationTimestamp'

# Suspend a CronJob (maintenance window)
kubectl patch cronjob nightly-database-backup -p '{"spec":{"suspend":true}}'

# Unsuspend it
kubectl patch cronjob nightly-database-backup -p '{"spec":{"suspend":false}}'

# Get logs from the most recent job
kubectl logs $(kubectl get pods -l job-name=nightly-database-backup-abc123 \
  -o jsonpath='{.items[0].metadata.name}')
```

---

## The Init Container: The Pre-Shift Setup Crew 🏗️

Init containers are special containers that run BEFORE the main containers in a Pod — to completion. They're perfect for pre-job setup: checking dependencies are ready, downloading data, running migrations before the app starts.

```yaml
spec:
  initContainers:
  - name: wait-for-database
    image: busybox:latest
    command: ['sh', '-c',
      'until nc -z postgres.production.svc.cluster.local 5432;
       do echo "Waiting for database..."; sleep 2; done;
       echo "Database is ready!"']

  - name: run-migrations
    image: my-app:latest
    command: ['python', 'manage.py', 'migrate']
    env:
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: db-secrets
          key: DB_PASSWORD

  containers:
  - name: web-app             # Main app ONLY starts after ALL init containers complete
    image: my-app:latest
    ports:
    - containerPort: 8080
```

Init containers run sequentially, each to completion, before the main containers start. If an init container fails, it's retried. The main containers don't start until ALL init containers succeed. 🎯

---

## The Harbourmaster's Log — Entry 13 📋

*Found the cursed crontab server today. A VM from 2016 with 47 cron entries, no documentation, and ownership attributed to an email address that no longer exists in the directory.*

*Migrated all 47 jobs to Kubernetes CronJobs over two weeks. Each one is now:*
*- Version controlled in Git*
*- Visible with kubectl get cronjobs*
*- Observable with kubectl logs*
*- Alertable via Prometheus metrics*
*- Retried automatically on failure*
*- Documented in the Job spec itself*

*The VM has been decommissioned.*

*Last night, for the first time in probably years, someone noticed a backup job FAILED because the alert fired. We fixed it. The data is safe.*

*For years before this, backups were probably failing occasionally and nobody knew.*

*The night shift, properly organised, is the most important shift.* 🎩

---

## Your Mission 🎯

1. Create a CronJob that runs every 2 minutes and writes the current timestamp + some stats to a log

2. Watch it create Jobs automatically

3. Manually trigger it with `kubectl create job --from=cronjob/...`

4. Check `successfulJobsHistoryLimit` is working by waiting for several runs

5. **Bonus:** Create a Job with `parallelism: 3` that processes a batch of items. Use an environment variable to give each parallel Pod a unique ID so you can see them processing different items.

---

## Next Time 🎬

**Episode 14**: Reserved Berths for Divas — **StatefulSets**. Regular Pods don't care where they live. Databases absolutely do. 🎭

---

**🎯 Key Takeaways:**

- **Job** = run to completion, not run forever. For migrations, batch processing, one-off tasks.
- **CronJob** = scheduled Jobs. The right home for every task that used to live in a crontab.
- `backoffLimit` = retry count. `activeDeadlineSeconds` = timeout. Both are essential for production.
- `concurrencyPolicy: Forbid` prevents overlapping runs. Critical for database operations.
- `successfulJobsHistoryLimit` + `failedJobsHistoryLimit` = control Pod + Job retention.
- `ttlSecondsAfterFinished` = auto-cleanup of completed Jobs.
- **Init containers** = pre-startup tasks. Run sequentially to completion before main app starts.
- `kubectl create job --from=cronjob/...` = trigger a CronJob manually. Extremely useful.
- Put EVERY crontab you have into a Kubernetes CronJob. Every. Single. One. 📋
