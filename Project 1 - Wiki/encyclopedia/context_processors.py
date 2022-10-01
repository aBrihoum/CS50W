from . import util


def entries_context_processor(request):
    return {
        "entries_context": util.list_entries()
    }
