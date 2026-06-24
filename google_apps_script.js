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
    var person    = e.parameter.person    || "";
    var industry  = e.parameter.industry  || "";
    var msg1      = e.parameter.message_1 || "";
    var msg2      = e.parameter.message_2 || "";
    var msg3      = e.parameter.message_3 || "";
    var msg4      = e.parameter.message_4 || "";
    var comment   = e.parameter.comment_prompt || "";
    var post      = e.parameter.post_prompt || "";

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
      // Order: Time/Date | Name | Whatsapp Number | Mail or Phone | Chose Location | Person | Industry | Msg1 | Msg2 | Msg3 | Msg4 | Comment | Post
      sheet.appendRow([timestamp, name, whatsapp, email, location, person, industry, msg1, msg2, msg3, msg4, comment, post]);
    } else {
      // Existing user → update their row (keep timestamp, update rest)
      sheet.getRange(existingRow, 2).setValue(name);      // B: Name
      sheet.getRange(existingRow, 3).setValue(whatsapp);  // C: Whatsapp Number
      sheet.getRange(existingRow, 4).setValue(email);     // D: Mail or Phone
      if (location) sheet.getRange(existingRow, 5).setValue(location); // E: Chose Location
      if (person) sheet.getRange(existingRow, 6).setValue(person);     // F: Person
      if (industry) sheet.getRange(existingRow, 7).setValue(industry); // G: Industry
      if (msg1) sheet.getRange(existingRow, 8).setValue(msg1);         // H: Msg 1
      if (msg2) sheet.getRange(existingRow, 9).setValue(msg2);         // I: Msg 2
      if (msg3) sheet.getRange(existingRow, 10).setValue(msg3);        // J: Msg 3
      if (msg4) sheet.getRange(existingRow, 11).setValue(msg4);        // K: Msg 4
      if (comment) sheet.getRange(existingRow, 12).setValue(comment);  // L: Comment Prompt
      if (post) sheet.getRange(existingRow, 13).setValue(post);        // M: Post Prompt
    }

    return ContentService.createTextOutput("OK");

  } catch (err) {
    // Log error for debugging in Apps Script dashboard
    Logger.log("ERROR: " + err.toString());
    return ContentService.createTextOutput("ERROR: " + err.toString());
  }
}
