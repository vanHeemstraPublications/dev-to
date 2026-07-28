---
title: "Species with AtomicServer 🖊️ Ep.7"
series: "Species with AtomicServer"
part: 7
organization: "the-software-s-journey"
tags: [atomicserver, atomicdata, agents, identity, did]
---

## Episode 7: The Ranger's Signature

No field observation means much without knowing who made it. A reserve's records are only as trustworthy as the ranger's signature beside each entry — proof that a specific, accountable person stood there and made that call. In AtomicServer, that signature belongs to the Agent, and without one, you may wander the reserve and read every specimen on file, but you may not add or change a single entry.

An Agent is rather like a user account, except it carries its own proof of authorship built in: it signs every change — every commit — it makes to the data, so that anyone else can verify, independently, that this specific Agent really did make this specific change. Agents are identified by a DID derived from their own public key, in the form `did:ad:{publicKey}`, which means an Agent's identity is not something a central authority hands out — it can be used on any AtomicServer anywhere, without first registering with that particular reserve. Show up with your key pair, and you are already, in a sense, credentialed.

Getting your own ranger credentials, in practice, means using the demo invite on atomicdata.dev, or the `/setup` invite on your own server, and clicking "Accept as new user" — the app generates a key pair on the spot and your Agent is born. The one thing worth guarding carefully afterward is your agent secret, found on the User Settings page: it is what you use to log back in, and losing it means losing the account outright, with no recovery path, the way losing a specimen tag in the field means that observation can never quite be re-attached to its rightful ranger. Setting up the root Agent — the one ranger with full write access to the whole Drive — follows the same `/setup` invite, used exactly once; after that it locks, though restarting the server with `--initialize` will re-open it if the root Agent ever needs replacing.

### SIPOC

| Supplier | Input | Process | Output | Customer |
|---|---|---|---|---|
| AtomicServer setup invite | A new user clicking "Accept as new user" | Generate a key pair and derive a `did:ad:{publicKey}` identity | A newly created Agent, portable across any AtomicServer | The person now able to sign commits |
| Agent | An intended change to a Resource | Sign the change (commit) with the Agent's private key | A verifiable, attributable edit | Other observers verifying who made the change |
| Root `/setup` invite (one-time use) | The first Agent to accept it | Grant write access to the whole Drive | A root Agent with full editing authority | The reserve's first and primary ranger |

Next stop: every signed change deserves a record of its own — see how each edit becomes an entry in the reserve's field journal: the Commit.
