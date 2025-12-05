"""
Simple HTTP Server for Dashboard
Run this to serve dashboard.html on your local network
"""
import http.server
import socketserver
import webbrowser
import os
import socket

PORT = 8000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()

def get_local_ip():
    """Get local IP address"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = 'localhost'
    finally:
        s.close()
    return ip

def main():
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Check if dashboard.html exists
    if not os.path.exists('dashboard.html'):
        print("❌ dashboard.html not found!")
        print("Run: python generate_dashboard.py first")
        return
    
    handler = MyHTTPRequestHandler
    
    try:
        with socketserver.TCPServer(("", PORT), handler) as httpd:
            local_ip = get_local_ip()
            
            print("=" * 60)
            print("📊 Dashboard Server Started!")
            print("=" * 60)
            print(f"\nLocal access:")
            print(f"  http://localhost:{PORT}/dashboard.html")
            print(f"\nNetwork access (share with team on same network):")
            print(f"  http://{local_ip}:{PORT}/dashboard.html")
            print("\n" + "=" * 60)
            print("Press Ctrl+C to stop the server")
            print("=" * 60 + "\n")
            
            # Open browser
            webbrowser.open(f'http://localhost:{PORT}/dashboard.html')
            
            # Start server
            httpd.serve_forever()
            
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"❌ Port {PORT} is already in use.")
            print(f"   Close the other application or change PORT in this script.")
        else:
            print(f"❌ Error: {e}")
    except KeyboardInterrupt:
        print("\n\n✅ Server stopped.")

if __name__ == "__main__":
    main()

