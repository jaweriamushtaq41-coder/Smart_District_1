# P-Task6: Server Log Error Streamer

100,000 lines ki log file ko line by line stream karna, sirf ERROR / CRITICAL entries yield karna, error type ke hisaab
se live count dikhana. Poori file kabhi memory mein load nahi hoti.

- **File:** `server_log_error_streamer.ipynb` (log file notebook khud banata hai aur end par delete kar deta hai)
- **Concepts:** `__iter__` / `__next__`, generators (`yield`), generator expressions, `itertools`
