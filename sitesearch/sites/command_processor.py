from sitesearch.models import TYPE_PAGE, SearchDocument
import json
from os import path

def process_commands(command_filename):
    pages = {}
    filename = path.join(path.dirname(__file__), 'commands.json')
    with open(filename) as f:
        data = json.load(f)
        keys = data.keys()
        for key in keys:
            if (' ' not in key) and len(key) < 10:
                downcased_key = key.lower()
                page = SearchDocument(
                        doc_id=f"redisio://commands/landing/{downcased_key}",
                        title=key,
                        section_title="",
                        hierarchy=["Redis", "Commands"],
                        s=downcased_key,
                        url=f"/commands/{downcased_key}/",
                        body=data[key].get('summary', f"Documentation for command '{downcased_key}'"),
                        type=TYPE_PAGE,
                        position=0
                    )
                pages[downcased_key] = page
    
    return pages