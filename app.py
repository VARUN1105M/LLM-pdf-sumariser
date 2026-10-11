import sys
import uvicorn
from src.config import settings

def main():
    print("=" * 65)
    print(f"  🚀  {settings.PROJECT_NAME} v{settings.VERSION}")
    print("      Forward Deployed Product & Growth Intelligence")
    print("=" * 65)
    print(f"  • Web UI:       http://localhost:{settings.PORT}")
    print(f"  • API Docs:     http://localhost:{settings.PORT}/docs")
    print(f"  • Health Check: http://localhost:{settings.PORT}/api/health")
    print(f"  • Database:     {settings.DATABASE_URL}")
    print(f"  • LLM Provider: {settings.DEFAULT_LLM_PROVIDER}")
    print("=" * 65)
    
    uvicorn.run(
        "src.api.server:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False
    )

if __name__ == "__main__":
    main()