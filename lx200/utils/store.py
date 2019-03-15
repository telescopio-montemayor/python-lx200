import argparse
import munch

import lx200.store
import lx200.commands


if __name__ == '__main__':
    store = lx200.store.Store()

    parser = argparse.ArgumentParser(description='Utilities to create sample scope status store', prog='lx200.utils.store')

    parser.add_argument('--format', required=False, default='json',  choices=['json', 'yaml'], help='Output format, default: JSON')
    parser.add_argument('--indent', required=False, default=4,  type=int, help='Indent size, default: 4')

    args = parser.parse_args()

    if args.format == 'json':
        serialized = munch.munchify(store).toJSON(indent=args.indent, sort_keys=True)
    else:
        serialized = munch.munchify(store).toYAML(indent=args.indent)

    print(serialized)
