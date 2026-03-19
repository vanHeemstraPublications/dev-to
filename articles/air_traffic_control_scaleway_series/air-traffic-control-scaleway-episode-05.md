---
title: "Air Traffic Control Scaleway Ep.5"
part: 5
published: false
description: "Episode 5 of the Air Traffic Control series: manage Object Storage on Scaleway — create buckets, control visibility, enforce bucket policies, enable versioning, host a static website, and configure CORS. Explained in the voice of Thunderbirds."
tags: [scaleway, cloud, object-storage, s3]
cover_image: "https://raw.githubusercontent.com/vanHeemstraPublication/dev-to/main/images/air_traffic_control_scaleway_series/air-traffic-control-scaleway-episode-05.png"
series: "Air Traffic Control Scaleway Series"
canonical_url: ""
organization: "the-software-s-journey"
---

# The Cargo Hold: Object Storage on Scaleway

*“Thunderbird 2 carries everything International Rescue needs for a mission — rescue pods, equipment, supplies. But the hold does not simply accept cargo. Every item is catalogued, classified, and secured. Some crates are visible to all crew. Others are restricted. The manifest is always controlled.”*
*— Virgil Tracy, Thunderbird 2 Pilot*

-----

Welcome back to the **Scaleway Air Traffic Control Centre**.

In Episode 4, we deployed unmanned probes — ephemeral functions and containers that execute and vanish. In this episode, we deal with what persists: **Object Storage**.

Object Storage is the cargo hold of your cloud infrastructure. It stores files, images, backups, datasets, and static assets in a flat namespace of **buckets** and **objects**. Access is controlled by visibility settings, bucket policies, and CORS rules. Data integrity over time is protected by versioning. And with the bucket website feature, that same hold can serve a public-facing static site directly from its contents.

This episode covers the full range of Object Storage capabilities — using three different tools: the **Scaleway Console**, the **MinIO Client**, and the **AWS CLI**.

-----

## 🎯 Mission Parameters

In this hands-on episode, you will learn how to:

- Create a bucket via the **Scaleway Console** and via the **MinIO Client**
- Add objects using both tools, including objects with different **storage classes**
- Manage **object visibility** — public versus private, with and without signed links
- Configure a **bucket policy** using a JSON document and the MinIO CLI
- Enable and use **bucket versioning** to maintain object history
- Configure the **AWS CLI** for Scaleway Object Storage
- Enable the **bucket website** feature and serve a static site from a bucket
- Configure **CORS rules** to control cross-origin access to your bucket

### Pre-Launch Checklist

- ✅ You have a Scaleway account and can access the Organisation you own
- ✅ [`aws-cli` and `awscli-plugin-endpoint`](https://www.scaleway.com/en/docs/storage/object/api-cli/object-storage-aws-cli/) are installed on your machine
- ✅ [MinIO Client](https://docs.min.io/minio/baremetal/reference/minio-mc.html) is installed on your machine
- ✅ You have cloned the [`scw-certifications`](https://github.com/scaleway/scw-certifications/) repository — the `05_storage/` folder contains the assets for this episode
- ✅ You have at least one partner available — bucket policy and CORS exercises are group activities

> **Tip:** The number of people in your group determines how you configure bucket policies. In a group of two, each person grants the other access to their Organisation’s resources. In a group of three, the first grants access to the second, the second to the third, and the third to the first — a full rotation of trust.

-----

## 📊 SIPOC — How Object Storage Flows Through the System

|Stage|SIPOC Element|Object Storage Equivalent                                                                                                |Example                                                                                  |
|-----|-------------|-------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
|**S**|**Supplier** |Scaleway Object Storage engine + your Organisation account                                                               |S3-compatible storage layer in `fr-par`                                                  |
|**I**|**Input**    |Bucket names, object files, storage classes, policy JSON, CORS config, HTML assets                                       |`hands-on-bucket-{yourname}`, `hello-world.txt`, `GLACIER`, `granular-bucket-policy.json`|
|**P**|**Process**  |Create buckets → Upload objects → Control visibility → Apply policies → Enable versioning → Host website → Configure CORS|All the hands-on steps in this episode                                                   |
|**O**|**Output**   |Governed, versioned, policy-controlled buckets with a live static website endpoint                                       |`https://<BUCKET_NAME>.s3-website.fr-par.scw.cloud/`                                     |
|**C**|**Consumer** |Users, applications, browsers, and cross-origin clients accessing bucket content                                         |Your partner, your browser, your frontend application                                    |

```
Supplier              Input                Process               Output               Consumer
─────────             ─────────            ─────────             ─────────            ─────────
Scaleway       ──▶   Bucket names    ──▶  Create buckets   ──▶  Governed      ──▶   Users
Object               Object files         Upload objects        versioned             Applications
Storage              Storage class        Control visibility    buckets               Browsers
engine               Policy JSON          Apply policies        Static website        Cross-origin
                     CORS config          Enable versioning     endpoint              clients
Organisation         HTML assets          Host website
Owner account                             Configure CORS
```

> **Tower to crew:** Object Storage is S3-compatible. Every CLI command in this episode that references `aws s3` or `mc` is targeting Scaleway’s storage layer via the same API that any S3-compatible tool understands. The platform is Scaleway; the protocol is S3.

-----

## 🛫 Section 1 — Pre-Flight: Configure Credentials and Tools

Before any cargo is loaded, the ground crew must be credentialed. Two tools require configuration: environment variables for both clients, and an alias for the MinIO Client.

### 1.1 — Export API Key Environment Variables

In your terminal, export your API key credentials:

```bash
export SCW_ACCESS_KEY={YOUR_ACCESS_KEY}
export SCW_SECRET_KEY={YOUR_SECRET_KEY}
```

> **Note:** Replace `{YOUR_ACCESS_KEY}` and `{YOUR_SECRET_KEY}` with the values from your Scaleway API key. These environment variables will be used by both the MinIO Client and subsequent CLI commands in this episode.

### 1.2 — Configure the MinIO Client Alias

Register Scaleway as a named storage target in the MinIO Client:

```bash
mc alias set scaleway https://s3.fr-par.scw.cloud $SCW_ACCESS_KEY $SCW_SECRET_KEY
```

From this point forward, `scaleway/` is the MinIO Client prefix for all Scaleway Object Storage operations.

-----

## 🏗️ Section 2 — Load the Cargo Hold: Create Buckets and Add Objects

We create two buckets — one via the Console, one via the CLI — and populate them with objects across different storage classes.

### 2.1 — Create a Bucket in the Console

1. In the **Storage** section of the side menu, select **Object Storage**.
1. Click **Create bucket**.
1. Name your bucket `hands-on-bucket-{yourname}`.

> **Note:** Bucket names are globally unique across all Scaleway users. If your name is taken, append a number or short suffix.

1. Leave the region and bucket visibility at their defaults.
1. Click **Create bucket**.

### 2.2 — Add an Object via the Console

1. Select your bucket from the **Buckets** tab.
1. Click **Upload**, then choose a file from your machine.
1. Select the `Standard` storage class, then click **Validate storage class**.

### 2.3 — Create a Bucket Using the MinIO Client

```bash
mc mb scaleway/hands-on-bucket-cli-{yourname}
```

Return to the **Buckets** tab in the Console and verify the new bucket appears in the list.

### 2.4 — Set a Bucket Environment Variable

```bash
export BUCKET=(NAME_OF_NEW_BUCKET)
```

> **Note:** Replace `(NAME_OF_NEW_BUCKET)` with the exact name you used in the MinIO `mb` command above. This variable is used throughout the remaining sections.

### 2.5 — Add Files Using the MinIO Client

Upload a Standard-class file and verify:

```bash
echo "Hello world" > /tmp/hello-world.txt
mc cp /tmp/hello-world.txt scaleway/$BUCKET
mc ls scaleway/$BUCKET
```

Confirm that `hello-world.txt` appears in the Console under your bucket.

Upload a second file and verify it, then push the same file again to the `GLACIER` storage class:

```bash
echo "Hello again, world" > /tmp/hello-again-world.txt
mc cp /tmp/hello-again-world.txt scaleway/$BUCKET

# Verify upload and download round-trip
mc ls scaleway/$BUCKET
mc cp scaleway/$BUCKET/hello-again-world.txt /tmp/hello-again-world.txt.download
diff /tmp/hello-again-world.txt /tmp/hello-again-world.txt.download

# Push the same file again with Glacier storage class
mc cp --storage-class GLACIER /tmp/hello-again-world.txt scaleway/$BUCKET
```

In the Console, verify that `hello-again-world.txt` appears with the `Glacier` storage class.

> **Tower to crew:** Scaleway Object Storage offers three storage classes: `Standard` (immediate access, higher cost), `Onezone-IA` (infrequent access, lower cost), and `Glacier` (archival, lowest cost, retrieval delay). The choice is made at upload time and can be changed later. Match the class to the access pattern — Glacier for backups that are rarely retrieved, Standard for assets that are served frequently.

-----

## 🧑‍✈️ Section 3 — Cargo Manifest: Manage Object Visibility

By default, all objects in a Scaleway bucket are `Private`. Making an object accessible to an external party requires a deliberate visibility decision. Two strategies are available.

**Strategy A — Set the object to Public:**

1. In the Console, navigate to the `hello-world.txt` object in your bucket.
1. Click **…** to the right of the object, then select **Visibility**.
1. Select the **Public** option, then click **Update object visibility**. The confirmation message `Object visibility modified` appears.
1. Click **…** again, then select **Get public link**.
1. Share the public link with your partner. They should be able to open it directly in a browser.

**Strategy B — Generate a signed link (object remains Private):**

Keep the object set to `Private` and use the Console or CLI to generate a time-limited signed URL. The object itself is never exposed — only the URL grants temporary access.

> **Tower confirms:** Strategy A is appropriate for genuinely public assets — static images, downloadable files, public documentation. Strategy B is appropriate for any asset that must remain access-controlled but needs to be shared temporarily. Never set a bucket containing sensitive data to public visibility.

-----

## 🔒 Section 4 — Flight Authorisation: Configure a Bucket Policy

A bucket policy defines granular access rules in JSON. It controls who may list the bucket, who may read objects, and who may write — at the path level.

### 4.1 — Retrieve Your User ID

```bash
export USER_ID={YOUR_USER_ID}
```

> **Note:** Your User ID is available in your Organisation → **IAM** → **Users** → your account → **Overview** → **User information**.

### 4.2 — Edit the Policy File

1. In your terminal, navigate to the `05_storage/assets/permissions` folder of the cloned repository.
1. Open `granular-bucket-policy.json`. The policy authorises all users to list buckets and read objects, but restricts write access to `/upload` for a specified user only.
1. Replace `<BUCKET_NAME>` with the name of your bucket and `<USER_ID>` with your User ID.
1. Save the file.

### 4.3 — Apply the Policy

```bash
mc anonymous set-json granular-bucket-policy.json scaleway/$BUCKET
```

### 4.4 — Test the Policy

Verify the following scenarios with your partner:

|Scenario                                   |Expected Result                                   |
|-------------------------------------------|--------------------------------------------------|
|`GET` / `LIST` by any user                 |Succeeds                                          |
|Upload to `/` by an authorised user        |Fails — write to root is not permitted            |
|Upload to `/upload` by an authorised user  |Succeeds                                          |
|Upload to `/upload` by an unauthorised user|Fails — policy denies write for unknown principals|


> **Tower confirms:** The policy is path-scoped. Authorised users can write to `/upload` but not to the bucket root. All other users are read-only. This is precisely the kind of granular clearance architecture that prevents a misconfigured CI/CD pipeline from overwriting production assets.

-----

## 💾 Section 5 — Version Control: Enable Bucket Versioning

Versioning preserves every previous state of every object. Overwrites do not destroy — they create a new version. Deletions are soft — a delete marker is placed, not data removed.

### 5.1 — Enable Versioning

1. In the **Buckets** tab, select your bucket.
1. Open the **Bucket settings** tab.
1. Scroll to the **Bucket versioning** section and click **Enable versioning**.

### 5.2 — Create Multiple Versions

```bash
echo "Hello world v2" > /tmp/hello-world.txt
mc cp /tmp/hello-world.txt scaleway/$BUCKET

echo "Hello world v3" > /tmp/hello-world.txt
mc cp /tmp/hello-world.txt scaleway/$BUCKET
```

### 5.3 — List All Versions

```bash
mc ls --versions scaleway/$BUCKET
```

Each version of `hello-world.txt` is listed with its own `VersionId` and timestamp.

### 5.4 — Retrieve a Specific Version

Copy the `VersionId` of the version you want to restore, then run:

```bash
mc cp --version-id <VersionId> scaleway/$BUCKET/hello-world.txt .
```

The file is downloaded containing the content from that specific version — v1, v2, or v3 — regardless of what the current version contains.

> **Tower to crew:** Versioning is your black box recorder. When something goes wrong — an accidental overwrite, a bad deployment, a corrupted upload — you retrieve the previous version rather than restoring from backup. Enable it on any bucket that holds data you cannot afford to lose.

-----

## 🌐 Section 6 — Static Broadcast: Enable the Bucket Website Feature

A bucket with the website feature enabled becomes a static hosting endpoint. No server, no container, no reverse proxy — just objects served directly over HTTPS from the bucket URL.

### 6.1 — Configure the AWS CLI

Before using `aws s3` commands, configure the AWS CLI for Scaleway by following the [Scaleway AWS CLI setup guide](https://www.scaleway.com/en/docs/storage/object/api-cli/object-storage-aws-cli/). You will point the CLI at `https://s3.fr-par.scw.cloud` and supply your access and secret keys.

### 6.2 — Enable the Website Feature

1. In the **Storage** section of the side menu, select **Object Storage**.
1. Select the bucket you wish to use as a website host.
1. Open the **Bucket settings** tab.
1. Scroll to the **Bucket website** section and click **Enable bucket website**.
1. Enter `index.html` as the index document and `error.html` as the error document.
1. Click **Save settings**.

Alternatively, enable the feature from the CLI:

```bash
aws s3 website s3://<BUCKET_NAME>/ \
  --index-document index.html \
  --error-document error.html
```

### 6.3 — Access the Bucket Website

Open your browser and navigate to:

```
https://<BUCKET_NAME>.s3-website.fr-par.scw.cloud/
```

The bucket returns a `404` error until index files are present — this is expected. Proceed through the following steps:

1. Upload `error.html` from the `05_storage/` assets folder, then refresh the page. The custom error page should render.
1. Also test:

```
https://<BUCKET_NAME>.s3-website.fr-par.scw.cloud/unknown.html
```

The `error.html` page should serve for any unknown path.

1. Upload `index.html`, then refresh the root URL. The index page should now render.

-----

## 🔑 Section 7 — Cross-Origin Clearance: Configure CORS Rules

CORS (Cross-Origin Resource Sharing) rules tell browsers which external origins are permitted to request resources from your bucket. Without them, a browser will block any cross-origin request to your bucket — regardless of the object’s visibility.

1. Open the files in the `05_storage/assets/cors` folder.
1. Update `cors.json` to include the origins of your hands-on partner(s).
1. Update line 27 of both `cors-s3.html` and `cors-website.html` to retrieve `content.txt` from your partner(s)’ bucket domains.
1. Update the contents of `content.txt` with a message your partner(s) will retrieve.
1. Upload all four files — `content.txt`, `cors-s3.html`, `cors-website.html`, and `cors.json` — to your bucket.
1. In your browser, navigate to your bucket website and open the pages corresponding to `cors-s3.html` and `cors-website.html`. At this point, the cross-origin requests will fail — the CORS rules are not yet applied.
1. Apply the CORS configuration:

```bash
aws s3api put-bucket-cors \
  --bucket <BUCKET_NAME> \
  --cors-configuration file://cors.json
```

1. Return to your browser and repeat step 6. The cross-origin requests should now succeed.

> **Tower confirms:** CORS is enforced by the browser, not the server. The bucket returns the `Access-Control-Allow-Origin` header only for origins listed in the CORS configuration. An origin not in the list receives no header — and the browser blocks the response. Your partner’s bucket must also list your origin for the exchange to work in both directions.

### Clean Up

Once all scenarios have been tested, delete all resources created during this episode — both buckets and all objects within them.

-----

## 🗺️ Object Storage Architecture — The Cargo Hold Map

```
┌────────────────────────────────────────────────────────────────┐
│              ORGANISATION — default project                    │
│                                                                │
│  BUCKETS                                                       │
│  hands-on-bucket-{yourname}     (Console — Standard)          │
│  hands-on-bucket-cli-{yourname} (MinIO CLI — mixed classes)   │
│                                                                │
│  STORAGE CLASSES                                               │
│  hello-world.txt          Standard                            │
│  hello-again-world.txt    Glacier                             │
│                                                                │
│  ACCESS CONTROLS                                               │
│  Bucket policy:  granular-bucket-policy.json applied          │
│  Write:          /upload path — authorised user only          │
│  Read/List:      all users                                     │
│                                                                │
│  VERSIONING                                                    │
│  hello-world.txt: v1 / v2 / v3 — all retrievable by VersionId│
│                                                                │
│  WEBSITE                                                       │
│  Endpoint: https://<BUCKET_NAME>.s3-website.fr-par.scw.cloud/ │
│  Index:    index.html   Error: error.html                      │
│                                                                │
│  CORS                                                          │
│  Permitted origins: partner bucket domains                     │
└────────────────────────────────────────────────────────────────┘
```

-----

## 📋 Episode Debrief

*“The manifest is complete. Every item catalogued, every access route controlled, every version on record. The hold is secured. Thunderbird 2 is ready for the next mission.”*
*— Virgil Tracy, Thunderbird 2 Pilot*

In this episode, you have:

- ✅ Configured API key environment variables and the MinIO Client alias
- ✅ Created buckets via both the Scaleway Console and the MinIO Client
- ✅ Uploaded objects with `Standard` and `Glacier` storage classes
- ✅ Managed object visibility using both public setting and signed link strategies
- ✅ Applied a granular bucket policy scoped to specific paths and users
- ✅ Tested policy enforcement across four access scenarios with a partner
- ✅ Enabled bucket versioning and retrieved a specific object version by `VersionId`
- ✅ Configured the AWS CLI for Scaleway Object Storage
- ✅ Enabled the bucket website feature and served `index.html` and `error.html` from a bucket URL
- ✅ Configured CORS rules and verified cross-origin request behaviour in the browser
- ✅ Mapped the full Object Storage lifecycle through the SIPOC model

The cargo hold is locked and inventoried. In the next episode, we provision managed databases — adding a structured, persistent data layer to the infrastructure we have assembled.

-----

## 📡 Further Transmissions

- [Scaleway Object Storage documentation](https://www.scaleway.com/en/docs/storage/object/)
- [Scaleway Object Storage — storage classes](https://www.scaleway.com/en/docs/storage/object/concepts/#storage-class)
- [Scaleway Object Storage — bucket policies](https://www.scaleway.com/en/docs/storage/object/api-cli/bucket-policy/)
- [Scaleway Object Storage — bucket website](https://www.scaleway.com/en/docs/storage/object/how-to/use-bucket-website/)
- [Scaleway Object Storage with AWS CLI](https://www.scaleway.com/en/docs/storage/object/api-cli/object-storage-aws-cli/)
- [MinIO Client reference](https://docs.min.io/minio/baremetal/reference/minio-mc.html)

-----

*Estimated reading time: 14 minutes. Estimated hands-on time: 60–90 minutes.*

*This series is part of the **the-software-s-journey** publication on DEV.to — cloud infrastructure explained through the metaphors that make it stick.*
