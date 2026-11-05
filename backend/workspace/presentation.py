"""View-only geometry for the dashboard's real request activity chart."""
from datetime import timedelta
from math import ceil
from django.utils import timezone


def activity_chart(created, resolved, start):
    created_days = [timezone.localtime(value).date() for value in created]
    resolved_days = [timezone.localtime(value).date() for value in resolved]
    days = [{"day": start + timedelta(days=i),
             "created": created_days.count(start + timedelta(days=i)),
             "resolved": resolved_days.count(start + timedelta(days=i))} for i in range(7)]
    peak = max([row[key] for row in days for key in ("created", "resolved")] + [1])
    ceiling = max(4, ceil(peak / 4) * 4)
    left, right, top, bottom = 46, 710, 22, 252
    for i, row in enumerate(days):
        row["x"] = round(left + i * (right - left) / 6, 2)
        for key in ("created", "resolved"):
            row[key + "_y"] = round(bottom - row[key] / ceiling * (bottom - top), 2)
    def line(key):
        return "M " + " L ".join(f'{row["x"]},{row[key + "_y"]}' for row in days)
    created_line, resolved_line = line("created"), line("resolved")
    return {"days": days, "created_line": created_line, "resolved_line": resolved_line,
            "created_area": created_line + f" L {right},{bottom} L {left},{bottom} Z",
            "resolved_area": resolved_line + f" L {right},{bottom} L {left},{bottom} Z",
            "ticks": [{"value": ceiling - i * ceiling // 4,
                       "y": top + i * (bottom-top) / 4} for i in range(5)],
            "start": start, "end": start + timedelta(days=6),
            "created_total": sum(row["created"] for row in days),
            "resolved_total": sum(row["resolved"] for row in days)}
