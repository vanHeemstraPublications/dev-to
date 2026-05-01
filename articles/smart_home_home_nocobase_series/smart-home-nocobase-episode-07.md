-----

## title: “Smart Home with NocoBase! Ep.7: The Home Library”
published: false
description: “Episode 7: A smart home with no library is a home where every AI Employee starts from scratch. The AI Knowledge Base gives your employees access to your organisation’s documents, policies, and institutional knowledge — through RAG retrieval that finds the right page in the right manual, instantly.”
tags: [nocobase, ai, rag, knowledgebase]
cover_image: “https://raw.githubusercontent.com/vanHeemstraPublications/dev-to/main/images/smart-home-nocobase-episode-07.png”
series: “Smart Home with NocoBase Series”
canonical_url: “”
organization: “the-software-s-journey”

# Smart Home with NocoBase! 🏠

## Episode 7: The Home Library

> *“A smart home without a library is a home that knows nothing about itself. The manuals are in a drawer somewhere. The previous owner’s notes are in the garage. The maintenance history is in someone’s head.”*

-----

## The Problem With Manuals in a Drawer 📚

Every organisation has a library — product documentation, HR policies, technical specifications, past project reports, regulatory compliance guides, training materials. The problem is not the existence of that knowledge. The problem is retrieval.

An AI Employee without access to your library has to work entirely from what you tell it in the chat. Ask Ellis to write a proposal and it writes a good generic proposal. Ask Ellis to write a proposal referencing your specific pricing structure, your compliance certifications, and your standard SLA terms — and without a knowledge base, it either guesses or asks you to paste everything in manually.

The **AI Knowledge Base** solves this. It connects your document corpus to your AI Employees through **RAG** (Retrieval-Augmented Generation) — a retrieval pipeline that finds the relevant passages from your documents and injects them into the employee’s context before it responds.

-----

## 🗂️ SIPOC — The Home Library

|**Suppliers**                     |**Inputs**                                     |**Process**                                                                                                     |**Outputs**                                                                |**Customers**                                                                             |
|----------------------------------|-----------------------------------------------|----------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------|------------------------------------------------------------------------------------------|
|Organisation’s document library   |PDFs, Word docs, text files, knowledge articles|Upload → chunk into segments → embed each chunk via embedding model → store vectors in Vector Store             |A searchable vector library of document chunks                             |AI Employees with Knowledge Base skill — can search it                                    |
|AI Employee (at query time)       |User’s question + Knowledge Base skill         |Employee formulates a search query → Vector Store retrieves top-K matching chunks → chunks injected into context|AI response grounded in specific document passages, with source attribution|User — gets accurate, traceable answers from authoritative sources                        |
|Embedding model (from LLM service)|Text chunks from documents                     |Model converts text to high-dimensional vectors capturing semantic meaning                                      |Vector embeddings stored in the vector database                            |Similarity search — finds semantically relevant chunks even if exact keywords do not match|

-----

## What Is RAG? The Smart Librarian Explained 📖

**RAG — Retrieval-Augmented Generation** — is a pattern that makes AI responses grounded in specific documents rather than generic training data. The name describes the three stages:

**Retrieval:** Convert the user’s question into a vector (a numerical representation of its meaning). Search the vector library for the document chunks whose meaning is most similar to the question. Return the top K results.

**Augmentation:** Take those retrieved document chunks and inject them into the AI’s context window along with the original question. The employee now sees both the question and the relevant passages.

**Generation:** The AI generates a response that is grounded in the retrieved passages, not just its general training. It can cite specific sections, quote accurate figures, and explain policies precisely as written.

```
User: "What is our standard payment term for new enterprise clients?"

Without RAG:
  Ellis: "Payment terms vary by client. Typically 30-60 days is standard in B2B..."
  (generic answer from training data)

With RAG + knowledge base containing the Sales Playbook:
  Ellis: "According to the Sales Playbook (Section 4.2), standard payment terms
          for new enterprise clients are Net 30, with a 2% discount for payment
          within 10 days. Exceptions above $500K require Finance approval."
  (precise answer from your actual document)
```

-----

## The Four Components of the AI Knowledge Base 🏗️

The knowledge base system has four layers, each serving a specific role:

### 1. Vector Database — The Filing Room

The **Vector Database** is the storage infrastructure — the physical filing room where all the vectorised document chunks live. NocoBase supports connecting to external vector database services.

```
System Settings → AI Employees → Knowledge Base → Vector Database → Add

Supported types:
  - pgvector (PostgreSQL extension — simplest for existing Postgres deployments)
  - Qdrant (purpose-built vector database)
  - Weaviate (vector database with built-in schema)
  - Pinecone (managed cloud vector service)
  - Milvus (high-performance vector database)
```

For most organisations starting out, **pgvector** is the lowest-friction option — it runs inside your existing PostgreSQL database, no new infrastructure required.

### 2. Vector Store — The Filing System

A **Vector Store** is a named collection within the Vector Database — like a section of the filing room dedicated to a specific subject. A company might have:

- `product-documentation` — product manuals, spec sheets, user guides
- `hr-policies` — employee handbook, benefits guide, code of conduct
- `sales-playbook` — pricing, objection handling, contract terms
- `legal-contracts` — standard agreements, NDA templates, compliance docs

```
AI Knowledge Base → Vector Stores → Add New

Name:              sales-playbook
Description:       Sales process documentation, pricing, objection handling
Vector Database:   [Select the configured vector database]
Embedding Model:   text-embedding-3-small (OpenAI) or equivalent
```

The **Embedding Model** is critical — it determines how document chunks are converted to vectors. The same model must be used for both document embedding (when files are uploaded) and query embedding (when a question is searched). Use a dedicated embedding model, not a chat model.

### 3. Knowledge Base — The Document Collection

A **Knowledge Base** is a collection of documents uploaded to and indexed in a Vector Store. Multiple Knowledge Bases can share the same Vector Store.

```
AI Knowledge Base → Knowledge Bases → Add New

Name:         Sales Playbook Q2 2026
Description:  Current quarter's sales documentation
Vector Store: sales-playbook [select]
```

### 4. Documents — The Actual Files

Upload documents to a Knowledge Base:

```
AI Knowledge Base → [Select Knowledge Base] → Documents → Upload

Supported formats:
  - PDF (text extraction)
  - Word (.docx)
  - Text files (.txt, .md)
  - HTML pages

Chunking settings:
  Chunk size:    500-1000 tokens (balance between context and precision)
  Chunk overlap: 50-100 tokens (prevents cut-off context at chunk boundaries)
```

After uploading, NocoBase:

1. Extracts text from the document
1. Splits the text into chunks of the configured size
1. Sends each chunk to the embedding model
1. Stores the resulting vectors in the Vector Store
1. Marks the document as “indexed” and searchable

-----

## Connecting the Knowledge Base to Employees 🔗

Once documents are indexed, give employees access:

```
System Settings → AI Employees → [Edit employee] → Skills tab

Knowledge Base skill:
  Vector Stores: [Select which vector stores this employee can search]
  Permission:    Ask / Allow

→ Submit
```

An employee with Knowledge Base access will automatically search the library when a question might be answered by the documents. The search happens transparently — the user does not need to trigger it manually.

-----

## RAG in Action: The Smart Librarian at Work 🤖

**Scenario:** An HR manager asks Cole (with access to the `hr-policies` vector store):

```
User: "What is the process for requesting parental leave?"

Cole's internal process (invisible to user):
  1. Converts question to query vector
  2. Searches hr-policies vector store
  3. Retrieves top 3 chunks:
     - Section 5.1 "Parental Leave Policy Overview"
     - Section 5.3 "Leave Request Process"
     - Section 5.4 "Supporting Documentation Required"
  4. Injects chunks into context + generates response

Cole's response:
  "According to the Employee Handbook (Section 5.1-5.4):
   Parental leave requests must be submitted at least 8 weeks before the
   expected start date using Form HR-104. You will need to attach [...]
   Your line manager and HR must both approve before confirmation is issued.
   For urgent situations (early birth), the notice period requirement can
   be waived with written notification..."
```

The response cites specific section numbers, uses exact figures from the policy, and covers the process accurately — because it retrieved the actual document text.

-----

## Embedding Model Selection: The Library Classification System 📑

The embedding model determines how semantic similarity is computed. All documents and all queries must use the same model. Changing the embedding model requires re-indexing all documents.

Recommended embedding models:

|Model                   |Provider      |Context  |Cost  |Notes                                  |
|------------------------|--------------|---------|------|---------------------------------------|
|`text-embedding-3-small`|OpenAI        |8K tokens|Low   |Good general-purpose starting point    |
|`text-embedding-3-large`|OpenAI        |8K tokens|Medium|Higher quality, larger vectors         |
|`text-embedding-ada-002`|OpenAI        |8K tokens|Low   |Older but widely tested                |
|`embedding-001`         |Google Gemini |2K tokens|Low   |Integrates well with Gemini chat models|
|`nomic-embed-text`      |Ollama (local)|8K tokens|Free  |Local deployment, no API calls         |

Configure the embedding model in the Vector Store settings, not in the general LLM service list. The embedding model can be a different provider than the chat models used by employees.

-----

## Practical Knowledge Base Architecture for a Small Business 🏠

```
Vector Database: pgvector (running in existing PostgreSQL)

Vector Stores:
  ├── internal-docs
  │     Documents:
  │       ├── Employee Handbook v4.2.pdf
  │       ├── IT Security Policy 2026.pdf
  │       └── Benefits Guide Q1 2026.pdf
  │
  ├── product-docs
  │     Documents:
  │       ├── Product Manual v2.1.pdf
  │       ├── API Documentation.md
  │       └── Release Notes Q1 2026.md
  │
  └── sales-resources
        Documents:
          ├── Sales Playbook 2026.pdf
          ├── Pricing Sheet Q2 2026.pdf
          └── Objection Handling Guide.pdf

Employee knowledge base access:
  Cole    → internal-docs, product-docs (general assistant)
  Ellis   → sales-resources (proposal and email writing)
  Viz     → product-docs, sales-resources (analysis with product context)
  Rex     → [custom] legal-contracts (contract review)
```

-----

## Maintenance: Keeping the Library Current 📅

A knowledge base is only as useful as its documents are current. Old policies, superseded pricing sheets, and outdated product documentation produce confidently wrong responses — which is worse than no knowledge base at all.

Best practices:

**Version documents, not files.** Instead of overwriting `Pricing Sheet 2025.pdf`, add `Pricing Sheet Q2 2026.pdf` and archive the old one.

**Re-index after updates.** After uploading a new version of a document, delete the old document from the Knowledge Base (which removes its vectors) and upload the new one.

**Audit regularly.** Check which documents employees are citing in responses. If a policy document keeps being retrieved but the policy has changed, update the document immediately.

**Separate stores by update frequency.** Stable reference material (legal templates) in one store; frequently updated material (pricing) in another. This minimises re-indexing work.

-----

In **Episode 8**, we wire up the automation rules. Workflow LLM Nodes embed AI intelligence directly into NocoBase’s workflow engine — text chat, multimodal chat, structured output, and AI Employee approval nodes for human-in-the-loop processes.

-----

**🔗 Resources**

- **AI Knowledge Base Overview**: [docs.nocobase.com/ai-employees/knowledge-base](https://docs.nocobase.com/ai-employees/knowledge-base/)
- **Vector Database**: [docs.nocobase.com/ai-employees/knowledge-base/vector-database](https://docs.nocobase.com/ai-employees/knowledge-base/vector-database)
- **RAG**: [docs.nocobase.com/ai-employees/knowledge-base/rag](https://docs.nocobase.com/ai-employees/knowledge-base/rag)

-----

*🏠 Smart Home with NocoBase Series — building a fully connected AI-powered business application, one smart device at a time.*
