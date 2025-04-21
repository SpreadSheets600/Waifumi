def format_watch_time(minutes):
    days = minutes // 1440
    remaining_minutes = minutes % 1440
    hours = remaining_minutes // 60

    if days > 0:
        return f"{days}d {hours}h"
    return f"{hours}h {remaining_minutes % 60}m"


def format_top_genres(genres, limit=3):
    if not genres:
        return "No data available"

    top_genres = sorted(genres, key=lambda x: x["count"], reverse=True)[:limit]
    return ", ".join(f"{g['genre']}" for g in top_genres)


def format_about_text(about_text, max_length=300):
    if not about_text or not about_text.strip():
        return "No bio provided"

    if len(about_text) > max_length:
        return about_text[: max_length - 3] + "..."
    return about_text
