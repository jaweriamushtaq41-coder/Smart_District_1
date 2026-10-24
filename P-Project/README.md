# P-Project: Academic Portal (Terminal Based)

University ke liye terminal application jo student records ko shuru se akhir tak manage karti hai: CSV se data
load, records validate, failed students flag, late fines calculate aur timestamp wali reports.

## Setup (virtual environment ke andar)

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # Windows: copy .env.example .env
# phir .env mein ADMIN_TOKEN apna likh do
```

## Chalane ka tareeqa

```bash
python main.py --demo             # saare features ek baar apne aap
python main.py                    # menu (admin token do, ya Enter = viewer)
python -m unittest discover tests -v
```

## Features

| Feature | Kahan hai |
|---|---|
| CSV loading, corrupt / missing / invalid data par crash nahi | `portal/loader.py` |
| Saari files `asyncio` se ek saath load (threads + `Lock`) | `portal/loader.py` |
| Custom exceptions | `portal/exceptions.py` |
| `logging` (file + screen), named loggers | `portal/logger_setup.py` |
| Decorators: `@timer`, `@log_call`, `@require_role("admin")` (stackable) | `portal/decorators.py` |
| OOP: `Person (ABC)` -> `Student` -> `GraduateStudent` -> `HonorsStudent` | `portal/models.py` |
| Apna iterator + `StudentCollection` (`len`, `[]`, `in`, `+`, `for`) | `portal/models.py` |
| Bubble / Selection / Insertion sort aur Binary search from scratch | `portal/sorting.py` |
| Ranking, failed students, fines, department summary, reports | `portal/service.py`, `portal/reports.py` |
| `.env` se secrets (`python-dotenv`), `venv` | `portal/config.py` |

## Folder structure

```
P-Project/
├── main.py              menu aur --demo
├── requirements.txt
├── .env.example         (asli .env GitHub par nahi jati)
├── data/                sample CSV files (theek, invalid rows wali, corrupt)
├── logs/                portal.log yahan banti hai
├── reports/             timestamp wali reports yahan banti hain
├── tests/test_portal.py
└── portal/
    ├── config.py   decorators.py   exceptions.py   loader.py
    ├── logger_setup.py   models.py   reports.py   service.py   sorting.py
```

## Roles

| Role | Kya kar sakta hai |
|---|---|
| viewer | ranking, failed list, search, summary dekh sakta hai |
| admin | viewer ka sab + data load, fines, reports |

## Fine rules

Rs `FINE_PER_DAY` (default 50) har late din ka.
Undergraduate: normal, Graduate: 1.5 guna, Honors: 1.5 guna magar maximum Rs 2000.

## Pass marks

Undergraduate 40, Graduate 50, Honors 60.
