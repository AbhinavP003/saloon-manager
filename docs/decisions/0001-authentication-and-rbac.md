# ADR 0001: Authentication and Role-Based Access Control (RBAC)

## Status
Accepted (Implemented)

## Context
As the Saloon Manager project grows, we need to secure sensitive endpoints (like store management and booking status updates) and provide a personalized experience for customers. We require a system that handles user identity and enforces role-specific permissions (Customer, Store Owner, Admin).

## Decision
1. **JWT-Based Authentication**: Use standard OAuth2 with Password Flow and JWT tokens for stateless authentication.
2. **Pydantic for Schemas**: Use `pydantic-settings` for secure configuration and `Pydantic` models for user schemas.
3. **Role-Based Middlewares**: Use a `RoleChecker` dependency class to wrap FastAPI endpoints, ensuring only authorized roles can access specific routes.
4. **SQLite Compatibility**: Ensure all authentication logic (especially UUID and Timestamp handling) is compatible with SQLite (used for testing) and PostgreSQL (planned for production).
5. **Optional Auth for Bookings**: Allow anonymous bookings but link them to a user account if a valid token is provided.

## Consequences
- **Security**: Routes like `/api/v1/owner/*` are strictly protected.
- **Complexity**: All existing tests required migration to use authentication headers in their fixtures.
- **Developer Experience**: New developers must register an account and use the generated token for most API calls.
- **Performance**: Minimal overhead due to stateless JWT validation.

## Development Note (March 29, 2026)
During implementation, several "Response Validation Errors" occurred due to lazy-loading of nested relationships (`Store`, `Service`) in the `Booking` model after the database session was closed. We solved this by:
1. Creating "Short" versions of schemas (`StoreShort`, `ServiceShort`) for nested responses.
2. Explicitly loading required relationships using `selectinload` when returning objects from write endpoints.
