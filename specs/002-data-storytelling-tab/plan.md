# Implementation Plan: Data Storytelling Tab

**Branch**: `002-data-storytelling-tab` | **Date**: May 13 2026 | **Spec**: [spec.md](./specs/002-data-storytelling-tab/spec.md)
**Input**: Feature specification from `/specs/002-data-storytelling-tab/spec.md`

## Summary

This feature adds a data storytelling tab to the Quortol application that enables users to interactively explore visual data stories. The implementation uses a Dash/Plotly-based application with page-based architecture for extensibility, where developers can add new dashboards as code pages. Users can browse multiple dashboards, filter visualizations, and compare metrics side-by-side.

**Technical Approach**: Dash/Plotly application integrated into existing Flask server (port 5000) using `server=app` pattern. Dash handles all data serving and routing automatically via callbacks, with page-based navigation at `/data-storytelling/*` prefix.

## Technical Context

**Language/Version**: Python 3.8+  
**Primary Dependencies**: Dash, Plotly, Flask  
**Storage**: Static JSON files (code-defined dashboards)  
**Testing**: pytest (backend), Jest (frontend)  
**Target Platform**: Desktop-first web application  
**Project Type**: Web application (Dash/Flask server)  
**Performance Goals**: p95 response time under 500ms, visualization render under 2 seconds  
**Constraints**: Desktop-first v1 (no mobile), standard deployment process (no hot-reloading)  
**Scale/Scope**: Multiple dashboard pages, up to 10,000 data points per chart

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **Code Quality**: No implementation details in specification (technology-agnostic requirements)  
✅ **Testing Standards**: Testable requirements defined (independent tests for each user story)  
✅ **User Experience**: Loading, error, and edge cases documented  
✅ **Performance Requirements**: p95 <500ms target matches spec requirements  
✅ **Simplicity & Maintainability**: Flat page structure, code-first approach  

**Status**: All gates pass. No complexity violations.

## Project Structure

### Documentation (this feature)

```text
specs/002-data-storytelling-tab/
├── spec.md              # Feature specification (/speckit.specify command)
├── plan.md              # This file (/speckit.plan command)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── checklists/
    └── requirements.md  # Specification quality checklist
```

### Source Code (repository root)

```text
backend/
├── dashboards/          # Dashboard page definitions (code files)
│   ├── __init__.py
│   └── [dashboard_name]/
│       ├── page.py      # Dash page code
│       └── data.py      # Data source configuration
├── routes/
│   └── dashboard.py     # Dashboard serving routes
├── services/
│   └── visualization.py # Plotly visualization services
└── app.py               # Dash application entry point

frontend/
└── src/
    └── router/
        └── index.js     # Updated with Data Storytelling route

tests/
├── backend/
│   ├── test_dashboards.py
│   └── test_visualizations.py
└── frontend/
    └── test_dashboards.js
```

**Structure Decision**: Dashboard pages are stored as code files in `backend/dashboards/` directory, following the code-first approach. Each dashboard is a separate subdirectory with its page.py and data.py files.

## Integration Approach

**Dash-Flask Integration Pattern**:

```python
# backend/app.py
from flask import Flask
from dash import Dash

def create_app(config_class=None):
    # Existing Flask app setup
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Register existing Flask routes/blueprints
    from .routes.blog import blog_bp
    from .routes.portfolio import portfolio_bp
    app.register_blueprint(blog_bp, url_prefix='/api/blog')
    app.register_blueprint(portfolio_bp, url_prefix='/api/portfolio')
    
    # Register Dash application within Flask (single server, port 5000)
    dash_app = Dash(__name__, 
                    server=app,  # <-- Uses existing Flask server
                    url_prefix='/data-storytelling')
    
    # Register dashboard pages with Dash
    from dashboards import register_dashboards
    register_dashboards(dash_app)
    
    return app
```

**Key Integration Points**:
1. **Single Server**: Dash runs on port 5000 alongside existing Flask routes
2. **Shared Config**: Both Vue API and Dash pages use same Flask configuration
3. **URL Routing**: 
   - Vue API: `/api/blog`, `/api/portfolio`
   - Dash pages: `/data-storytelling/{dashboard_name}`
4. **No Port Conflicts**: Dash uses existing Flask request handling
5. **Callback Routing**: Dash automatically handles data callbacks at `/data-storytelling/.../dash-callbacks/...`
6. **Shared Database**: Dash callbacks can query same database as Flask routes
7. **Shared Auth**: Dash pages can use existing Flask authentication if needed

**Architecture Overview**:

```
┌─────────────────────────────────────────────────────────────┐
│              Single Flask Server (Port 5000)                │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────┐  ┌─────────────────────────────┐  │
│  │ Vue Router (SPA)    │  │ Dash Application            │  │
│  │                     │  │ (Built on Flask)            │  │
│  │ - /blog             │  │ - /data-storytelling/*      │  │
│  │ - /portfolio        │  │   └─ Dashboard pages        │  │
│  │                     │  │   └─ Plotly charts          │  │
│  └─────────────────────┘  └─────────────────────────────┘  │
│                           │                                   │
│  ┌─────────────────────┐  │                                   │
│  │ Flask Routes        │  │                                   │
│  │ - /api/blog         │  │                                   │
│  │ - /api/portfolio    │  │                                   │
│  │ - /api/auth         │  │                                   │
│  └─────────────────────┘  │                                   │
└───────────────────────────┴──────────────────────────────────┘
```

**Why This Works**:
- Dash is built on Flask - can register as Flask extension
- `server=app` tells Dash to use the existing Flask server instead of creating a new one
- `url_prefix` routes Dash pages under `/data-storytelling/` prefix
- All routes (Vue API, Flask routes, Dash pages) serve from same origin
- No CORS issues, same authentication context

**Frontend Router Integration**:

```javascript
// frontend/src/router/index.js
const routes = [
  // Existing routes
  { path: '/blog', name: 'blog', component: BlogList },
  
  // NEW: Data Storytelling navigation
  { path: '/data-storytelling', name: 'data-storytelling', redirect: '/data-storytelling/strikes' },
  { path: '/data-storytelling/:dashboard', name: 'dashboard-view', component: () => import('@/views/DataStorytelling.vue') }
]
```

**What This Means for Development**:

1. **No Separate Server**: Dash runs on the same Flask server as existing routes
2. **Development**: `python -m backend.app` starts both Vue API and Dash pages
3. **Production**: Single deployment, single port, single process
4. **Callbacks**: Dash callbacks automatically handle data requests (no manual API needed)
5. **Routing**: Vue router navigates to `/data-storytelling/*` pages, Dash serves them
6. **Data Flow**: Vue → Flask API (existing) | Vue → Dash callbacks (automatic)

## Complexity Tracking

> **No violations of simplicity principles detected.**

The implementation follows flat structure for dashboard pages, inline comments explain WHY code is structured that way, and complexity is minimized through the code-first approach where developers define dashboards directly rather than through a complex admin interface.
