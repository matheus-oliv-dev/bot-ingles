@echo off
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

echo Running Lint (flake8)...
flake8 src tests main.py
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Linting failed. Please fix the errors above.
    exit /b %ERRORLEVEL%
)

echo Running Tests (pytest)...
python -m pytest tests/
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Tests failed. Please fix the errors above.
    exit /b %ERRORLEVEL%
)

echo [SUCCESS] All checks passed! You are good to commit or code.
exit /b 0
