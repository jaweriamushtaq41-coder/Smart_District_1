# P-Task10: Async Data Sync Dashboard

Teen mock sources se ek saath data khinchna (`asyncio.gather`), merge karna aur combined summary dikhana.
Saath mein threads + Lock aur multiprocessing ke chhote demos.

- **Files:** `async_data_sync_dashboard.ipynb`, `workers.py`, `requirements.txt`, `.env.example`

## Chalane ka tareeqa
```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # phir .env mein apni keys likho
```
Phir notebook kholo (venv wala kernel select karke) aur *Run All* karo.
`.env` GitHub par push nahi hoti, sirf `.env.example` hoti hai.
