import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import uvicorn

if __name__ == '__main__':
    uvicorn.run(
        'agent.main:app',
        host='127.0.0.1',
        port=8000,
        log_level='info',
    )
