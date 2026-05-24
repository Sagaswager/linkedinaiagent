/*
 * ============================================================
 * GOOGLE APPS SCRIPT - LinkedIn AI Agent (Simple Version)
 * ============================================================
 *
 * HOW TO SETUP (Do this ONCE):
 * 1. Open your Google Sheet (Form_Responses tab).
 * 2. Click "Extensions" > "Apps Script".
 * 3. DELETE all existing code.
 * 4. PASTE this entire file's code.
 * 5. Click Save (💾 icon).
 * 6. Click "Deploy" > "New deployment".
 * 7. Click the gear icon ⚙️ > Select "Web app".
 * 8. Set:
 *      - Execute as: Me
 *      - Who has access: Anyone
 * 9. Click "Deploy". Authorize when asked.
 * 10. COPY the Web App URL shown.
 * 11. Paste that URL into form_handler.js → WEB_APP_URL variable.
 *
 * NOTE: Every time you change this code, you must redeploy:
 *       Deploy > Manage Deployments > ✏️ Edit > New Version > Deploy
 * ============================================================
 */

function doGet(e) {
  try {
    // Get the active spreadsheet and the sheet named "Form_Responses"
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sheet = ss.getSheetByName("Form_Responses");

    // If "Form_Responses" tab doesn't exist, use the first sheet
    if (!sheet) {
      sheet = ss.getSheets()[0];
    }

    // Read URL params sent from the website
    var timestamp = new Date();
    var name      = e.parameter.name      || "";
    var whatsapp  = e.parameter.whatsapp  || "";
    var email     = e.parameter.email     || "";
    var location  = e.parameter.location  || "";

    // Must have email to proceed
    if (!email) {
      return ContentService.createTextOutput("ERROR: No email provided");
    }

    // Check if this email already exists in column D (Mail or Phone = col 4)
    var data = sheet.getDataRange().getValues();
    var existingRow = -1;
    for (var i = 1; i < data.length; i++) {
      if (data[i][3] && data[i][3].toString().toLowerCase() === email.toLowerCase()) {
        existingRow = i + 1; // Sheet rows are 1-indexed
        break;
      }
    }

    if (existingRow === -1) {
      // New user → append a new row
      // Order: Time/Date | Name | Whatsapp Number | Mail or Phone | Chose Location
      sheet.appendRow([timestamp, name, whatsapp, email, location]);
    } else {
      // Existing user → update their row (keep timestamp, update rest)
      sheet.getRange(existingRow, 2).setValue(name);      // B: Name
      sheet.getRange(existingRow, 3).setValue(whatsapp);  // C: Whatsapp Number
      sheet.getRange(existingRow, 4).setValue(email);     // D: Mail or Phone
      if (location) sheet.getRange(existingRow, 5).setValue(location); // E: Chose Location
    }

    return ContentService.createTextOutput("OK");

  } catch (err) {
    // Log error for debugging in Apps Script dashboard
    Logger.log("ERROR: " + err.toString());
    return ContentService.createTextOutput("ERROR: " + err.toString());
  }
}
