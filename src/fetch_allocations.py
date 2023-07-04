from __future__ import annotations
import requests
import json
import time
from pathlib import Path
from base_allocation import BaseAllocation
from allocation import Allocation
from collections.abc import Iterable
from canonical_allocation import CanonicalAllocation



def main():
    download_allocations()





# raises AllocationError
def download_allocations(ids: Iterable[int] = range(1,1000), outdir: Path = Path.cwd()):
    markdown_dir = outdir/"markdown"
    json_dir = outdir/"json"

    markdown_dir.mkdir(exist_ok=True)
    json_dir.mkdir(exist_ok=True)

    for id in ids:
        print(f'ID {id}: processing allocation')
        try:
            a = CanonicalAllocation(get_allocation(id))
        except IDError:
            print(f'ID {id}: Failed, stopping')
            break
        print(f'ID {id}: Success: {a.long_title}')

        # write markdown
        with open(markdown_dir / f'{a.long_title}.md', 'w') as f:
            f.write(a.to_markdown())
        
        # write json
        with open(json_dir / f'{a.short_title}.json', 'w') as f:
            f.write(a.to_json())

        time.sleep(0.5)



class IDError(ValueError):
    pass

# raises: IDError, HTTPError
def get_allocation(id:int) -> Allocation[int]:
    url = f'https://breakoutroom.pythonanywhere.com/allocate/download/{id}'
    response = requests.get(url, stream=True)
    response.raise_for_status()
    if response.content.decode("utf-8") == "Unknown matching ID.":
        raise IDError()
    else:
        allocation_str = response.content.decode("utf-8")
        allocation: list[list[list[int]]] = json.loads(allocation_str)
        return Allocation.from_lists(allocation)
        




if __name__ == "__main__":
    main()