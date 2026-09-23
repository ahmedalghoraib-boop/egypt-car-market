#!/bin/bash
set -e
cd /tmp/car-site
cp index.html.bak_unify index.html
python3 unify_arabic.py
python3 polish.py
python3 polish2.py
python3 chips_fill.py
python3 chips_fill2.py
echo "pipeline done"
