# Test script to verify OCR pipeline setup
import sys
import os

def test_imports():
    """Test if all required packages can be imported"""
    try:
        import PIL
        print("✓ PIL (Pillow) imported successfully")
    except ImportError as e:
        print(f"❌ PIL import failed: {e}")
        return False
    
    try:
        import openai
        print("✓ openai imported successfully")
    except ImportError as e:
        print(f"❌ openai import failed: {e}")
        return False
    
    try:
        import cv2
        print("✓ opencv-python imported successfully")
    except ImportError as e:
        print(f"❌ opencv-python import failed: {e}")
        return False
    
    try:
        import yaml
        print("✓ PyYAML imported successfully")
    except ImportError as e:
        print(f"❌ PyYAML import failed: {e}")
        return False
    
    try:
        import dateutil
        print("✓ python-dateutil imported successfully")
    except ImportError as e:
        print(f"❌ python-dateutil import failed: {e}")
        return False
    
    try:
        import dotenv
        print("✓ python-dotenv imported successfully")
    except ImportError as e:
        print(f"❌ python-dotenv import failed: {e}")
        return False
    
    return True

def test_directories():
    """Test if required directories exist"""
    dirs = [
        "src/images_raw",
        "src/ocr_md", 
        "tools",
        "dist"
    ]
    
    all_exist = True
    for d in dirs:
        if os.path.exists(d):
            print(f"✓ Directory {d} exists")
        else:
            print(f"❌ Directory {d} missing")
            all_exist = False
    
    return all_exist

def test_environment():
    """Test if environment variables are properly configured"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            # Mask the API key for security
            masked = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "***"
            print(f"✓ OPENAI_API_KEY found: {masked}")
            return True
        else:
            print("❌ OPENAI_API_KEY not found in environment")
            print("Please create a .env file with: OPENAI_API_KEY=your_api_key_here")
            return False
    except Exception as e:
        print(f"❌ Environment test failed: {e}")
        return False

def test_files():
    """Test if required files exist"""
    files = [
        "tools/ocr_batch.py",
        "tools/normalize.yaml",
        "tools/consolidate.py",
        "requirements.txt",
        "README.md"
    ]
    
    all_exist = True
    for f in files:
        if os.path.exists(f):
            print(f"✓ File {f} exists")
        else:
            print(f"❌ File {f} missing")
            all_exist = False
    
    # Check for .env file
    if os.path.exists(".env"):
        print("✓ .env file exists")
    else:
        print("❌ .env file missing (create with OPENAI_API_KEY=your_key)")
        all_exist = False
    
    return all_exist

def main():
    print("Wedding OCR Pipeline - OpenAI Setup Test")
    print("=" * 45)
    
    print("\n1. Testing Python package imports...")
    imports_ok = test_imports()
    
    print("\n2. Testing directory structure...")
    dirs_ok = test_directories()
    
    print("\n3. Testing required files...")
    files_ok = test_files()
    
    print("\n4. Testing environment configuration...")
    env_ok = test_environment()
    
    print("\n" + "=" * 45)
    if imports_ok and dirs_ok and files_ok and env_ok:
        print("✅ All tests passed! Pipeline is ready to use.")
        print("\nNext steps:")
        print("1. Add photos to src/images_raw/")
        print("2. Run: python tools/ocr_batch.py")
        print("3. Run: python tools/consolidate.py")
        print("4. Export: pandoc src/master.md -o dist/wedding_consolidated.rtf --standalone")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        print("\nSetup instructions:")
        if not imports_ok:
            print("- Install dependencies: pip install -r requirements.txt")
        if not env_ok:
            print("- Create .env file with: OPENAI_API_KEY=your_api_key_here")
        sys.exit(1)

if __name__ == "__main__":
    main()