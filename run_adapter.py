import uvicorn
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'adapter_1c'))

if __name__ == "__main__":
    uvicorn.run(
        "adapter_1c.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )