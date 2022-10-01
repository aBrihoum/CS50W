from .models import User


def watchlist(request):
    if (request.user.is_authenticated):
        watchlist_length = len(User.objects.get(
            id=request.user.id).my_watch_list.all())
    else:
        watchlist_length = 0
    return {
        "watchlist_length": watchlist_length
    }
