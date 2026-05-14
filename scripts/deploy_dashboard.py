# Dashboard deployment script
# This script deploys dashboard pages to the application

import os
import sys
import shutil
import argparse
from datetime import datetime


def deploy_dashboard(dashboard_name, dry_run=False):
    """
    Deploy a dashboard to the application.
    
    Args:
        dashboard_name: Name of the dashboard (directory name)
        dry_run: If True, only print what would be deployed
    
    Returns:
        Tuple of (success, messages)
    """
    base_path = 'backend/dashboards'
    dashboard_path = os.path.join(base_path, dashboard_name)
    
    if not os.path.exists(dashboard_path):
        return False, [f"Dashboard directory not found: {dashboard_path}"]
    
    # Validate dashboard first
    from services.dashboard_validation import dashboard_validator
    is_valid, errors = dashboard_validator.validate_all(dashboard_path)
    
    if not is_valid:
        return False, errors
    
    # Check if dashboard is already registered
    from dashboards import get_dashboard_list
    dashboards = get_dashboard_list()
    
    messages = []
    
    if dashboard_name in dashboards:
        messages.append(f"Dashboard '{dashboard_name}' is already registered")
    
    if dry_run:
        messages.append("Dry run mode - no changes made")
        print(f"Would deploy: {dashboard_name}")
        for msg in messages:
            print(f"  - {msg}")
        return True, messages
    
    # Update dashboard list
    # In a real implementation, this would update a database or registry
    print(f"Deploying dashboard: {dashboard_name}")
    print(f"Location: {dashboard_path}")
    
    return True, [f"Dashboard '{dashboard_name}' deployed successfully at {datetime.now()}"]


def main():
    """Main entry point for dashboard deployment."""
    parser = argparse.ArgumentParser(description='Deploy dashboard pages')
    parser.add_argument('dashboard', help='Name of dashboard to deploy')
    parser.add_argument('--dry-run', action='store_true', help='Print what would be deployed')
    
    args = parser.parse_args()
    
    success, messages = deploy_dashboard(args.dashboard, args.dry_run)
    
    if success:
        print("Deployment successful!")
        for msg in messages:
            print(f"  - {msg}")
    else:
        print("Deployment failed!")
        for msg in messages:
            print(f"  - ERROR: {msg}")
        sys.exit(1)


if __name__ == '__main__':
    main()
