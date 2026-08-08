"""
Master menu for flac-library-tools.
Run this from the project root: python3 master.py
"""

import importlib
import pkgutil

import tools


def discover_tools():
    found = {}
    for _, name, _ in pkgutil.iter_modules(tools.__path__):
        try:
            mod = importlib.import_module(f"tools.{name}")
        except Exception as e:
            print(f"Could not load tools.{name}: {e}")
            continue

        if hasattr(mod, "run"):
            desc = getattr(mod, "DESCRIPTION", name)
            found[name] = (desc, mod.run)

    return found


def main():
    tools_map = discover_tools()
    names = sorted(tools_map)

    if not names:
        print("No tools found in tools/. Check that files define run().")
        return

    while True:
        print("\n" + "=" * 50)
        print("flac-library-tools")
        print("=" * 50)
        for i, name in enumerate(names, 1):
            desc, _ = tools_map[name]
            print(f"{i}. {desc}")
        print("0. Exit")

        choice = input("\nPick: ").strip()

        if choice == "0":
            break

        try:
            idx = int(choice) - 1
            if idx < 0:
                raise ValueError
            name = names[idx]
        except (ValueError, IndexError):
            print("Invalid choice.")
            continue

        print()
        try:
            tools_map[name][1]()
        except KeyboardInterrupt:
            print("\nInterrupted.")
        except Exception as e:
            print(f"Tool crashed: {e}")


if __name__ == "__main__":
    main()