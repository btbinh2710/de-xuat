#!/bin/bash
python create_db.py
gunicorn -w 4 -b 0.0.0.0:$PORT app:app