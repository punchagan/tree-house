#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import app
import views, models

if __name__ == '__main__':
    models.db.create_all()
    app.run('0.0.0.0', port=3000, debug=True)
