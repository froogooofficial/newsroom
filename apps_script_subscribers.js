// Arlo's Dispatch — Newsletter Subscriber Collector
// Deploy as Google Apps Script Web App
//
// SETUP:
// 1. Go to https://script.google.com
// 2. Create new project
// 3. Paste this code
// 4. Deploy → New deployment → Web app
//    - Execute as: Me
//    - Who has access: Anyone
// 5. Copy the deployment URL
// 6. Replace PLACEHOLDER in build.py with the URL

var SHEET_ID = "17M7uoRnWE2JolQYMfLlVbKcoKP4Bx4Rrn9j-jPJb8iY";

function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var email = data.email;
    
    if (!email || !email.includes("@")) {
      return ContentService.createTextOutput(JSON.stringify({status: "error", message: "Invalid email"}))
        .setMimeType(ContentService.MimeType.JSON);
    }
    
    var sheet = SpreadsheetApp.openById(SHEET_ID).getActiveSheet();
    
    // Check for duplicates
    var existing = sheet.getRange("A:A").getValues().flat();
    if (existing.includes(email)) {
      return ContentService.createTextOutput(JSON.stringify({status: "exists", message: "Already subscribed"}))
        .setMimeType(ContentService.MimeType.JSON);
    }
    
    // Add subscriber
    sheet.appendRow([email, new Date().toISOString(), data.source || "website"]);
    
    return ContentService.createTextOutput(JSON.stringify({status: "ok", message: "Subscribed!"}))
      .setMimeType(ContentService.MimeType.JSON);
      
  } catch(err) {
    return ContentService.createTextOutput(JSON.stringify({status: "error", message: err.toString()}))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet(e) {
  // Allow GET requests too (for sendBeacon fallback)
  if (e && e.parameter && e.parameter.email) {
    var fakePost = {postData: {contents: JSON.stringify({email: e.parameter.email, source: "beacon"})}};
    return doPost(fakePost);
  }
  
  // Return subscriber count
  var sheet = SpreadsheetApp.openById(SHEET_ID).getActiveSheet();
  var count = Math.max(0, sheet.getLastRow() - 1); // minus header
  return ContentService.createTextOutput(JSON.stringify({subscribers: count}))
    .setMimeType(ContentService.MimeType.JSON);
}
