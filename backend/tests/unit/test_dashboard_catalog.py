from backend.dashboards import serialize_dashboard_registry


def test_serialize_dashboard_registry_filters_sorts_and_builds_paths():
    registry = {
        'index': {'path': '/', 'name': 'Index', 'order': 0},
        'hidden': {'path': '/hidden', 'name': 'Hidden', 'dashboard_visible': False},
        'second': {'path': '/second', 'name': 'Second', 'description': 'Second story', 'order': 2},
        'first': {
            'path': '/first', 'name': 'Fallback', 'dashboard_title': 'First',
            'dashboard_description': 'First story', 'order': 1,
        },
    }

    assert serialize_dashboard_registry(registry) == [
        {
            'slug': 'first', 'title': 'First', 'description': 'First story', 'order': 1,
            'public_path': '/data-storytelling/first',
            'embed_path': '/data-storytelling-app/first',
        },
        {
            'slug': 'second', 'title': 'Second', 'description': 'Second story', 'order': 2,
            'public_path': '/data-storytelling/second',
            'embed_path': '/data-storytelling-app/second',
        },
    ]


def test_serialize_dashboard_registry_handles_empty_registry():
    assert serialize_dashboard_registry({}) == []
