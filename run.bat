@echo off
echo Starting LinkedIn AI Agent Local Server (Flask Backend)...
start /B python app.py
timeout /t 3 >nul
echo Opening your website...
start http://localhost:8000/index.html
echo.
echo ============================================
echo DONE! You can now access your website at 
echo http://localhost:8000
echo ============================================
pause
