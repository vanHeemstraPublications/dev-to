---
title: "What has changed, LikeC4? ☁️ Ep.9"
series: "What has changed, LikeC4?"
part: 9
organization: "the-software-s-journey"
tags: [likec4, cli, aws, s3, cloudfront, deployment]
---

## Episode 9: Shipping the Documentation, Not Just Writing It

A model sitting in my editor helps exactly nobody who isn't me. This episode is about the full loop I've actually run on a real AWS project — from a multi-file `.c4` project to a live, interactive site stakeholders can click through on their own.

Real projects don't fit in one file, and I structure mine deliberately:

```
my-git-repository/
├── docs/
|   ├── specs.c4             # Define the vocabulary
│   ├── workspace.c4         # Define how the company projects are organized
│   ├── ecommerce/
|       ├── model.c4         # Define the system structure and relations
│       ├── views.c4         # Define the views that we need
└── ...
```

That's `specs.c4` from Episode 2, `workspace.c4` from Episode 3's corporate-landscape example, and `ecommerce/model.c4` plus `ecommerce/views.c4` holding everything built across Episodes 3 through 6 — all as one coherent logical model, just organized sensibly instead of jammed into a single unreadable file.

First, install the CLI:

```bash
npm install -D @likec4/cli
```

Confirm it's there:

```bash
likec4 --version
```

Then start the local dev server:

```bash
likec4 start
```

This opens a browser at `http://localhost:5173`, serving the diagrams with hot reload — change any `.c4` file and the view updates in the browser immediately, no manual refresh, no re-export step. This is where I spend ninety percent of my actual modeling time, watching the diagram react to the model as I write it.

When it's ready for an audience, I build a static site:

```bash
likec4 build -o ./dist
```

`./dist` now holds an `index.html` and an `assets` folder — the entire architecture portal, ready to host anywhere a static site can live. On the AWS project, I deliberately kept the S3 bucket private — no "static website hosting" toggle, no public bucket, block-all-public-access left checked — and put CloudFront in front of it instead, as the only thing actually allowed to reach the bucket's contents. Create the distribution pointing at the S3 origin, set `index.html` as the default root object, and within a few minutes of deployment, the CloudFront domain serves the whole interactive site over HTTPS.

The payoff shows up the moment I embed it somewhere else — a wiki page, a blog post, another piece of documentation entirely:

```html
<iframe
  src="https://abcd123456789.cloudfront.net/index.html?view=myView"
  width="100%"
  height="500px"
  style="border: 1px solid #e5e7eb; border-radius: 8px;"
></iframe>
```

That `?view=myView` query parameter is a contextual deep link — I can point a specific paragraph of documentation at the exact view relevant to it, not just the site's front page. And because the iframe points at a live CloudFront URL rather than a static screenshot, the moment I update the model and redeploy, every embedded iframe across every piece of documentation updates too, automatically, with no one needing to remember which slide deck also needs a new screenshot pasted in. That's the actual mechanism behind this whole series' promise: I don't chase down stale copies. There's only ever one copy.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| `likec4 start` | The multi-file `.c4` project | Serve diagrams locally with hot reload on every save | An immediate, always-current local preview | The architect (me), iterating on the model |
| `likec4 build -o ./dist` | The finished `.c4` project | Compile it into a static, self-contained web application | A deployable `index.html` + `assets` bundle | S3, CloudFront, or any static hosting target |
| CloudFront + private S3 | The built static site | Serve it securely over HTTPS, without a public bucket | A shareable, embeddable, always-live architecture portal | Stakeholders, and every iframe embedding a specific view |

Next stop: everything the CLI can do beyond `start` and `build` — exports, format checking, and validation.
