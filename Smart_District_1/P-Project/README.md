# Academic Portal (Terminal Based)

Student records ko end-to-end manage karne wali terminal application.

## Setup
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # Windows: copy .env.example .env  (phir token badlo)
```

## Run
```bash
python main.py --demo           # sab features ek baar automatically
python main.py                  # interactive menu (admin token do ya Enter = viewer)
python -m unittest discover tests -v
```

## Features
- CSV loading (concurrent, `asyncio`) - corrupt / missing / invalid data par crash nahi
- Custom exceptions + `logging` (file + console)
- Decorators: `@timer`, `@log_call`, `@require_role("admin")` (stackable)
- OOP: `Person` (ABC) -> `Student` -> `GraduateStudent` -> `HonorsStudent`
- Ranking (marks, phir name), binary search by name
- Failed students flag, late fines (tier-wise), timestamped reports
- `.env` config + venv

## Structure
```
main.py            CLI menu / demo
portal/config.py   .env loading          portal/models.py      OOP classes
portal/loader.py   CSV + async + generator   portal/service.py  business logic
portal/decorators.py  decorators         portal/reports.py     timestamped reports
portal/exceptions.py  custom errors      portal/utils.py       binary search
data/              sample CSVs (valid, invalid rows, corrupt, missing)
```
