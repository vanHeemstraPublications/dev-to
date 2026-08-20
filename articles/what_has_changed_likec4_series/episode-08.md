---
title: "🌍 Where This Thing Actually Runs"
series: "What has changed, LikeC4?"
part: 8
organization: "the-software-s-journey"
tags: [likec4, dsl, deployment, infrastructure]
---

## 🌍 Where This Thing Actually Runs

Everything so far has been the *logical* model — what the system is made of, conceptually, regardless of where any of it physically lives. Sooner or later, though, someone asks the other question: "which of this is actually in the EU region, and which VM is it running on?" That's a different layer entirely, and LikeC4 keeps it genuinely separate — a Deployment Model, its own physical structure of deployment nodes, that references the logical model and inherits its relationships rather than duplicating them.

Same discipline as before: declare the kinds first.

```
specification {
  deploymentNode environment
  deploymentNode zone
  deploymentNode kubernetes {
    style {
      color blue
      icon tech:kubernetes
      multiple true
    }
  }
  deploymentNode vm {
    notation 'Virtual Machine'
    technology 'VMware'
  }
}
```

Then the actual physical hierarchy, nested exactly like the logical model was:

```
deployment {
  environment prod {
    zone eu {
      zone zone1 {
        vm vm1
        vm vm2
      }
      zone2 = zone {
        vm1 = vm
        vm2 = vm
      }
    }
  }
}
```

Nodes can carry the same kind of properties logical elements can — tags, technology, a Markdown description, a link:

```
deployment {
  environment prod 'Production' {
    #live #sla-customer
    technology 'OpenTofu'
    summary 'Production environment'
    description '''
      ## Detailed description
      With **Markdown** support
    '''
    link https://likec4.dev

    zone eu {
      title 'EU Region'
    }
  }
}
```

Here's the part that actually connects this whole physical layer back to everything I've built in this series so far: `instanceOf` *deploys* a logical element onto a deployment node.

```
deployment {
  environment prod {
    zone eu {
      zone zone1 {
        instanceOf frontend.ui
        instanceOf backend.api
      }
      zone zone2 {
        ui = instanceOf frontend.ui
        api1 = instanceOf backend.api
        api2 = instanceOf backend.api
      }
      db = instanceOf database
    }
  }
}
```

Two instances of `backend.api`, same logical element, deployed twice — that's a genuinely common real-world shape (a backend running in two zones for redundancy) that the logical model alone can't express, because the logical model doesn't know or care about redundancy; it only knows the API exists. The deployment layer is where "how many, and where" actually gets recorded.

And deployment relationships can say things the logical model never needed to — replication between a primary and a standby, say, something that only makes sense once you're talking about two physical instances of the same logical database:

```
deployment {
  environment prod {
    vm vm1 {
      db = instanceOf database 'Primary DB'
    }
    vm vm2 {
      db = instanceOf database 'Standby DB'
    }

    vm2.db -[streaming]-> vm1.db {
      #next, #live
      title 'replicates'
      description 'Streaming replication'
    }
  }
}
```

That's a relationship between two *instances* of the same logical element — something I'd never model at the logical level, because logically, a database doesn't replicate to itself. Physically, it very much does, and now that fact lives exactly where it belongs.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| The architect (me) | Real infrastructure structure (environments, zones, VMs, clusters) | Declare deployment node kinds, then nest actual nodes under `deployment {}` | A physical hierarchy, separate from but linked to the logical model | Deployment views (next episodes touch on this indirectly) |
| `instanceOf` | A logical element (e.g. `backend.api`) and a target deployment node | Deploy that element onto the node, possibly more than once | Concrete instances representing "this API, running here, and also here" | Anyone asking where something actually runs |
| Deployment-specific relationships | Two instances of the same or different logical elements | Define connections that only make sense physically (e.g. replication) | Infrastructure-level facts the logical model was never meant to hold | Ops-focused diagrams and audits |

Next stop: taking everything built across a whole real project — multiple files, a full logical and physical model — and putting it in front of actual stakeholders on the open internet.
