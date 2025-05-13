# 1 . create virtual env
    python -m venv .venv

# 2. PowerShell - 
     Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    .venv\Scripts\Activate.ps1

# 3. installing dependencies
    pip install -r requirements.txt
    +
    pip install selenium webdriver-manager beautifulsoup4