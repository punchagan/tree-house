from datetime import datetime

def get_days_ago(date):
    delta = datetime.now() - date
    return delta.days