# Analytics Setup for Arlo's Dispatch

## Current: GitHub Repo Traffic
- `python3 newsroom/analytics.py report` — shows 14-day traffic stats
- Only tracks visits to the GitHub REPO, not the published site

## Needed: Real Site Analytics

### Option A: Google Apps Script (Recommended)
**Dan needs 2 minutes to deploy this:**

1. Go to https://script.google.com
2. Click "New Project"
3. Paste this code:

```javascript
var SHEET_ID = '1zFgp8pPj2ug64N5RwLVisLrh8jwMEUyBxvAbarSkReg';

function doGet(e) {
  try {
    var sheet = SpreadsheetApp.openById(SHEET_ID).getActiveSheet();
    var params = e.parameter;
    sheet.appendRow([
      new Date().toISOString(),
      params.p || '/',
      params.r || '(direct)',
      params.s || '',
      params.l || ''
    ]);
    return ContentService.createTextOutput('ok');
  } catch (err) {
    return ContentService.createTextOutput('error');
  }
}
```

4. Click Deploy → New Deployment
5. Type: Web app
6. Execute as: Me
7. Who has access: Anyone
8. Deploy → Copy the URL

Then tell me the URL and I'll add the tracking snippet to the newspaper.

### Tracking snippet (goes in newspaper <head>):
```html
<script>
(function(){
  var u = 'APPS_SCRIPT_URL_HERE';
  var p = location.pathname;
  var r = document.referrer || '(direct)';
  var s = screen.width + 'x' + screen.height;
  var l = navigator.language;
  navigator.sendBeacon(u + '?p=' + encodeURIComponent(p) + '&r=' + encodeURIComponent(r) + '&s=' + s + '&l=' + l);
})();
</script>
```

### Option B: Cloudflare Web Analytics (Free, no proxy needed)
Needs a Cloudflare account. Just a JS snippet, no DNS changes.

### Option C: GoatCounter
Account exists at arlosdispatch.goatcounter.com but confirmation email never arrived.

## Google Sheet
- ID: 1zFgp8pPj2ug64N5RwLVisLrh8jwMEUyBxvAbarSkReg
- URL: https://docs.google.com/spreadsheets/d/1zFgp8pPj2ug64N5RwLVisLrh8jwMEUyBxvAbarSkReg
