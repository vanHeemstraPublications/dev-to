---
title: "Figurines like Picos 📜 Ep.2"
series: "Figurines like Picos"
part: 2
organization: "the-software-s-journey"
tags: [krl, rulesets, pico, event-driven]
---

## Episode 2: The Instruction Sheet That Makes a Figurine Come Alive

You know that little fold-out instruction sheet that comes tucked inside a figurine's box — the one showing you exactly how the joints articulate, which accessories click into which hands? For a pico, that instruction sheet is called a ruleset, and the language it's written in is KRL, which stands for the Kinetic Rule Language — and if there is a more perfect name for "the language that makes a figurine kinetic," I have not heard it.

A ruleset is a bundle of rules, and every rule is an event-condition-action triple: when this happens, and if this is true, then do this. Here's the smallest possible instruction sheet I could write for a figurine that waves hello when you press its little button:

```krl
ruleset io.example.greeter {
  meta {
    name "Greeter Figurine"
    description "Waves hello when greeted"
    author "a very happy collector"
    logging on
  }

  global {
    greeting = function(name) {
      "Hello there, " + name + "! *waves enthusiastically*"
    }
  }

  rule wave_hello {
    select when figurine greet
    pre {
      name = event:attr("name") || "friend"
    }
    send_directive("greeting") with
      message = greeting(name)
  }
}
```

Read that `select when figurine greet` line as the figurine's little ear, tuned to exactly one kind of knock: a `greet` event in the `figurine` domain. The `pre` block reads whatever came along with the knock — here, a `name` attribute — and falls back to "friend" if nobody bothered to say who they were. And `send_directive` is the figurine actually striking its pose: a structured little response any client can read and render however it likes.

Figurines remember things, too, and this is where KRL quietly saves you from ever needing a separate database. Persistent variables — written as `ent:something` — live inside the pico itself, set inside a rule's action, and they survive exactly as long as the figurine sits on its shelf:

```krl
rule count_greetings {
  select when figurine greet
  always {
    ent:greetingCount := (ent:greetingCount || 0) + 1
  }
}
```

Every time this figurine is greeted, it quietly ticks up its own personal count of how many times it's been said hello to — no external table, no ORM, just a number the figurine itself is keeping track of, the way a well-loved figurine keeps its own little scuffs and stories.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| Ruleset author | An event-condition-action rule written in KRL | Define a `select when` trigger, a `pre` condition, and an action | An installable rule that gives the figurine a new reflex | The pico that installs this ruleset |
| Pico Engine's event-evaluation cycle | An incoming event (e.g. `figurine greet`) | Match the event against every installed rule's `select when` clause | The fired rule's action, run in order | The requester who raised the event, other listening rules |
| Persistent variables (`ent:*`) | A value set inside a rule's action | Store it durably inside the pico | State that survives across every future event | Future rules reading the same `ent:` variable |

Next stop: figurines don't just appear on the shelf out of nowhere — meet the workshop that assembles every one of them: Wrangler.
