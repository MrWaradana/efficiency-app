# -*- coding: utf-8 -*-

import multiprocessing
import os
from dotenv import load_dotenv

load_dotenv()

bind = f"0.0.0.0:{os.getenv('APPLICATION_PORT', 3000)}"
accesslog = "-"
access_log_format = "%(h)s %(l)s %(u)s %(t)s '%(r)s' %(s)s %(b)s '%(f)s' '%(a)s' in %(D)sµs"  # noqa: E501

workers = int(os.getenv("WEB_CONCURRENCY", multiprocessing.cpu_count() * 2))
threads = int(os.getenv("PYTHON_MAX_THREADS", 1))

reload = True

timeout = int(os.getenv("WEB_TIMEOUT", 120))
