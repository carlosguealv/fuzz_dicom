#!/usr/bin/env python3
import sys
import io
import contextlib
import os
import re
from datetime import datetime
from multiprocessing import Pool, cpu_count  # New import for multi-core support
from fuzz_dicom import differential_fuzz

# Precompile your regular expressions.
HEX_REGEX = re.compile(r'0x[0-9a-fA-F]+')
DIGITS_REGEX = re.compile(r'\d+')
PATH_REGEX = re.compile(r'(/[^ ]+)')

def normalize_error_message(msg):
    # Use the sub() method of each precompiled regex.
    msg = HEX_REGEX.sub('0x', msg)
    msg = DIGITS_REGEX.sub('', msg)
    msg = PATH_REGEX.sub('', msg)
    # Remove extra whitespace.
    return ' '.join(msg.split())

def extract_error_messages(output):
    """
    Extract and normalize error messages from the given output.
    Returns a sorted list of normalized error messages.
    """
    errors = []
    for line in output.splitlines():
        if "Error" in line or "Exception:" in line:
            normalized = normalize_error_message(line)
            errors.append(normalized)
    return sorted(errors)

def run_fuzz(data):
    """
    Runs differential_fuzz on the given data and returns the captured stdout output.
    """
    captured_output = io.StringIO()
    with contextlib.redirect_stdout(captured_output):
        try:
            differential_fuzz(data)
        except Exception as e:
            print(f"Exception: {e}")
    return captured_output.getvalue()

def test_case(data, baseline):
    """
    Runs the fuzzing function on candidate data and compares its normalized error messages
    to the baseline. Returns True if they match exactly.
    """
    output = run_fuzz(data)
    candidate_errors = extract_error_messages(output)
    return candidate_errors == baseline

# Helper function for multiprocessing.
def test_candidate(args):
    i, candidate, baseline = args
    return (i, candidate, test_case(candidate, baseline))

def ddmin(data, baseline):
    """
    Delta debugging minimizer that repeatedly tries to remove chunks of the input.
    It accepts a candidate only if the normalized error messages match the baseline.
    This version evaluates candidate removals in parallel.
    """
    n = 2
    current = data
    while len(current) > 1:
        chunk_size = max(1, len(current) // n)
        reduction_found = False

        # Prepare candidate removals.
        candidates = []
        for i in range(n):
            start = i * chunk_size
            # For the last chunk, remove everything from start to end.
            end = start + chunk_size if i < n - 1 else len(current)
            candidate = current[:start] + current[end:]
            candidates.append((i, candidate, baseline))
        
        # Evaluate candidates in parallel.
        with Pool(cpu_count()) as pool:
            results = pool.map(test_candidate, candidates)

        # Ensure results are processed in candidate order.
        results.sort(key=lambda x: x[0])
        for i, candidate, success in results:
            start = i * chunk_size
            end = start + chunk_size if i < n - 1 else len(current)
            print(f"Trying candidate of size {len(candidate)} (removed bytes {start}:{end})")
            if success:
                print(f"Reduction successful: candidate size {len(candidate)}")
                current = candidate
                n = max(n - 1, 2)
                reduction_found = True
                break  # Restart with the reduced candidate.
        if not reduction_found:
            if n >= len(current):
                break
            n = min(n * 2, len(current))
    return current

def main():
    if len(sys.argv) != 2:
        print("Usage: python minimizer.py <failing_dicom_file>")
        sys.exit(1)

    input_filename = sys.argv[1]
    try:
        with open(input_filename, "rb") as f:
            data = f.read()
    except IOError as e:
        print(f"Error reading file {input_filename}: {e}")
        sys.exit(1)

    # Capture the baseline error messages from the original failing test case.
    print("Capturing baseline error messages from original test case...")
    baseline_output = run_fuzz(data)
    baseline = extract_error_messages(baseline_output)
    print("Baseline normalized error messages:")
    for msg in baseline:
        print(msg)
    
    if not baseline:
        print("No error messages detected in the baseline test case. Exiting.")
        sys.exit(1)
    else:
        print("Baseline errors detected. Starting minimization...")

    minimized = ddmin(data, baseline)
    minimized_filename = input_filename + ".min"

    with open(minimized_filename, "wb") as f:
        f.write(minimized)
    
    print(f"Minimization complete. Minimized test case written to: {minimized_filename}")
    print(f"Original size: {len(data)} bytes, Minimized size: {len(minimized)} bytes")

if __name__ == "__main__":
    main()

