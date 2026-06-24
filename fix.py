with open('dashboard.html', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('btn.innerHTML = \\Resend OTP in \\s\\;', 'btn.innerHTML = Resend OTP in s;')

with open('dashboard.html', 'w', encoding='utf-8') as f:
    f.write(text)
print('Fixed!')
