import os
import argparse


print('[*] Launch...')

filename: str = os.path.basename(__file__)

modes: dict[str, str] = {
    'dicts': 'researching with downloaded dictionaries and vector bases',
    'ai': 'researching with ai'
}


def main():
    parser = argparse.ArgumentParser(
        description='A program for researching Chinese hieroglyphs. It generates new words in the chosen research mode, '
                    'and then adds them to hieroglyph databases.',
        epilog='research modes:\n' + '\n'.join([
            f'  - {k} — {v}'
            for k, v in modes.items()
        ]),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('-m', '--mode', type=str, required=True, choices=modes.keys(), help='research mode')
    parser.add_argument('-s', '--safety', type=bool, default=False, help='safety mode — data will not be changed')
    args = parser.parse_args()

    if args.safety:
    	print('[i] Safety mode on')
    
    if args.mode == 'ai':
        from research_ai.hier_research import run
        run(safety=args.safety)
    elif args.mode == 'dicts':
        from research_dictionaries.hier_research import run
        run()#safety=args.safety)


if __name__ == '__main__':
    main()

