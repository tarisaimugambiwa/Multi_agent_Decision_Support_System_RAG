"""
Simple HTTPS wrapper for Django development server
"""
import os
import sys

# Add the project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medical_ai.settings')

# Import Django and set it up
import django
django.setup()

# Import the WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# SSL configuration
import ssl
from werkzeug.serving import run_simple

if __name__ == "__main__":
    # SSL context
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain('ssl/cert.pem', 'ssl/key.pem')
    
    print("=" * 60)
    print("HTTPS Django Development Server")
    print("Certificate valid for 365 days")
    print("=" * 60)
    print()
    print("Access the application at:")
    print("  🔒 Local:   https://127.0.0.1:8000")
    print("  🔒 Network: https://192.168.14.240:8000")
    print()
    print("⚠️  Browser Security Warning:")
    print("   You'll see a warning because this is a self-signed certificate.")
    print("   Click 'Advanced' → 'Proceed to site' to continue.")
    print()
    print("Press CTRL+C to stop the server")
    print("=" * 60)
    print()
    
    # Run HTTPS server
    run_simple(
        '0.0.0.0',
        8000,
        application,
        use_reloader=True,
        use_debugger=True,
        ssl_context=ssl_context
    )
