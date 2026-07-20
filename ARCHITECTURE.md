# Architecture

The project follows clean architecture principles.

## Layers

### Domain
Contains financial entities, enums, exceptions, and business rules.

### Application
Contains services, use cases, and interfaces.

### Infrastructure
Contains CSV, JSON, SQLite, logging, and configuration implementations.

### Analytics
Contains data processing, statistics, and visualizations.

### Presentation
Contains the command-line interface.

### Utilities
Contains reusable helpers, validators, decorators, and file utilities.

## Dependency Rule

Core domain code should not depend on databases, command-line tools,
or visualization libraries. Outer layers may depend on inner layers.