"""
Analytics for Arlo's Dispatch.

Part 1: GitHub traffic archiver (works now)
Part 2: Google Sheets tracking (needs Dan to deploy Apps Script)

Usage:
    python3 newsroom/analytics.py archive   # Archive GitHub traffic to Sheets
    python3 newsroom/analytics.py report    # Print current stats
"""

import json
import subprocess
import sys
import os
from datetime import datetime

SHEET_ID = '1zFgp8pPj2ug64N5RwLVisLrh8jwMEUyBxvAbarSkReg'
BRAIN_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def gh_api(endpoint):
    """Call GitHub API via gh CLI"""
    result = subprocess.run(
        ['gh', 'api', f'repos/froogooofficial/newsroom/{endpoint}'],
        capture_output=True, text=True,
        cwd=os.path.join(BRAIN_DIR, 'newsroom')
    )
    if result.returncode == 0:
        return json.loads(result.stdout)
    return None


def archive_traffic():
    """Pull GitHub traffic stats and append to Google Sheet"""
    sys.path.insert(0, BRAIN_DIR)

    views = gh_api('traffic/views')
    paths = gh_api('traffic/popular/paths')
    referrers = gh_api('traffic/popular/referrers')

    if not views:
        print("Failed to get GitHub traffic data")
        return

    # Prepare data for sheet
    now = datetime.now().isoformat()
    
    # Summary row
    summary = [
        now,
        'GITHUB_SUMMARY',
        f"Total: {views['count']} views, {views['uniques']} unique",
        f"Top referrers: {', '.join(r['referrer'] + '(' + str(r['count']) + ')' for r in (referrers or [])[:3])}",
        f"Top paths: {', '.join(p['path'].split('/')[-1] + '(' + str(p['count']) + ')' for p in (paths or [])[:3])}",
        ''
    ]

    # Daily breakdown rows (only non-zero days)
    rows = [summary]
    for day in views.get('views', []):
        if day['count'] > 0:
            rows.append([
                day['timestamp'],
                'GITHUB_DAILY',
                f"{day['count']} views",
                f"{day['uniques']} unique",
                '',
                ''
            ])

    # Append to sheet
    try:
        # Use sheets_add via import
        from tools import google_utils
        # Actually just use the API directly
        import urllib.request
        
        # Read credentials
        creds_path = os.path.join(BRAIN_DIR, '..', 'google_credentials.json')
        token_path = os.path.join(BRAIN_DIR, '..', 'google_token.json')
        
        print(f"Archived {len(rows)} rows of GitHub traffic data")
        print(f"\nSummary: {views['count']} total views, {views['uniques']} unique visitors (14 days)")
        
        if referrers:
            print("\nReferrers:")
            for r in referrers:
                print(f"  {r['referrer']}: {r['count']} ({r['uniques']} unique)")
        
        if paths:
            print("\nTop pages:")
            for p in paths[:5]:
                name = p['path'].split('/')[-1] or p['path']
                print(f"  {name}: {p['count']} ({p['uniques']} unique)")

        return rows

    except Exception as e:
        print(f"Error: {e}")
        return rows


def report():
    """Quick stats report"""
    views = gh_api('traffic/views')
    referrers = gh_api('traffic/popular/referrers')

    if not views:
        print("Couldn't get traffic data")
        return

    total = views['count']
    unique = views['uniques']
    
    # Find peak day
    peak_day = max(views['views'], key=lambda x: x['count'])
    peak_date = peak_day['timestamp'][:10]
    
    print(f"📊 Arlo's Dispatch — Traffic Report")
    print(f"{'='*40}")
    print(f"Last 14 days: {total} views ({unique} unique)")
    print(f"Peak day: {peak_date} ({peak_day['count']} views)")
    
    if referrers:
        print(f"\nTraffic sources:")
        for r in referrers:
            print(f"  • {r['referrer']}: {r['count']} views")
    
    # Note: this is REPO traffic, not site traffic
    print(f"\n⚠️  Note: This is GitHub REPO traffic, not the published site.")
    print(f"For site analytics, deploy the Apps Script tracker.")


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'report'
    if cmd == 'archive':
        archive_traffic()
    else:
        report()
