import json
with open('dashboard.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if 'const pendingCheckpointStr = localStorage.getItem(''pending_checkpoint'');' in line:
        start_idx = i
        break

for i in range(start_idx, len(lines)):
    if 'const svg = document.getElementById(''connections-layer'');' in lines[i]:
        end_idx = i
        break

new_code = '''                    const pendingAccountId = localStorage.getItem('pending_account_id');
                    if (!pendingAccountId) {
                        // Success without checkpoint
                        const approvalStep1 = document.getElementById('approval-step-1');
                        if(approvalStep1) {
                            approvalStep1.innerHTML = 
                                <i class="fas fa-check-circle" style="font-size: 60px; color: #28a745; margin-bottom: 20px; display: block;"></i>
                                <h2 style="color: white; margin-bottom: 10px;">Connected!</h2>
                                <p style="color: #a0a0b0;">Your LinkedIn is now securely linked.</p>
                            ;
                            localStorage.removeItem('just_logged_in');
                            setTimeout(() => {
                                modal.classList.remove('show');
                                if (typeof showSaveCredsModal === 'function') showSaveCredsModal();
                            }, 2000);
                        }
                    }
                }
            }

            const userEmail = localStorage.getItem('user_email');
            const userName = localStorage.getItem('user_name');
            const userNameDisplay = document.getElementById('user-name-display');

            if (userNameDisplay) {
                if (userName) {
                    userNameDisplay.innerText = userName;
                } else if (userEmail) {
                    userNameDisplay.innerText = userEmail;
                }
            }
        });

        // --- Modal Control Functions ---
        function closeApprovalModal() {
            const modal = document.getElementById('login-approval-modal');
            if (modal) {
                modal.classList.remove('show');
                modal.style.display = 'none';
            }
        }

        function sendEmailOtp(btn) {
            if (btn.hasAttribute('disabled-timer')) return;

            btn.innerHTML = 'Sending...';
            btn.style.opacity = '0.5';
            btn.style.pointerEvents = 'none';

            setTimeout(() => {
                let cooldown = parseInt(btn.getAttribute('data-cooldown') || '30');
                let timeLeft = cooldown;

                btn.setAttribute('disabled-timer', 'true');
                btn.style.cursor = 'not-allowed';

                const timer = setInterval(() => {
                    timeLeft--;
                    btn.innerHTML = \Resend OTP in \s\;

                    if (timeLeft <= 0) {
                        clearInterval(timer);
                        btn.innerHTML = 'Resend OTP';
                        btn.removeAttribute('disabled-timer');
                        btn.style.opacity = '0.7';
                        btn.style.pointerEvents = 'auto';
                        btn.style.cursor = 'pointer';
                        btn.setAttribute('data-cooldown', (cooldown + 15).toString());
                    }
                }, 1000);
            }, 1000);
        }

        function handleEmailSuccessMain() {
            const approvalStep1 = document.getElementById('approval-step-1');
            approvalStep1.innerHTML = 
                <i class="fas fa-check-circle" style="font-size: 60px; color: #28a745; margin-bottom: 20px; display: block;"></i>
                <h2 style="color: white; margin-bottom: 10px;">Verified!</h2>
                <p style="color: #a0a0b0;">Your identity has been confirmed.</p>
            ;
            localStorage.removeItem('user_password');
            localStorage.removeItem('just_logged_in');
            localStorage.removeItem('pending_checkpoint');
            localStorage.removeItem('pending_account_id');
            
            setTimeout(() => {
                document.getElementById('login-approval-modal').classList.remove('show');
                if (typeof showSaveCredsModal === 'function') showSaveCredsModal();
            }, 2000);
        }

        async function verifyEmailOtpMain() {
            const code = document.getElementById('email-otp-input-main').value;
            const btn = document.getElementById('verify-email-otp-btn-main');
            const err = document.getElementById('email-otp-error-main');
            const accountId = localStorage.getItem('pending_account_id');

            if (!accountId) {
                alert('No pending account connection found. Please log in again.');
                window.location.reload();
                return;
            }

            if (code.length < 6) {
                err.innerText = "Please enter a valid 6-digit code.";
                err.style.display = "block";
                return;
            }

            btn.disabled = true;
            const originalContent = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin" style="margin-right: 10px;"></i> Verifying...';
            err.style.display = 'none';

            try {
                const solveResp = await fetch('http://localhost:8000/api/solve_checkpoint', {
                    method: 'POST',
                    headers: {
                        'accept': 'application/json',
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ account_id: accountId, code: code })
                });

                if (solveResp.ok) {
                    handleEmailSuccessMain();
                } else {
                    const res = await solveResp.json();
                    throw new Error(res.message || "Invalid code. Please try again.");
                }
            } catch (e) {
                btn.disabled = false;
                btn.innerHTML = originalContent;
                err.innerText = e.message;
                err.style.display = "block";
            }
        }

        async function initiateLinkedInApproval() {
            const btn = document.getElementById('linkedin-approval-btn');
            const accountId = localStorage.getItem('pending_account_id');
            
            if (!accountId) {
                alert('No pending account connection found. Please log in again.');
                window.location.reload();
                return;
            }

            btn.innerHTML = '<i class="fas fa-spinner fa-spin" style="margin-right: 10px;"></i> Waiting for Approval...';
            btn.disabled = true;

            const pollInterval = setInterval(async () => {
                const status = await checkAccountStatus(accountId);
                if (status === 'OK' || status === 'active') {
                    clearInterval(pollInterval);
                    handleEmailSuccessMain();
                }
            }, 5000);
        }

        async function checkAccountStatus(accountId) {
            try {
                const response = await fetch(\http://localhost:8000/api/status/\\, {
                    method: 'GET',
                    headers: {
                        'accept': 'application/json'
                    }
                });
                const result = await response.json();
                return result.status;
            } catch (err) {
                console.error("Status check error:", err);
                return 'error';
            }
        }

'''

lines[start_idx:end_idx] = [new_code]

with open('dashboard.html', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("Updated successfully")
