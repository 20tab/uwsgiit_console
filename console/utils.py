from __future__ import unicode_literals, absolute_import
from datetime import date, timedelta
from calendar import monthrange

from django.utils.six.moves import xrange


def diff(a, b):
    return list(set(a) - set(b))


def all_days_of(year, month=None, day=None):
        res = []
        if day and month:
            res.append(date(year, month, day))
        elif month:
            today = date.today()
            if year == today.year and month == today.month:
                last_day = today.day
            else:
                last_day = monthrange(year, month)[1]

            for d in xrange(last_day):
                res.extend(all_days_of(year, month, d+1))
        else:
            today = date.today()

            last_month = 12 if year != today.year else today.month

            for m in xrange(1, last_month+1):
                res.extend(all_days_of(year, m))
        return res


def excluded_days(all_days, days_to_exclude):
    return diff(all_days, days_to_exclude)


def daterange(start_date, end_date):
    for n in xrange((end_date - start_date).days + 1):
        yield start_date + timedelta(n)
