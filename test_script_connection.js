const fetch = require('node-fetch');

// This is the URL extracted from your form_handler.js
const WEB_APP_URL = 'https://script.google.com/macros/s/AKfycbwhL1qIHmD2U7i18CG1T2MtbbU0lgypfmZ9Mp8P_9MV5IYkweKAmVE9wVhhvrSGcx6L/exec';

async function testConnection() {
    console.log('Testing connection to Google Apps Script...');
    console.log('URL:', WEB_APP_URL);

    const testPayload = {
        email: 'test_user_ai_agent@example.com',
        location: ['Test City'],
        person: ['Test CEO'],
        industry: ['Testing'],
        message_1: 'Hello form validation'
    };

    try {
        const response = await fetch(WEB_APP_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'text/plain;charset=utf-8' },
            body: JSON.stringify(testPayload),
            redirect: 'follow' // Follow redirects which Google Scripts use
        });

        const text = await response.text();
        console.log('Response Status:', response.status);
        console.log('Response Body:', text);

        try {
            const json = JSON.parse(text);
            if (json.result === 'success') {
                console.log('✅ SUCCESS! The script is working and accessible.');
            } else {
                console.log('❌ SCRIPT ERROR:', json);
            }
        } catch (e) {
            console.log('❌ RESPONSE IS NOT JSON. Likely an HTML error page (permissions or 404). check the output above.');
        }

    } catch (error) {
        console.error('❌ NETWORK ERROR:', error);
    }
}

testConnection();
