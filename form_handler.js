/**
 * Google Sheet Handler for LinkedIn AI Agent
 * Uses Google Apps Script Web App to handle row updates and custom columns.
 */

// 🚨 PASTE YOUR DEPLOYED WEB APP URL HERE 🚨
const WEB_APP_URL = 'https://script.google.com/macros/s/AKfycbxpARZDKup1kioJj71-gyF_oYBtPb7osWjari4_w-x-IpO02lqgGLoBnRQ_ZvUb3SJEQA/exec';

/**
 * Submits data to Google Sheet via Apps Script
 * @param {Object} data - The data to submit
 */
async function saveToGoogleSheet(data) {
    if (WEB_APP_URL.includes('PASTE_YOUR')) {
        alert("Configuration Message: Please follow the instructions to Paste your Google Apps Script URL in 'form_handler.js'");
        console.error("Missing Web App URL");
        // We pause execution or let it fail gracefully if user hasn't set it yet
        return;
    }

    // Always try to get email from localStorage if not provided
    const email = data.email || localStorage.getItem('user_email');
    const name = data.name || localStorage.getItem('user_name');
    const whatsapp = data.whatsapp || localStorage.getItem('user_whatsapp');

    if (!email) {
        alert("Error: User email missing. Please login first.");
        return;
    }

    // Prepare Request Payload
    // We merge the email and other stored details into the data object
    const payload = {
        ...data,
        email: email,
        name: name || data.name,
        whatsapp: whatsapp || data.whatsapp
    };

    console.log('Sending data to Sheet via Web App:', payload);

    try {
        await fetch(WEB_APP_URL, {
            method: 'POST',
            mode: 'no-cors', // standard for GAS Web Apps simple POST
            headers: {
                'Content-Type': 'text/plain;charset=utf-8',
            },
            body: JSON.stringify(payload)
        });

        // With no-cors, we cannot read the response status, but the request is sent.
        console.log('Request sent to Web App (no-cors mode)');

    } catch (error) {
        console.error('Error submitting to Sheet:', error);
    }
}

// Expose to window
window.saveToGoogleSheet = saveToGoogleSheet;
