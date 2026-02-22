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

        const getVal = (headerText) => {
            const h = headerText.toString().toLowerCase().trim();

            if (h.includes("timestamp")) return new Date();
            if (h.includes("name")) return data.name;

            // PRIORITY 1: Match Email/Mail columns (matches "Mail or Phone" correctly)
            if (h.includes("mail") || h.includes("email")) return data.email;

            // PRIORITY 2: Match WhatsApp/Phone (only if it didn't match Mail/Email)
            if (h.includes("whatsapp") || h.includes("phone")) return data.whatsapp;

            if (h.includes("location")) return data.location;
            if (h.includes("person")) return data.person;
            if (h.includes("industry")) return data.industry;

            // Automation Comments
            if (h.includes("global") && h.includes("template")) return data.global_template;
            if (h.includes("niche") && h.includes("comment")) return data.comment_niche;
            if (h.includes("hiring") && h.includes("comment")) return data.comment_hiring;
            if (h.includes("new connection") && h.includes("comment")) return data.comment_new_connections;
            if (h.includes("connections posts") && h.includes("comment")) return data.comment_connections_posts;

            return null;
        };

        // Find email column index fuzzy
        let emailColIdx = -1;
        for (let i = 0; i < headers.length; i++) {
            const text = headers[i].toString().toLowerCase();
            if (text.includes("mail") || text.includes("email")) {
                emailColIdx = i;
                break;
            }
        }

        if (emailColIdx === -1) throw new Error("Required column 'Email' or 'Mail' not found.");

        const values = sheet.getDataRange().getValues();
        let rowIndex = -1;
        for (let i = 1; i < values.length; i++) {
            if (values[i][emailColIdx] == email) {
                rowIndex = i + 1;
                break;
            }
        }

        let isNewRow = (rowIndex === -1);
        if (isNewRow) rowIndex = sheet.getLastRow() + 1;

        let currentRowData = isNewRow ? [] : sheet.getRange(rowIndex, 1, 1, headers.length).getValues()[0];

        const newRowData = headers.map((header, index) => {
            const newVal = getValForHeader(header);

            if (newVal !== undefined && newVal !== null && newVal !== "") {
                return Array.isArray(newVal) ? newVal.join(", ") : newVal;
            }
            return currentRowData[index] || "";
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
