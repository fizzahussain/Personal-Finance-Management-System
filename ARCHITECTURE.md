# Architecture

The Personal Finance Analytics System uses a layered architecture that separates user interaction, business logic, storage, reporting, and infrastructure concerns

## Architecture overview

```text
User
  |
  v
Command line interface
  |
  +-----------------------+
  |                       |
  v                       v
Transaction services    Budget services
  |                       |
  +-----------+-----------+
              |
              v
        Report services
              |
              v
       Storage selection
              |
       +------+------+ 
       |      |      |
       v      v      v
      JSON   CSV   SQLite