# Development Rules

1. Keep business logic independent from the Kivy UI so it can be tested with the Python standard library.
2. Persist user records locally in SQLite; do not transmit personal or financial data to external services.
3. Validate race names, ISO dates, and non-negative integer yen amounts before saving.
4. Use parameterized SQL queries and never build SQL statements from user input.
5. Preserve a simple mobile-first layout and the dark navy / neon cyan / purple visual theme.
6. Add or update unit tests for normal, invalid, and boundary cases when behavior changes.
7. Keep dependencies minimal and document setup and test commands in README.md.
