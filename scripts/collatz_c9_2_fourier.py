import argparse
import csv
import json
import math
import os


def compute_dft(values):
    N = len(values)
    if N == 0:
        return []
    spectrum = []
    for k in range(N):
        re = 0.0
        im = 0.0
        for n, v in enumerate(values):
            angle = 2 * math.pi * k * n / N
            re += v * math.cos(angle)
            im -= v * math.sin(angle)
        magnitude = math.sqrt(re * re + im * im)
        phase = math.atan2(im, re)
        spectrum.append({'k': k, 're': re, 'im': im, 'magnitude': magnitude, 'phase': phase})
    return spectrum


def find_modes(spectrum, top_n=10):
    sorted_modes = sorted(spectrum, key=lambda x: x['magnitude'], reverse=True)
    return sorted_modes[:top_n]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='C9.2 Fourier Analysis')
    parser.add_argument('--input', type=str, required=True, help='Input CSV file (output of collatz_c9_2_sampling.py)')
    parser.add_argument('--output-dir', type=str, default=None, help='Directory for output files (defaults to input file directory)')
    parser.add_argument('--top-modes', type=int, default=10, help='Number of top Fourier modes to record')

    args = parser.parse_args()

    input_path = args.input
    output_dir = args.output_dir or os.path.dirname(os.path.abspath(input_path))

    base = os.path.splitext(os.path.basename(input_path))[0]

    values = []
    with open(input_path, 'r', newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            if row:
                values.append(float(row[0]))

    spectrum = compute_dft(values)
    modes = find_modes(spectrum, top_n=args.top_modes)

    fourier_json_path = os.path.join(output_dir, f'{base}_fourier.json')
    with open(fourier_json_path, 'w') as f:
        json.dump({'input': input_path, 'N': len(values), 'spectrum': spectrum}, f, indent=2)

    fourier_modes_csv_path = os.path.join(output_dir, f'{base}_fourier_modes.csv')
    with open(fourier_modes_csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['k', 're', 'im', 'magnitude', 'phase'])
        writer.writeheader()
        writer.writerows(modes)

    print(f'Wrote {fourier_json_path}')
    print(f'Wrote {fourier_modes_csv_path}')
