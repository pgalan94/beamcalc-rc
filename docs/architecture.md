# 🧱 Architecture Overview

This document describes the architectural decisions, layering, and development conventions of the **beamcalc-rc** project.

The goal is to ensure:

* scalability
* maintainability
* testability
* clear separation of concerns

---

# 🏗️ High-Level Architecture

The project follows a **layered architecture inspired by Clean Architecture and DDD (Domain-Driven Design)**.

```
beamcalc/
  domain/        ← Core business logic (engineering rules)
  application/   ← Use cases and orchestration
  infra/         ← External integrations (solver, database, adapters)
  api/           ← Public interface for users
  mcp/           ← AI/LLM integration layer (JSON-based)
  utils/         ← Generic utilities
```

---

# 🔁 Dependency Rules (CRITICAL)

Dependencies must always point **inward**.

```
api        → application → domain
mcp        → api
infra      → domain
domain     → (no dependencies)
```

## Rules:

* `domain` must NOT depend on any other layer
* `application` depends only on `domain`
* `infra` implements interfaces defined in `application`
* `api` orchestrates `application`
* `mcp` uses `api`, never domain or solver directly

---

# 🧠 Domain Layer (`domain/`)

This is the **core of the system** and contains all engineering logic.

## Responsibilities:

* Represent structural concepts
* Enforce business rules
* Remain independent from frameworks and external libraries

## Structure:

```
domain/
  models/         ← Beam, Load, Section, Material, Support, Results
  value_objects/  ← Geometry, Units, Coordinates
  services/       ← Complex domain logic
  exceptions/     ← Domain-specific errors
```

## Rules:

* No external dependencies (e.g., no AnaStruct, no JSON)
* Use explicit objects (no dict-based logic)
* Keep models cohesive and focused

---

# ⚙️ Application Layer (`application/`)

This layer orchestrates **use cases**.

## Responsibilities:

* Coordinate domain objects
* Define workflows (create beam, add load, solve, etc.)
* Define interfaces for external systems

## Structure:

```
application/
  use_cases/      ← One file per action (create_beam, solve_beam, etc.)
  interfaces/     ← Solver and repository abstractions
  services/       ← Light orchestration (optional)
  dto/            ← Data transfer objects
```

## Rules:

* No direct use of external libraries
* Depends only on `domain`
* Each use case should be small and focused

---

# 🏗️ Infrastructure Layer (`infra/`)

This layer contains all **external integrations**.

## Responsibilities:

* Implement solver logic (AnaStruct)
* Handle persistence (if needed)
* Map external data to domain models

## Structure:

```
infra/
  solver/         ← FEM solver implementations
  adapters/       ← Mapping between external libs and domain
  repositories/   ← Persistence implementations
  database/       ← DB connection and migrations
```

## Rules:

* Can depend on external libraries (e.g., AnaStruct)
* Must implement interfaces from `application`
* Must NOT contain business logic

---

# 🎯 API Layer (`api/`)

This is the **public interface** of the library.

## Responsibilities:

* Provide a clean, simple interface for users
* Hide internal complexity
* Offer fluent and intuitive usage

## Example usage:

```python
beam = Beam(length=5)
beam.add_support("pin", x=0)
beam.add_support("roller", x=5)
beam.add_load(PointLoad(10, x=2.5))

results = beam.solve()
```

## Rules:

* Should be easy to use without reading internal code
* Should not contain business logic
* Should delegate to `application`

---

# 🤖 MCP Layer (`mcp/`)

This layer enables integration with **LLMs via Model Context Protocol (MCP)**.

## Responsibilities:

* Expose operations via JSON
* Convert between JSON and domain objects
* Provide tool-like interface for AI systems

## Structure:

```
mcp/
  handlers/   ← Entry points (create_beam, solve, etc.)
  schemas/    ← JSON schemas
  adapters/   ← JSON ↔ domain conversion
  server/     ← MCP server setup
```

## Rules:

* Must NOT access `domain` directly
* Must go through `api`
* Input/output must always be JSON-compatible

---

# 🧪 Testing Strategy

Tests are organized outside the package:

```
tests/
  unit/
  integration/
```

## Guidelines:

* Unit tests for domain and solver logic
* Integration tests for full workflows
* Avoid testing implementation details
* Focus on behavior and correctness

---

# 🧰 Utilities (`utils/`)

Contains generic helpers.

## Allowed:

* logging
* configuration
* pure helper functions

## Not allowed:

* business logic
* domain rules

---

# 🚫 Anti-Patterns (DO NOT DO)

* ❌ Business logic inside `api`
* ❌ Direct use of solver (AnaStruct) outside `infra`
* ❌ Passing raw dicts instead of domain objects
* ❌ Large functions (>50 lines)
* ❌ Tight coupling between layers
* ❌ MCP accessing domain directly

---

# 🧭 Design Principles

* Single Responsibility Principle (SRP)
* Explicit over implicit
* Composition over inheritance
* Domain-first design
* Testability by design

---

# 🚀 Evolution Strategy

The architecture is designed to support:

* Multiple solver backends
* Advanced structural analysis (continuous beams, non-linear behavior)
* AI integration via MCP
* Future SaaS/API exposure

---

# 📌 Final Note

This architecture is intentionally designed to:

> Keep the domain pure, the system modular, and the product extensible.

Any new feature must respect these boundaries.
