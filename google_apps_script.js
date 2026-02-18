/*
 * GOOGLE APPS SCRIPT CODE
 * -----------------------
 * COPY EVERYTHING BELOW THIS LINE AND PASTE IT INTO YOUR GOOGLE SHEET'S APPS SCRIPT EDITOR.
 *
 * INSTRUCTIONS:
 * 1. Open your Google Sheet.
 * 2. Go to "Extensions" > "Apps Script".
 * 3. Delete any code there and paste this entire code.
 * 4. Click the "Save" icon (floppy disk).
 * 5. Click "Deploy" (top right) > "New deployment".
 * 6. Click the "Select type" gear icon > "Web app".
 * 7. Set "Description" to "LinkedIn Agent v1".
 * 8. Set "Execute as" to "Me".
 * 9. Set "Who has access" to "Anyone". (CRITICAL)
 * 10. Click "Deploy".
 * 11. Copy the "Web app URL" and paste it into local file: form_handler.js
 */

function doPost(e) {
    const lock = LockService.getScriptLock();
    lock.tryLock(10000);

    try {
        const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
        const headers = sheet.getRange(1, 1, 1, sheet.getLastColumn()).getValues()[0];
        const data = JSON.parse(e.postData.contents);

        // Key to identify the user (Email)
        const email = data.email;
        if (!email) {
            return ContentService.createTextOutput(JSON.stringify({ "result": "error", "message": "No email provided" })).setMimeType(ContentService.MimeType.JSON);
        }

        // Map inputs to Header Names exactly as shown in your Sheet
        const fieldMapping = {
            "email": "Mail or Phone",
            "location": "Chose Location",
            "person": "Chose Person",
            "industry": "Chose Industry",
            "message_1": "Message 1",
            "message_2": "Message 2",
            "message_3": "Message 3",
            "message_4": "Message 4",
            "global_template": "Global Template Comment",
            "comment_niche": "comment on Niche - Location, Industry",
            "comment_hiring": "Comment on Hiring Managers Posts",
            "comment_new_connections": "Comment on New Connections",
            "comment_connections_posts": "Comment on Connections Posts"
        };

        // Find if user exists
        const emailColIndex = headers.indexOf(fieldMapping["email"]);
        if (emailColIndex === -1) throw new Error("Column 'Mail or Phone' not found in Sheet.");

        const dataRange = sheet.getDataRange();
        const values = dataRange.getValues();
        let rowIndex = -1;

        // Search for email (skip header row 0)
        for (let i = 1; i < values.length; i++) {
            if (values[i][emailColIndex] == email) {
                rowIndex = i + 1; // 1-based row index
                break;
            }
        }

        // Prepare data row
        let rowToUpdate = [];
        let isNewRow = false;

        if (rowIndex === -1) {
            // New User -> Append
            isNewRow = true;
            rowIndex = sheet.getLastRow() + 1;
        }

        // For updates, we need to be careful not to overwrite existing data with empty values if the user didn't send them
        // But since we are stateless, we iterate headers and fill what we have.

        // Strategy: Read current row if exists, then overlay new data
        let currentRowData = [];
        if (!isNewRow) {
            currentRowData = sheet.getRange(rowIndex, 1, 1, sheet.getLastColumn()).getValues()[0];
        }

        const newRowData = headers.map((header, index) => {
            // Find which key maps to this header
            const key = Object.keys(fieldMapping).find(k => fieldMapping[k] === header);

            // If we have new data for this header, use it
            if (key && data[key] !== undefined && data[key] !== null && data[key] !== "") {
                // Handle arrays (like location tags)
                if (Array.isArray(data[key])) return data[key].join(", ");
                return data[key];
            }

            // If no new data, keep existing data (if row exists)
            if (!isNewRow && currentRowData[index]) {
                return currentRowData[index];
            }

            // Timestamp handling
            if (header === "Timestamp" && isNewRow) {
                return new Date();
            }

            return ""; // Empty otherwise
        });

        if (isNewRow) {
            sheet.appendRow(newRowData);
        } else {
            sheet.getRange(rowIndex, 1, 1, newRowData.length).setValues([newRowData]);
        }

        return ContentService.createTextOutput(JSON.stringify({ "result": "success", "row": rowIndex, "action": isNewRow ? "created" : "updated" })).setMimeType(ContentService.MimeType.JSON);

    } catch (e) {
        return ContentService.createTextOutput(JSON.stringify({ "result": "error", "error": e.toString() })).setMimeType(ContentService.MimeType.JSON);
    } finally {
        lock.releaseLock();
    }
}
