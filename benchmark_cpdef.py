#!/usr/bin/env python
"""Micro-benchmark for cpdef optimization analysis."""
import time
from odict.codict import codict

def benchmark_operation(name, operation, iterations=100000):
    """Benchmark a single operation."""
    start = time.perf_counter()
    operation()
    end = time.perf_counter()
    elapsed_ms = (end - start) * 1000
    per_op_us = (elapsed_ms * 1000) / iterations
    print(f"{name:30s}: {elapsed_ms:8.3f}ms total, {per_op_us:6.3f}µs/op")
    return elapsed_ms

print("=" * 70)
print("Codict Micro-Benchmark - cpdef Optimization Candidates")
print("=" * 70)

# Setup test data
cd = codict([(str(i), i*2) for i in range(1000)])

print("\n1. ITEM ACCESS OPERATIONS (most critical)")
print("-" * 70)

def test_getitem():
    for i in range(100000):
        _ = cd['500']
benchmark_operation("__getitem__ (dict access)", test_getitem)

def test_get():
    for i in range(100000):
        _ = cd.get('500')
benchmark_operation("get() method", test_get)

def test_contains():
    for i in range(100000):
        _ = '500' in cd
benchmark_operation("__contains__ (in operator)", test_contains)

def test_has_key():
    for i in range(100000):
        _ = cd.has_key('500')
benchmark_operation("has_key() method", test_has_key)

print("\n2. MODIFICATION OPERATIONS")
print("-" * 70)

def test_setitem():
    test_cd = codict([(str(i), i) for i in range(100)])
    for i in range(10000):
        test_cd['50'] = i
benchmark_operation("__setitem__ (assignment)", test_setitem, 10000)

def test_delitem():
    for _ in range(1000):
        test_cd = codict([(str(i), i) for i in range(100)])
        for i in range(10, 20):
            del test_cd[str(i)]
benchmark_operation("__delitem__ (deletion)", test_delitem, 10000)

print("\n3. COLLECTION OPERATIONS")
print("-" * 70)

def test_len():
    for i in range(100000):
        _ = len(cd)
benchmark_operation("__len__", test_len)

def test_keys():
    for i in range(10000):
        _ = cd.keys()
benchmark_operation("keys()", test_keys, 10000)

def test_values():
    for i in range(10000):
        _ = cd.values()
benchmark_operation("values()", test_values, 10000)

def test_items():
    for i in range(10000):
        _ = cd.items()
benchmark_operation("items()", test_items, 10000)

print("\n4. SPECIALIZED OPERATIONS")
print("-" * 70)

def test_firstkey():
    for i in range(100000):
        _ = cd.firstkey()
benchmark_operation("firstkey()", test_firstkey)

def test_lastkey():
    for i in range(100000):
        _ = cd.lastkey()
benchmark_operation("lastkey()", test_lastkey)

def test_first_key_property():
    for i in range(100000):
        _ = cd.first_key
benchmark_operation("first_key property", test_first_key_property)

def test_last_key_property():
    for i in range(100000):
        _ = cd.last_key
benchmark_operation("last_key property", test_last_key_property)

print("\n5. NAVIGATION OPERATIONS")
print("-" * 70)

def test_next_key():
    for i in range(10000):
        _ = cd.next_key('500')
benchmark_operation("next_key()", test_next_key, 10000)

def test_prev_key():
    for i in range(10000):
        _ = cd.prev_key('500')
benchmark_operation("prev_key()", test_prev_key, 10000)

print("\n" + "=" * 70)
print("Benchmark Complete")
print("=" * 70)
print("\nRECOMMENDATIONS for cpdef optimization:")
print("  HIGH PRIORITY:")
print("    - __getitem__, __setitem__, __delitem__  (called most frequently)")
print("    - __contains__, __len__                  (simple, fast operations)")
print("    - get(), has_key()                       (frequently used)")
print("  MEDIUM PRIORITY:")
print("    - keys(), values(), items()              (return lists, moderate use)")
print("    - firstkey(), lastkey()                  (simple accessors)")
print("    - next_key(), prev_key()                 (navigation)")
print("  LOW PRIORITY:")
print("    - Properties (already optimized)")
print("    - Iterator methods (incompatible with cpdef - use yield)")
print("=" * 70)
