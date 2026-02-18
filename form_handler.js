/**
 * Google Sheet Handler for LinkedIn AI Agent
 * Uses Google Apps Script Web App to handle row updates and custom columns.
 */

// 🚨 PASTE YOUR DEPLOYED WEB APP URL HERE 🚨
const WEB_APP_URL = 'https://script.google.com/macros/s/AKfycby-ZicLogEk4ud5xx5EJvrXzks48xujy7BZDOUk4yPJ02oH85j5O8F3E027cKZ8DpiJBg/exec';

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

    if (!email) {
        alert("Error: User email missing. Please login first.");
        return;
    }

    // Prepare Request Payload
    // We merge the email into the data object
    const payload = { ...data, email: email };

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
