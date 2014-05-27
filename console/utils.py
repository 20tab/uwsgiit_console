from django.utils.dates import MONTHS
from datetime import date
from calendar import monthrange


def diff(a, b):
    return list(set(a) - set(b))


def all_days_of(year, month=None, day=None):
        res = []
        if day and month:
            res.append(date(year, month, day))
        elif month:
            for d in xrange(monthrange(year, month)[1]):
                res.extend(all_days_of(year, month, d+1))
        else:
            for m in MONTHS.keys():
                res.extend(all_days_of(year, m))
        return res


def exluded_days(all_days, days_to_exclude):
    return diff(all_days, days_to_exclude)