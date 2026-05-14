# Research: Data Storytelling Tab

**Created**: May 13 2026  
**Feature**: 002-data-storytelling-tab

## Technology Decisions

### 1. Dash/Plotly vs lets-plot

**Decision**: Use Dash/Plotly instead of lets-plot for the data storytelling application

**Rationale**: 
- Dash provides a framework for building interactive web applications with page navigation
- Plotly offers rich interactive charts with hover, zoom, and filter capabilities
- Dash supports Flask backend integration (matches existing project architecture)
- Dash has built-in multi-page navigation support
- Plotly charts can be embedded directly in Dash pages

**Alternatives Considered**:
- **lets-plot**: Used in previous IPL visualization, but better for static PNG generation rather than interactive web apps
- **Recharts**: React-based, requires frontend framework integration
- **Chart.js**: Static chart library, limited interactivity

**Conclusion**: Dash/Plotly is the optimal choice for interactive, extensible dashboard pages.

### 2. Page-based Architecture

**Decision**: Each dashboard is a separate page in the Dash application

**Rationale**:
- Clear separation of concerns for each dashboard
- Easy to add new dashboards as new pages
- Dash handles navigation automatically via URL routing
- Users can bookmark or share specific dashboard URLs

**Alternatives Considered**:
- Single-page application with dashboard tabs
- URL query parameters for dashboard selection

**Conclusion**: Page-based architecture provides better extensibility and URL sharing.

### 3. Code-First Dashboard Creation

**Decision**: Dashboards are defined as code files, not admin interface

**Rationale**:
- Developers have full control over dashboard structure
- Version control for dashboard definitions
- No need for admin UI development
- Simpler to maintain and test

**Alternatives Considered**:
- Admin interface for creating dashboards
- JSON configuration files

**Conclusion**: Code-first approach aligns with existing project practices and developer workflow.

### 4. Navigation Structure

**Decision**: Dash navigation via app.layout with multi-page routing

**Rationale**:
- Dash provides built-in navigation component (dcc.Location, dcc.Link)
- Standard web navigation patterns familiar to users
- Clean URL structure for each dashboard

**Implementation**: Use Dash's `app.layout` to define page structure with navigation menu, and `dcc.Location` for URL routing.

### 5. Data Source Pattern

**Decision**: Static JSON files with code-defined structure

**Rationale**:
- Matches existing project pattern (static JSON serving)
- Simple to version and deploy
- No database complexity for v1
- Can be extended to API endpoints later

**Structure**: Each dashboard has its own data.py file that loads JSON and serves via Flask routes.

## Integration Approach

**Dashboard Serving Strategy**: Dash application integrated into existing Flask backend

**Decision**: Dash application will run on its own route within the existing Flask server, not as a separate port.

**Rationale**:
- Single port deployment (port 5000)
- Easier to share authentication with existing routes
- Consistent with existing project architecture
- Dash is built on Flask - can register dash routes alongside existing Flask routes

**Implementation**: Dash routes will be registered at `/data-storytelling/` prefix within the Flask app, accessible alongside `/api/blog`, `/blog`, etc.

## Performance Considerations

**Chart Rendering**: Plotly renders client-side in browser
- Target: 95% of visualizations render within 2 seconds
- Large datasets (10,000+ points) may need sampling or aggregation
- Consider using `plotly.express` for simple charts, `plotly.graph_objects` for complex ones

**Page Loading**: Dash serves pages server-side
- Target: Initial page load under 1 second
- Use lazy loading for visualization components if needed

**Port Conflict**: Dash and Flask share the same server instance
- Dash uses Flask's request handling
- No additional port needed
- Existing port 5000 serves both Vue API and Dash pages

## Testing Strategy

**Backend Tests**: pytest for dashboard code
- Test data loading
- Test page layout generation
- Test visualization rendering

**Frontend Tests**: Jest for Vue components
- Test interactivity (hover, click)
- Test filter behavior
- Test navigation between dashboards

**Integration Tests**: Test Dash-Flask integration
- Test dashboard page serving via Flask route
- Test data loading from Dash callbacks
- Test authentication with existing auth system

## Security Considerations

**Data Access**: No user authentication required for viewing dashboards
- Use existing auth system if sensitive data needed
- Sanitize all user inputs for filters

**Code Deployment**: Dashboard code deployed with standard process
- Validate dashboard configuration before serving
- Handle invalid configurations gracefully (show error page)

**Cross-Origin**: Vue frontend and Dash served from same origin
- No CORS issues (both on localhost:5000)
- Vue can directly access Dash callbacks via AJAX

## Deployment Considerations

**Flask Extension**: Dash registered as Flask extension
- Single WSGI application
- No need to configure separate Dash server
- Can use existing Flask configurations for production
