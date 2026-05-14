# API Contracts: Derivative Art Analysis

**Feature**: Derivative Art Analysis  
**Date**: May 13 2026  
**Source**: [specs/001-derivative-art-analysis/spec.md](../spec.md)

---

## Overview

This document defines the RESTful API contracts for the Derivative Art Analysis backend. All endpoints follow REST conventions and return JSON responses.

---

## Base URL

```
http://localhost:5000/api
```

**Authentication**: None required (historical art data is public)

**Rate Limiting**: No limits (static dataset, internal network)

---

## Endpoint: Dashboard Overview

**GET** `/api/art/overview`

**Purpose**: Retrieve summary statistics for the main dashboard.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `time_period` | string | No | Filter by time period (e.g., "1800-1850") |
| `movement` | string | No | Filter by movement (e.g., "impressionism") |
| `medium` | string | No | Filter by medium (e.g., "oil") |

### Response Schema

```json
{
  "summary": {
    "total_artworks": 15432,
    "total_artists": 8234,
    "total_movements": 156,
    "avg_originality_score": 67.3,
    "avg_influence_density": 2.4,
    "total_influence_chains": 45678
  },
  "trends": [
    {
      "period": "1800-1850",
      "avg_originality": 45.2,
      "avg_influence_density": 1.8,
      "trend_direction": "increasing"
    },
    {
      "period": "1850-1900",
      "avg_originality": 58.7,
      "avg_influence_density": 2.3,
      "trend_direction": "stable"
    }
  ],
  "top_movements": [
    {
      "id": "mov-001",
      "name": "Impressionism",
      "artwork_count": 1234,
      "artist_count": 456,
      "avg_originality": 72.5
    }
  ]
}
```

### Error Responses

| Status Code | Error | Description |
|-------------|-------|-------------|
| 400 | Bad Request | Invalid filter parameters |
| 500 | Internal Server Error | Data loading failure |

---

## Endpoint: Influence Chain

**GET** `/api/art/influences/{entity_id}`

**Purpose**: Retrieve influence chain for a specific artwork or artist.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `entity_id` | string | Yes | UUID of artwork or artist |

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `type` | string | Yes | "artist" or "artwork" |
| `direction` | string | No | "both", "incoming", "outgoing" (default: "both") |
| `include_strength` | boolean | No | Include influence strength values (default: true) |

### Response Schema

```json
{
  "entity": {
    "id": "art-001",
    "type": "artwork",
    "title": "Starry Night",
    "artist": "Vincent van Gogh"
  },
  "influences": {
    "incoming": [
      {
        "entity_id": "art-002",
        "entity_title": "Sunflowers",
        "entity_type": "artwork",
        "influence_strength": 0.85,
        "confidence_level": "high"
      }
    ],
    "outgoing": [
      {
        "entity_id": "art-003",
        "entity_title": "Night Café",
        "entity_type": "artwork",
        "influence_strength": 0.72,
        "confidence_level": "medium"
      }
    ]
  },
  "metadata": {
    "total_influences": 12,
    "avg_strength": 0.68,
    "data_sufficient": true
  }
}
```

### Error Responses

| Status Code | Error | Description |
|-------------|-------|-------------|
| 404 | Not Found | Entity not found |
| 400 | Bad Request | Invalid entity type |
| 500 | Internal Server Error | Data processing failure |

---

## Endpoint: Compare Metrics

**POST** `/api/art/compare`

**Purpose**: Compare metrics across multiple entities.

### Request Schema

```json
{
  "entities": [
    {
      "entity_id": "art-001",
      "type": "artwork"
    },
    {
      "entity_id": "art-002",
      "type": "artwork"
    }
  ],
  "metrics": ["originality_score", "influence_density"],
  "include_trends": true
}
```

### Response Schema

```json
{
  "entities": [
    {
      "id": "art-001",
      "type": "artwork",
      "title": "Starry Night",
      "metrics": {
        "originality_score": 78.5,
        "influence_density": 3.2
      }
    },
    {
      "id": "art-002",
      "type": "artwork",
      "title": "Sunflowers",
      "metrics": {
        "originality_score": 72.3,
        "influence_density": 2.8
      }
    }
  ],
  "comparison": {
    "avg_originality": 75.4,
    "avg_influence_density": 3.0,
    "std_deviation": 4.2
  },
  "visual_overlay": {
    "type": "line_chart",
    "data_points": [...]
  }
}
```

### Error Responses

| Status Code | Error | Description |
|-------------|-------|-------------|
| 400 | Bad Request | Invalid entity list or metrics |
| 422 | Unprocessable Entity | Insufficient entities for comparison |
| 500 | Internal Server Error | Comparison calculation failure |

---

## Endpoint: Filter Results

**GET** `/api/art/filter`

**Purpose**: Retrieve filtered list of artworks/artists.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `period` | string | No | Time period filter (e.g., "1800-1850") |
| `movement` | string | No | Movement filter (e.g., "impressionism") |
| `medium` | string | No | Medium filter (e.g., "oil") |
| `min_originality` | number | No | Minimum originality score threshold |
| `max_originality` | number | No | Maximum originality score threshold |
| `page` | integer | No | Page number (default: 1) |
| `page_size` | integer | No | Items per page (default: 50, max: 100) |

### Response Schema

```json
{
  "items": [
    {
      "id": "art-001",
      "title": "Starry Night",
      "artist": "Vincent van Gogh",
      "period": "1889",
      "movement": "Post-Impressionism",
      "medium": "oil",
      "originality_score": 78.5
    }
  ],
  "pagination": {
    "current_page": 1,
    "total_pages": 308,
    "total_items": 15432,
    "page_size": 50
  },
  "filters_applied": {
    "period": "1800-1850",
    "movement": "impressionism"
  }
}
```

### Error Responses

| Status Code | Error | Description |
|-------------|-------|-------------|
| 400 | Bad Request | Invalid filter values |
| 422 | Unprocessable Entity | Invalid pagination parameters |

---

## Data Models (Request/Response)

### Artwork Summary

```json
{
  "id": "uuid-string",
  "title": "string",
  "artist": "string",
  "artist_id": "uuid-string",
  "date_created": "ISO8601",
  "movement": "string",
  "medium": "string",
  "originality_score": 0-100 or null,
  "influence_count": integer
}
```

### Artist Summary

```json
{
  "id": "uuid-string",
  "name": "string",
  "birth_year": integer or null,
  "death_year": integer or null,
  "nationality": "string",
  "period": "string",
  "movements": ["string", ...],
  "originality_score": 0-100 or null,
  "total_works": integer
}
```

### Movement Summary

```json
{
  "id": "uuid-string",
  "name": "string",
  "start_year": integer,
  "end_year": integer,
  "origin_country": "string",
  "total_artists": integer,
  "total_works": integer,
  "avg_originality": 0-100 or null
}
```

---

## Contract Testing

**Success Paths**:
- Dashboard loads with summary statistics
- Influence chains display bidirectional relationships
- Comparison view shows side-by-side metrics
- Filter results return paginated lists

**Error States**:
- Invalid entity IDs return 404
- Invalid filter parameters return 400
- Empty datasets return empty arrays with metadata

**Edge Cases**:
- Artists with no influences return empty influence arrays
- Incomplete data returns null scores with metadata warnings
- Large result sets handled via pagination

---

## Versioning

**Current Version**: 1.0.0  
**Version Header**: `X-API-Version: 1.0.0`

**Breaking Changes**: Will increment major version and update contract documentation.
