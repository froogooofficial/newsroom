// Google Apps Script — Arlo's Dispatch Analytics Endpoint
// Deploy as Web App (Anyone can access, Execute as me)
// 
// Receives page view data via GET request, logs to spreadsheet.
// Called from the newspaper site via a tiny JS snippet.

var SHEET_ID = '1zFgp8pPj2ug64N5RwLVisLrh8jwMEUyBxvAbarSkReg';

function doGet(e) {
  try {
    var sheet = SpreadsheetApp.openById(SHEET_ID).getActiveSheet();
    var params = e.parameter;
    
    sheet.appendRow([
      new Date().toISOString(),           // Timestamp
      params.p || '/',                     // Page path
      params.r || '(direct)',              // Referrer
      params.s || '',                      // Screen size
      params.l || '',                      // Language
      ''                                    // Country (could use Apps Script geo later)
    ]);
    
    // Return 1x1 transparent GIF
    return ContentService.createTextOutput('ok')
      .setMimeType(ContentService.MimeType.TEXT);
  } catch (err) {
    return ContentService.createTextOutput('error')
      .setMimeType(ContentService.MimeType.TEXT);
  }
}
