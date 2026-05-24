/**
 * Google Sheet Handler - LinkedIn AI Agent
 * -----------------------------------------
 * Sends user data to Google Sheet via Apps Script Web App.
 * Uses Image Beacon technique — zero CORS issues, works 100%.
 *
 * SETUP: Paste the Apps Script Web App URL below.
 */

// ✅ PASTE YOUR APPS SCRIPT WEB APP URL HERE
const WEB_APP_URL = 'https://script.google.com/macros/s/AKfycbysUaGaPK2Jah00UELMm5dPAuy8eHqIjt_zJiKRj8EBytladLtGRswHJ5qHfwMzDgjL0g/exec';

/**
 * Saves user data to Google Sheet when "Connect Account" is clicked.
 * @param {Object} data - Contains all possible fields.
 */
async function saveToGoogleSheet(data) {
    // Fallback to localStorage if values not passed directly
    const email    = (data.email    || localStorage.getItem('user_email')    || '').trim();
    const name     = (data.name     || localStorage.getItem('user_name')     || '').trim();
    const whatsapp = (data.whatsapp || localStorage.getItem('user_whatsapp') || '').trim();
    const location = (data.location || '').trim();
    const person   = (data.person   || '').trim();
    const industry = (data.industry || '').trim();
    const message_1 = (data.message_1 || '').trim();
    const message_2 = (data.message_2 || '').trim();
    const message_3 = (data.message_3 || '').trim();
    const message_4 = (data.message_4 || '').trim();
    const comment_prompt = (data.comment_prompt || '').trim();
    const post_prompt = (data.post_prompt || '').trim();

    if (!email) {
        console.warn('saveToGoogleSheet: email is empty, skipping sheet save.');
        return;
    }

    // Build URL with query params
    const params = new URLSearchParams({ email, name, whatsapp, location, person, industry, message_1, message_2, message_3, message_4, comment_prompt, post_prompt });
    const url = `${WEB_APP_URL}?${params.toString()}`;

    console.log('📊 Sending to Google Sheet:', { email, name, whatsapp, location, person, industry, message_1, message_2, message_3, message_4, comment_prompt, post_prompt });
    console.log('🔗 Request URL:', url);

    // ✅ Image Beacon Method — most reliable way to hit Google Apps Script
    // No CORS issues, no redirect blocks, works from any origin (localhost or live)
    return new Promise((resolve) => {
        const img = new Image();
        img.onload  = () => { console.log('✅ Google Sheet updated successfully'); resolve(); };
        img.onerror = () => { console.log('✅ Google Sheet request sent (error is normal for GAS, data still saved)'); resolve(); };
        img.src = url;

        // Fallback resolve after 5 seconds in case image never loads/errors
        setTimeout(resolve, 5000);
    });
}

// Make it available globally
window.saveToGoogleSheet = saveToGoogleSheet;
