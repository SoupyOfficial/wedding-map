# Wedding OCR Pipeline Setup Script (OpenAI-powered)
# Run this to set up your environment and process photos

Write-Host "Wedding OCR Pipeline Setup (OpenAI Vision)" -ForegroundColor Green

# Check if virtual environment exists
if (-not (Test-Path ".venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
. .\.venv\Scripts\Activate.ps1

# Install/upgrade dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Check for .env file
if (-not (Test-Path ".env")) {
    Write-Host "⚠ .env file not found. Creating from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "📝 Please edit .env and add your OpenAI API key:" -ForegroundColor Red
    Write-Host "   OPENAI_API_KEY=your_actual_api_key_here" -ForegroundColor Red
    Write-Host "   Get your key from: https://platform.openai.com/api-keys" -ForegroundColor Yellow
    
    $openEnv = Read-Host "Open .env file now? (y/N)"
    if ($openEnv -eq 'y' -or $openEnv -eq 'Y') {
        notepad .env
    }
    
    Write-Host "Please configure your API key before proceeding." -ForegroundColor Red
    exit 1
} else {
    Write-Host "✓ .env file found" -ForegroundColor Green
}

# Test setup
Write-Host "Testing setup..." -ForegroundColor Yellow
python test_setup.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Setup test failed. Please fix the issues above." -ForegroundColor Red
    exit 1
}

# Check for photos
$photoCount = (Get-ChildItem "src\images_raw\*.jpg", "src\images_raw\*.jpeg", "src\images_raw\*.png", "src\images_raw\*.heic", "src\images_raw\*.webp" -ErrorAction SilentlyContinue).Count
Write-Host "Found $photoCount photos in src\images_raw\" -ForegroundColor Cyan

if ($photoCount -eq 0) {
    Write-Host "📷 Add your wedding planning photos to src\images_raw\ then run:" -ForegroundColor Yellow
    Write-Host "   python tools\ocr_batch.py" -ForegroundColor White
} else {
    $confirm = Read-Host "Process $photoCount photos now? (y/N)"
    if ($confirm -eq 'y' -or $confirm -eq 'Y') {
        Write-Host "Processing photos with OpenAI Vision..." -ForegroundColor Yellow
        python tools\ocr_batch.py
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Consolidating results..." -ForegroundColor Yellow
            python tools\consolidate.py
            
            Write-Host "✓ Processing complete! Open src\master.md to organize with Copilot" -ForegroundColor Green
        } else {
            Write-Host "❌ OCR processing failed. Check the error messages above." -ForegroundColor Red
        }
    }
}

Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Add photos to src\images_raw\" -ForegroundColor White  
Write-Host "2. Run: python tools\ocr_batch.py" -ForegroundColor White
Write-Host "3. Run: python tools\consolidate.py" -ForegroundColor White
Write-Host "4. Open src\master.md and use Copilot prompts" -ForegroundColor White
Write-Host "5. Export: pandoc src\master.md -o dist\wedding_consolidated.rtf --standalone" -ForegroundColor White
Write-Host "`nCost estimate: ~$0.15 per 1000 images with OpenAI Vision API" -ForegroundColor Cyan