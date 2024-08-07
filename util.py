from typing import Iterable


def flatten(iterable):
    for item in iterable:
        if isinstance(item, Iterable) and not isinstance(item, (str, bytes)):
            # Pokud je položka iterovatelná (a není řetězec ani bajty), rekurzivně voláme flatten
            yield from flatten(item)
        else:
            # Jinak vracíme položku přímo
            yield item

if __name__ == "__main__":
    print(list(flatten([2,[3,5]])))