def get_user_level(rating):
    if not rating:
        return "Beginner"
    if rating<1000:
        return "Beginner"
    elif rating<=1400:
        return "Intermediate"
    else:
        return "Advanced"
