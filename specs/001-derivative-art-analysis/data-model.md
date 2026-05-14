# Data Model: Derivative Art Analysis

**Feature**: Derivative Art Analysis  
**Date**: May 13 2026  
**Source**: [specs/001-derivative-art-analysis/spec.md](../spec.md)

---

## Entities Overview

This data model defines the core entities used throughout the derivative art analysis system. All entities are derived from historical art records stored in static JSON files.

---

## Entity: Artwork

**Description**: Represents an individual piece of art with metadata, attribution, and derivative metrics.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier (UUID) |
| `title` | string | Yes | Title of the artwork |
| `artist_id` | string | Yes | Reference to Artist entity |
| `date_created` | string | Yes | ISO 8601 date string |
| `medium` | string | Yes | Art medium (oil, sculpture, digital, etc.) |
| `movement_id` | string | Yes | Reference to Art Movement entity |
| `current_location` | string | No | Museum/collection location |
| `provenance` | array | No | List of ownership history entries |
| `source_urls` | array | No | Links to original data sources |
| `originality_score` | number | No | 0-100 scale, null if insufficient data |
| `influence_count` | number | No | Number of documented influences |
| `created_at` | datetime | Yes | Record creation timestamp |
| `updated_at` | datetime | Yes | Record last update timestamp |

### Validation Rules

- `id`: Must be unique UUID v4
- `title`: 1-200 characters, no special characters
- `date_created`: Must be valid ISO 8601, historical (≤ current year)
- `originality_score`: If present, must be 0-100
- `artist_id` and `movement_id`: Must reference existing entities

### Relationships

- **Artist**: Many-to-One (artwork belongs to artist)
- **Art Movement**: Many-to-One (artwork belongs to movement)
- **Influence Chains**: One-to-Many (artwork can be influenced by or influence others)

---

## Entity: Artist

**Description**: Represents an individual creator with career timeline, influence network, and originality metrics.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier (UUID) |
| `name` | string | Yes | Full name (birth name or known name) |
| `birth_year` | number | No | Birth year or range |
| `death_year` | number | No | Death year or range |
| `nationality` | string | No | Country/region of origin |
| `period` | string | No | Active period (e.g., "Renaissance", "19th century") |
| `movement_ids` | array | No | List of associated movements |
| `originality_score` | number | No | Average originality across works |
| `influence_density` | number | No | Influences relative to peer group |
| `total_works` | number | No | Count of documented works |
| `influences_count` | number | No | Documented predecessors |
| `influenced_count` | number | No | Documented successors |
| `source_urls` | array | No | Links to original data sources |
| `created_at` | datetime | Yes | Record creation timestamp |
| `updated_at` | datetime | Yes | Record last update timestamp |

### Validation Rules

- `id`: Must be unique UUID v4
- `name`: 1-100 characters, alphabetic and spaces only
- `birth_year` / `death_year`: Must be positive integers, death ≥ birth if both present
- `originality_score`: If present, must be 0-100
- `influences_count` / `influenced_count`: Must be non-negative integers

### Relationships

- **Artworks**: One-to-Many (artist created multiple works)
- **Art Movements**: Many-to-Many (artist can belong to multiple movements)
- **Influence Chains**: Many-to-Many (bidirectional influence network)

---

## Entity: Art Movement

**Description**: Represents a stylistic period or movement with characteristic influence patterns and timeline.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier (UUID) |
| `name` | string | Yes | Movement name (e.g., "Impressionism") |
| `start_year` | number | Yes | Movement start year |
| `end_year` | number | Yes | Movement end year |
| `origin_country` | string | No | Geographic origin |
| `description` | string | No | Movement characteristics |
| `parent_movement_id` | string | No | Parent movement (if derived) |
| `total_artists` | number | No | Artists associated with movement |
| `total_works` | number | No | Total documented works |
| `originality_trend` | number | No | Average trend over movement period |
| `source_urls` | array | No | Links to original data sources |
| `created_at` | datetime | Yes | Record creation timestamp |
| `updated_at` | datetime | Yes | Record last update timestamp |

### Validation Rules

- `id`: Must be unique UUID v4
- `name`: 1-100 characters, no special characters
- `start_year` / `end_year`: Must be positive integers, end ≥ start
- `originality_trend`: If present, must be a valid decimal number
- `parent_movement_id`: If present, must reference existing movement

### Relationships

- **Artworks**: One-to-Many (movements contain artworks)
- **Artists**: One-to-Many (artists belong to movement)
- **Sub-movements**: One-to-Many (movements can have derived sub-movements)

---

## Entity: Influence Chain

**Description**: Represents the relationship between artworks or artists showing the flow of artistic influence.

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier (UUID) |
| `source_entity_id` | string | Yes | Entity that influenced (artist_id or artwork_id) |
| `source_type` | string | Yes | "artist" or "artwork" |
| `target_entity_id` | string | Yes | Entity that was influenced |
| `target_type` | string | Yes | "artist" or "artwork" |
| `influence_strength` | number | No | 0-1 scale, null if unquantified |
| `evidence_type` | string | No | "documentary", "stylistic", "historical" |
| `source_citations` | array | No | List of scholarly references |
| `confidence_level` | string | No | "high", "medium", "low", "speculative" |
| `notes` | string | No | Additional context |
| `created_at` | datetime | Yes | Record creation timestamp |
| `updated_at` | datetime | Yes | Record last update timestamp |

### Validation Rules

- `id`: Must be unique UUID v4
- `source_entity_id` / `target_entity_id`: Must reference existing entities
- `source_type` / `target_type`: Must be "artist" or "artwork"
- `influence_strength`: If present, must be 0-1
- `confidence_level`: Must be one of: "high", "medium", "low", "speculative"

### Relationships

- **Bidirectional**: Can be traversed forward (influenced by) and backward (influenced)
- **Artwork/Artist**: Links to either type of entity

---

## Entity: Derivative Metric

**Description**: Represents quantitative measures of originality, influence density, and trend analysis. This is not stored as a separate entity but computed from Artwork, Artist, and Movement entities.

### Metric Types

| Metric | Scale | Description |
|--------|-------|-------------|
| **Originality Index** | 0-100 | Score measuring departure from established patterns within a movement |
| **Influence Density** | Ratio | Number of documented influence connections per entity relative to peer group |
| **Trend Shift** | Decimal | Change in originality scores across movement periods |

### Computation Rules

- **Originality Index**: 
  - Calculated as average distance from movement centroid in feature space
  - Null if insufficient data (< 3 documented works)
  
- **Influence Density**:
  - `influences_count / peer_group_size`
  - Normalized to 0-1 scale
  
- **Trend Shift**:
  - `originality_score_current_period - originality_score_previous_period`
  - Can be positive (increasing originality) or negative (increasing derivative)

---

## Data Relationships Summary

```
Artist ──────────┐
   │              │
   │ One-to-Many  │ Many-to-Many
   ▼              │
Artwork          │
   │              │
   │ Many-to-One  │ One-to-Many
   ▼              ▼
Art Movement ────┼───┐
                  │   │
                  │   └── Many-to-Many (via Influence Chain)
                  │
              ┌───┴───┐
              │       │
           Artwork  Artist
              │       │
              └───────┘
                    │
              Influence Chain (bidirectional)
```

---

## State Transitions

**No state transitions** - All entities represent historical art records that are treated as static data. Once created, records do not change state; they are only updated with new data when sources are supplemented.

---

## Data Volume Assumptions

- **Artworks**: 10,000+ documented works
- **Artists**: 5,000+ documented creators
- **Art Movements**: 100+ movements
- **Influence Chains**: 50,000+ documented relationships
- **Data Sources**: Wikipedia, WikiArt.org, and supplementary web sources

---

## Privacy & Compliance

**No user tracking** - This data model only contains historical art information with no personal or user-related data. All data is:
- Static (no updates after initial load)
- Aggregated from public sources
- Privacy-compliant (no PII collected)
