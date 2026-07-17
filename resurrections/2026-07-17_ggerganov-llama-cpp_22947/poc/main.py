import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description='Llama Bench with MTP Support')
    parser.add_argument('-m', '--model', type=str, required=True, help='Model file')
    parser.add_argument('--spec-type', type=str, choices=['mtp'], help='Speculative decoding type')
    parser.add_argument('--spec-draft-n-max', type=str, help='Speculative draft n-max values (comma-separated)')
    parser.add_argument('--spec-draft-ngl', type=str, help='Speculative draft ngl values (comma-separated)')

    args = parser.parse_args()

    if args.spec_type and args.spec_type == 'mtp':
        if not args.spec_draft_n_max or not args.spec_draft_ngl:
            print('Error: --spec-draft-n-max and --spec-draft-ngl are required for --spec-type mtp')
            sys.exit(1)

        try:
            n_max_values = [int(val) for val in args.spec_draft_n_max.split(',')]
            ngl_values = [int(val) for val in args.spec_draft_ngl.split(',')]
        except ValueError:
            print('Error: Invalid values for --spec-draft-n-max or --spec-draft-ngl')
            sys.exit(1)

        print('Running MTP benchmark with model:', args.model)
        print('Spec-type:', args.spec_type)
        print('N-max values:', n_max_values)
        print('NGL values:', ngl_values)

        # Perform benchmarking here
        # ...

    else:
        print('Running standard benchmark with model:', args.model)

if __name__ == '__main__':
    main()