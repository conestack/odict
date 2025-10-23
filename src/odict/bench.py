# Python Software Foundation License
"""
Comprehensive benchmark suite for odict implementations.

Compares performance and memory usage of all public API methods across:
- dict (Python built-in)
- OrderedDict (collections.OrderedDict)
- odict (Python implementation from this package)
- codict (Cython-optimized implementation)
"""
from collections import OrderedDict
from .pyodict import odict
try:
    from .codict import codict
    HAS_CODICT = True
except ImportError:
    HAS_CODICT = False
import time
import gc
import tracemalloc
import sys


# Configuration
SIZES = [1000, 10000, 100000, 1000000]
MICRO_ITERATIONS = 10000  # For fast operations
MACRO_ITERATIONS = 1000   # For slow operations
WARMUP_ITERATIONS = 100


class BenchmarkRunner:
    """Main benchmark runner for all odict methods."""

    def __init__(self):
        """Initialize benchmark runner with available implementations."""
        self.implementations = {
            'dict': dict,
            'OrderedDict': OrderedDict,
            'odict': odict,
        }
        if HAS_CODICT:
            self.implementations['codict'] = codict

        self.results = {}

    def has_method(self, impl_class, method_name):
        """Check if implementation has the specified method."""
        if method_name.startswith('__') and method_name.endswith('__'):
            # Special methods - check on instance
            try:
                obj = impl_class()
                return hasattr(obj, method_name)
            except:
                return False
        else:
            # Regular methods
            return hasattr(impl_class, method_name) or hasattr(impl_class(), method_name)

    def benchmark_method(self, method_name, setup_fn, test_fn, iterations=MICRO_ITERATIONS):
        """
        Benchmark a specific method across all implementations and sizes.

        Args:
            method_name: Name of the method being tested
            setup_fn: Function(impl_class, size) -> test object
            test_fn: Function(obj, size, iterations) -> None
            iterations: Number of times to run the operation

        Returns:
            dict: Results keyed by (impl_name, size)
        """
        results = {}

        for size in SIZES:
            for impl_name, impl_class in self.implementations.items():
                # Skip if method not available
                if not self.has_method(impl_class, method_name):
                    continue

                try:
                    # Setup test object
                    test_obj = setup_fn(impl_class, size)

                    # Warmup
                    warmup_obj = setup_fn(impl_class, min(size, 100))
                    test_fn(warmup_obj, min(size, 100), WARMUP_ITERATIONS)
                    del warmup_obj

                    # Force garbage collection and reset memory tracking
                    gc.collect()
                    tracemalloc.start()
                    mem_before = tracemalloc.get_traced_memory()[0]

                    # Measure time
                    start = time.perf_counter()
                    test_fn(test_obj, size, iterations)
                    end = time.perf_counter()

                    # Measure memory after
                    mem_after = tracemalloc.get_traced_memory()[0]
                    tracemalloc.stop()

                    # Store results
                    time_ms = (end - start) * 1000
                    memory_kb = (mem_after - mem_before) / 1024

                    results[(impl_name, size)] = {
                        'time_ms': time_ms,
                        'memory_kb': memory_kb,
                        'iterations': iterations
                    }

                    # Cleanup
                    del test_obj
                    gc.collect()

                except Exception as e:
                    # If benchmark fails, just skip this combination
                    print(f"  [Skipped {impl_name} at size {size}: {e}]", file=sys.stderr)
                    continue

        return results

    def print_table(self, method_name, results, description=""):
        """
        Print formatted results table for a method.

        Args:
            method_name: Name of the method
            results: Results dict from benchmark_method
            description: Optional description of what's being measured
        """
        print(f"\n{'=' * 110}")
        print(f"Method: {method_name}")
        if description:
            print(f"Description: {description}")
        print(f"{'=' * 110}")

        for size in SIZES:
            # Check if we have any results for this size
            has_results = any((impl, size) in results for impl in self.implementations.keys())
            if not has_results:
                continue

            print(f"\n--- Size: {size:,} objects ---")
            print(f"{'Implementation':<15} | {'Time (ms)':<12} | {'vs odict':<12} | {'Memory (KB)':<12} | {'vs odict':<12}")
            print("-" * 110)

            # Get odict baseline
            odict_data = results.get(('odict', size))
            odict_time = odict_data['time_ms'] if odict_data else None
            odict_mem = odict_data['memory_kb'] if odict_data else None

            # Print results for each implementation
            for impl in ['dict', 'OrderedDict', 'odict', 'codict']:
                if (impl, size) not in results:
                    print(f"{impl:<15} | {'N/A':<12} | {'-':<12} | {'N/A':<12} | {'-':<12}")
                    continue

                data = results[(impl, size)]
                time_ms = data['time_ms']
                mem_kb = data['memory_kb']

                # Calculate percentages vs odict
                if odict_time and impl != 'odict' and odict_time > 0:
                    time_pct = ((time_ms - odict_time) / odict_time) * 100
                    time_vs = f"{time_pct:+7.1f}%"
                else:
                    time_vs = "-"

                if odict_mem and impl != 'odict' and abs(odict_mem) > 0.001:
                    mem_pct = ((mem_kb - odict_mem) / abs(odict_mem)) * 100
                    mem_vs = f"{mem_pct:+7.1f}%"
                else:
                    mem_vs = "-"

                print(f"{impl:<15} | {time_ms:>10.3f}ms | {time_vs:<12} | {mem_kb:>10.3f}KB | {mem_vs:<12}")

    def benchmark_and_print(self, method_name, setup_fn, test_fn, iterations=MICRO_ITERATIONS, description=""):
        """Convenience method to benchmark and immediately print results."""
        print(f"\n[Benchmarking {method_name}...]")
        results = self.benchmark_method(method_name, setup_fn, test_fn, iterations)
        self.results[method_name] = results
        self.print_table(method_name, results, description)


# ============================================================================
# Setup Functions
# ============================================================================

def setup_populated(impl_class, size):
    """Create a populated dict/odict/codict with 'size' items."""
    return impl_class([(str(i), i * 2) for i in range(size)])


def setup_empty(impl_class, size):
    """Create an empty dict/odict/codict."""
    return impl_class()


def setup_for_iteration(impl_class, size):
    """Create a populated dict for iteration tests."""
    return impl_class([(str(i), i * 2) for i in range(size)])


# ============================================================================
# Test Functions: Basic Dictionary Operations
# ============================================================================

def test_getitem(obj, size, iterations):
    """Test __getitem__ (d['key'])"""
    keys = [str(i) for i in range(min(size, 100))]
    for _ in range(iterations):
        for key in keys:
            _ = obj[key]


def test_setitem(obj, size, iterations):
    """Test __setitem__ (d['key'] = value)"""
    for i in range(iterations):
        obj[str(i % size)] = i * 3


def test_delitem(obj, size, iterations):
    """Test __delitem__ (del d['key'])"""
    # We need to recreate obj for each iteration
    impl_class = type(obj)
    for _ in range(iterations):
        test_obj = impl_class([(str(i), i) for i in range(min(size, 100))])
        for i in range(min(size, 50)):
            try:
                del test_obj[str(i)]
            except KeyError:
                pass


def test_contains(obj, size, iterations):
    """Test __contains__ ('key' in d)"""
    keys = [str(i) for i in range(min(size, 100))]
    for _ in range(iterations):
        for key in keys:
            _ = key in obj


def test_len(obj, size, iterations):
    """Test __len__ (len(d))"""
    for _ in range(iterations):
        _ = len(obj)


def test_get(obj, size, iterations):
    """Test get(key, default)"""
    keys = [str(i) for i in range(min(size, 100))]
    for _ in range(iterations):
        for key in keys:
            _ = obj.get(key, None)


def test_has_key(obj, size, iterations):
    """Test has_key(key) - odict/codict only"""
    keys = [str(i) for i in range(min(size, 100))]
    for _ in range(iterations):
        for key in keys:
            _ = obj.has_key(key)


def test_keys(obj, size, iterations):
    """Test keys()"""
    for _ in range(iterations):
        _ = list(obj.keys())


def test_values(obj, size, iterations):
    """Test values()"""
    for _ in range(iterations):
        _ = list(obj.values())


def test_items(obj, size, iterations):
    """Test items()"""
    for _ in range(iterations):
        _ = list(obj.items())


def test_clear(obj, size, iterations):
    """Test clear()"""
    impl_class = type(obj)
    for _ in range(iterations):
        test_obj = impl_class([(str(i), i) for i in range(min(size, 100))])
        test_obj.clear()


def test_copy(obj, size, iterations):
    """Test copy()"""
    for _ in range(iterations):
        _ = obj.copy()


def test_update(obj, size, iterations):
    """Test update(data)"""
    update_data = {str(i): i * 3 for i in range(min(size, 100))}
    for _ in range(iterations):
        obj.update(update_data)


def test_setdefault(obj, size, iterations):
    """Test setdefault(key, default)"""
    for i in range(iterations):
        obj.setdefault(str(i % size), i)


def test_pop(obj, size, iterations):
    """Test pop(key, default)"""
    impl_class = type(obj)
    for _ in range(iterations):
        test_obj = impl_class([(str(i), i) for i in range(min(size, 100))])
        for i in range(min(size, 50)):
            test_obj.pop(str(i), None)


def test_popitem(obj, size, iterations):
    """Test popitem()"""
    impl_class = type(obj)
    for _ in range(iterations):
        test_obj = impl_class([(str(i), i) for i in range(min(size, 100))])
        try:
            while True:
                test_obj.popitem()
        except (KeyError, IndexError):
            pass


def test_fromkeys(obj, size, iterations):
    """Test fromkeys(keys, value) - class method"""
    impl_class = type(obj)
    keys = [str(i) for i in range(min(size, 100))]
    for _ in range(iterations):
        _ = impl_class.fromkeys(keys, 0)


# ============================================================================
# Test Functions: Iteration Operations
# ============================================================================

def test_iter(obj, size, iterations):
    """Test __iter__ (for key in d)"""
    for _ in range(iterations):
        for key in obj:
            pass


def test_reversed(obj, size, iterations):
    """Test __reversed__ (for key in reversed(d))"""
    for _ in range(iterations):
        for key in reversed(obj):
            pass


def test_iterkeys(obj, size, iterations):
    """Test iterkeys() - odict/codict only"""
    for _ in range(iterations):
        for key in obj.iterkeys():
            pass


def test_itervalues(obj, size, iterations):
    """Test itervalues() - odict/codict only"""
    for _ in range(iterations):
        for value in obj.itervalues():
            pass


def test_iteritems(obj, size, iterations):
    """Test iteritems() - odict/codict only"""
    for _ in range(iterations):
        for key, value in obj.iteritems():
            pass


def test_riterkeys(obj, size, iterations):
    """Test riterkeys() - odict/codict only"""
    for _ in range(iterations):
        for key in obj.riterkeys():
            pass


def test_ritervalues(obj, size, iterations):
    """Test ritervalues() - odict/codict only"""
    for _ in range(iterations):
        for value in obj.ritervalues():
            pass


def test_riteritems(obj, size, iterations):
    """Test riteritems() - odict/codict only"""
    for _ in range(iterations):
        for key, value in obj.riteritems():
            pass


def test_rkeys(obj, size, iterations):
    """Test rkeys() - odict/codict only"""
    for _ in range(iterations):
        _ = obj.rkeys()


def test_rvalues(obj, size, iterations):
    """Test rvalues() - odict/codict only"""
    for _ in range(iterations):
        _ = obj.rvalues()


def test_ritems(obj, size, iterations):
    """Test ritems() - odict/codict only"""
    for _ in range(iterations):
        _ = obj.ritems()


# ============================================================================
# Test Functions: Ordered Dict Specific Operations
# ============================================================================

def test_firstkey(obj, size, iterations):
    """Test firstkey() - odict/codict only"""
    for _ in range(iterations):
        _ = obj.firstkey()


def test_lastkey(obj, size, iterations):
    """Test lastkey() - odict/codict only"""
    for _ in range(iterations):
        _ = obj.lastkey()


def test_first_key_property(obj, size, iterations):
    """Test first_key property - odict/codict only"""
    for _ in range(iterations):
        _ = obj.first_key


def test_last_key_property(obj, size, iterations):
    """Test last_key property - odict/codict only"""
    for _ in range(iterations):
        _ = obj.last_key


def test_next_key(obj, size, iterations):
    """Test next_key(key) - odict/codict only"""
    key = str(size // 2) if size > 0 else '0'
    for _ in range(iterations):
        try:
            _ = obj.next_key(key)
        except (KeyError, StopIteration):
            pass


def test_prev_key(obj, size, iterations):
    """Test prev_key(key) - odict/codict only"""
    key = str(size // 2) if size > 0 else '0'
    for _ in range(iterations):
        try:
            _ = obj.prev_key(key)
        except (KeyError, StopIteration):
            pass


def test_sort(obj, size, iterations):
    """Test sort() - odict/codict only"""
    impl_class = type(obj)
    for _ in range(iterations):
        test_obj = impl_class([(str(i), i) for i in range(min(size, 100))])
        test_obj.sort()


def test_alter_key(obj, size, iterations):
    """Test alter_key(old, new) - odict/codict only"""
    impl_class = type(obj)
    for _ in range(iterations):
        test_obj = impl_class([(str(i), i) for i in range(min(size, 100))])
        if len(test_obj) > 0:
            test_obj.alter_key('0', 'renamed_0')


def test_swap(obj, size, iterations):
    """Test swap(a, b) - odict/codict only"""
    impl_class = type(obj)
    for _ in range(iterations):
        test_obj = impl_class([(str(i), i) for i in range(min(size, 100))])
        if len(test_obj) > 1:
            test_obj.swap('0', '1')


def test_insertbefore(obj, size, iterations):
    """Test insertbefore(ref, key, value) - odict/codict only"""
    impl_class = type(obj)
    for _ in range(iterations):
        test_obj = impl_class([(str(i), i) for i in range(min(size, 100))])
        if len(test_obj) > 0:
            test_obj.insertbefore('0', 'new', 999)


def test_insertafter(obj, size, iterations):
    """Test insertafter(ref, key, value) - odict/codict only"""
    impl_class = type(obj)
    for _ in range(iterations):
        test_obj = impl_class([(str(i), i) for i in range(min(size, 100))])
        if len(test_obj) > 0:
            test_obj.insertafter('0', 'new', 999)


def test_insertfirst(obj, size, iterations):
    """Test insertfirst(key, value) - odict/codict only"""
    impl_class = type(obj)
    for _ in range(iterations):
        test_obj = impl_class([(str(i), i) for i in range(min(size, 100))])
        test_obj.insertfirst('new', 999)


def test_insertlast(obj, size, iterations):
    """Test insertlast(key, value) - odict/codict only"""
    impl_class = type(obj)
    for _ in range(iterations):
        test_obj = impl_class([(str(i), i) for i in range(min(size, 100))])
        test_obj.insertlast('new', 999)


def test_movebefore(obj, size, iterations):
    """Test movebefore(ref, key) - odict/codict only"""
    impl_class = type(obj)
    for _ in range(iterations):
        test_obj = impl_class([(str(i), i) for i in range(min(size, 100))])
        if len(test_obj) > 1:
            test_obj.movebefore('0', '1')


def test_moveafter(obj, size, iterations):
    """Test moveafter(ref, key) - odict/codict only"""
    impl_class = type(obj)
    for _ in range(iterations):
        test_obj = impl_class([(str(i), i) for i in range(min(size, 100))])
        if len(test_obj) > 1:
            test_obj.moveafter('0', '1')


def test_movefirst(obj, size, iterations):
    """Test movefirst(key) - odict/codict only"""
    impl_class = type(obj)
    for _ in range(iterations):
        test_obj = impl_class([(str(i), i) for i in range(min(size, 100))])
        if len(test_obj) > 0:
            test_obj.movefirst(str(len(test_obj) - 1))


def test_movelast(obj, size, iterations):
    """Test movelast(key) - odict/codict only"""
    impl_class = type(obj)
    for _ in range(iterations):
        test_obj = impl_class([(str(i), i) for i in range(min(size, 100))])
        if len(test_obj) > 0:
            test_obj.movelast('0')


def test_as_dict(obj, size, iterations):
    """Test as_dict() - odict/codict only"""
    for _ in range(iterations):
        _ = obj.as_dict()


def test_lh_property(obj, size, iterations):
    """Test lh property (list head) - odict/codict only"""
    for _ in range(iterations):
        _ = obj.lh


def test_lt_property(obj, size, iterations):
    """Test lt property (list tail) - odict/codict only"""
    for _ in range(iterations):
        _ = obj.lt


# ============================================================================
# Main Runner
# ============================================================================

def run():
    """Main benchmark runner."""
    runner = BenchmarkRunner()

    print("\n" + "=" * 110)
    print("ODICT COMPREHENSIVE BENCHMARK SUITE")
    print("=" * 110)
    print(f"\nComparing implementations: {', '.join(runner.implementations.keys())}")
    print(f"Test sizes: {', '.join(str(s) for s in SIZES)}")
    print(f"Micro-benchmark iterations: {MICRO_ITERATIONS:,}")
    print(f"Macro-benchmark iterations: {MACRO_ITERATIONS:,}")
    print("\nNote: Negative % means faster/less memory than odict (baseline)")
    print("      'N/A' means method not available on that implementation")

    # ========================================================================
    # CATEGORY 1: Basic Dictionary Operations
    # ========================================================================
    print("\n" + "=" * 110)
    print("CATEGORY 1: BASIC DICTIONARY OPERATIONS")
    print("=" * 110)

    runner.benchmark_and_print('__getitem__', setup_populated, test_getitem,
                               description="Access item by key: d['key']")

    runner.benchmark_and_print('__setitem__', setup_populated, test_setitem,
                               description="Set item by key: d['key'] = value")

    runner.benchmark_and_print('__delitem__', setup_populated, test_delitem,
                               iterations=MACRO_ITERATIONS,
                               description="Delete item by key: del d['key']")

    runner.benchmark_and_print('__contains__', setup_populated, test_contains,
                               description="Check if key exists: 'key' in d")

    runner.benchmark_and_print('__len__', setup_populated, test_len,
                               description="Get dictionary length: len(d)")

    runner.benchmark_and_print('get', setup_populated, test_get,
                               description="Get with default: d.get(key, default)")

    runner.benchmark_and_print('has_key', setup_populated, test_has_key,
                               description="Check if key exists: d.has_key(key) [odict/codict only]")

    runner.benchmark_and_print('keys', setup_populated, test_keys,
                               iterations=MACRO_ITERATIONS,
                               description="Get list of keys: d.keys()")

    runner.benchmark_and_print('values', setup_populated, test_values,
                               iterations=MACRO_ITERATIONS,
                               description="Get list of values: d.values()")

    runner.benchmark_and_print('items', setup_populated, test_items,
                               iterations=MACRO_ITERATIONS,
                               description="Get list of items: d.items()")

    runner.benchmark_and_print('clear', setup_populated, test_clear,
                               iterations=MACRO_ITERATIONS,
                               description="Remove all items: d.clear()")

    runner.benchmark_and_print('copy', setup_populated, test_copy,
                               iterations=MACRO_ITERATIONS,
                               description="Create shallow copy: d.copy()")

    runner.benchmark_and_print('update', setup_populated, test_update,
                               iterations=MACRO_ITERATIONS,
                               description="Update with dict: d.update(other)")

    runner.benchmark_and_print('setdefault', setup_populated, test_setdefault,
                               description="Set if not exists: d.setdefault(key, default)")

    runner.benchmark_and_print('pop', setup_populated, test_pop,
                               iterations=MACRO_ITERATIONS,
                               description="Pop key with default: d.pop(key, default)")

    runner.benchmark_and_print('popitem', setup_populated, test_popitem,
                               iterations=MACRO_ITERATIONS,
                               description="Pop last item: d.popitem()")

    runner.benchmark_and_print('fromkeys', setup_empty, test_fromkeys,
                               iterations=MACRO_ITERATIONS,
                               description="Create from keys: dict.fromkeys(keys, value)")

    # ========================================================================
    # CATEGORY 2: Iteration Operations
    # ========================================================================
    print("\n" + "=" * 110)
    print("CATEGORY 2: ITERATION OPERATIONS")
    print("=" * 110)

    runner.benchmark_and_print('__iter__', setup_populated, test_iter,
                               iterations=MACRO_ITERATIONS,
                               description="Forward iteration: for key in d")

    runner.benchmark_and_print('__reversed__', setup_populated, test_reversed,
                               iterations=MACRO_ITERATIONS,
                               description="Reverse iteration: for key in reversed(d)")

    runner.benchmark_and_print('iterkeys', setup_populated, test_iterkeys,
                               iterations=MACRO_ITERATIONS,
                               description="Iterate keys: for key in d.iterkeys() [odict/codict only]")

    runner.benchmark_and_print('itervalues', setup_populated, test_itervalues,
                               iterations=MACRO_ITERATIONS,
                               description="Iterate values: for val in d.itervalues() [odict/codict only]")

    runner.benchmark_and_print('iteritems', setup_populated, test_iteritems,
                               iterations=MACRO_ITERATIONS,
                               description="Iterate items: for k,v in d.iteritems() [odict/codict only]")

    runner.benchmark_and_print('riterkeys', setup_populated, test_riterkeys,
                               iterations=MACRO_ITERATIONS,
                               description="Reverse iterate keys: d.riterkeys() [odict/codict only]")

    runner.benchmark_and_print('ritervalues', setup_populated, test_ritervalues,
                               iterations=MACRO_ITERATIONS,
                               description="Reverse iterate values: d.ritervalues() [odict/codict only]")

    runner.benchmark_and_print('riteritems', setup_populated, test_riteritems,
                               iterations=MACRO_ITERATIONS,
                               description="Reverse iterate items: d.riteritems() [odict/codict only]")

    runner.benchmark_and_print('rkeys', setup_populated, test_rkeys,
                               iterations=MACRO_ITERATIONS,
                               description="Get reverse keys list: d.rkeys() [odict/codict only]")

    runner.benchmark_and_print('rvalues', setup_populated, test_rvalues,
                               iterations=MACRO_ITERATIONS,
                               description="Get reverse values list: d.rvalues() [odict/codict only]")

    runner.benchmark_and_print('ritems', setup_populated, test_ritems,
                               iterations=MACRO_ITERATIONS,
                               description="Get reverse items list: d.ritems() [odict/codict only]")

    # ========================================================================
    # CATEGORY 3: Ordered Dict Specific Operations
    # ========================================================================
    print("\n" + "=" * 110)
    print("CATEGORY 3: ORDERED DICT SPECIFIC OPERATIONS")
    print("=" * 110)

    runner.benchmark_and_print('firstkey', setup_populated, test_firstkey,
                               description="Get first key: d.firstkey() [odict/codict only]")

    runner.benchmark_and_print('lastkey', setup_populated, test_lastkey,
                               description="Get last key: d.lastkey() [odict/codict only]")

    runner.benchmark_and_print('first_key', setup_populated, test_first_key_property,
                               description="Get first key property: d.first_key [odict/codict only]")

    runner.benchmark_and_print('last_key', setup_populated, test_last_key_property,
                               description="Get last key property: d.last_key [odict/codict only]")

    runner.benchmark_and_print('next_key', setup_populated, test_next_key,
                               description="Get next key: d.next_key(key) [odict/codict only]")

    runner.benchmark_and_print('prev_key', setup_populated, test_prev_key,
                               description="Get previous key: d.prev_key(key) [odict/codict only]")

    runner.benchmark_and_print('sort', setup_populated, test_sort,
                               iterations=MACRO_ITERATIONS,
                               description="Sort by keys: d.sort() [odict/codict only]")

    runner.benchmark_and_print('alter_key', setup_populated, test_alter_key,
                               iterations=MACRO_ITERATIONS,
                               description="Rename key: d.alter_key(old, new) [odict/codict only]")

    runner.benchmark_and_print('swap', setup_populated, test_swap,
                               iterations=MACRO_ITERATIONS,
                               description="Swap two keys: d.swap(a, b) [odict/codict only]")

    runner.benchmark_and_print('insertbefore', setup_populated, test_insertbefore,
                               iterations=MACRO_ITERATIONS,
                               description="Insert before key: d.insertbefore(ref, key, val) [odict/codict only]")

    runner.benchmark_and_print('insertafter', setup_populated, test_insertafter,
                               iterations=MACRO_ITERATIONS,
                               description="Insert after key: d.insertafter(ref, key, val) [odict/codict only]")

    runner.benchmark_and_print('insertfirst', setup_populated, test_insertfirst,
                               iterations=MACRO_ITERATIONS,
                               description="Insert at start: d.insertfirst(key, val) [odict/codict only]")

    runner.benchmark_and_print('insertlast', setup_populated, test_insertlast,
                               iterations=MACRO_ITERATIONS,
                               description="Insert at end: d.insertlast(key, val) [odict/codict only]")

    runner.benchmark_and_print('movebefore', setup_populated, test_movebefore,
                               iterations=MACRO_ITERATIONS,
                               description="Move key before ref: d.movebefore(ref, key) [odict/codict only]")

    runner.benchmark_and_print('moveafter', setup_populated, test_moveafter,
                               iterations=MACRO_ITERATIONS,
                               description="Move key after ref: d.moveafter(ref, key) [odict/codict only]")

    runner.benchmark_and_print('movefirst', setup_populated, test_movefirst,
                               iterations=MACRO_ITERATIONS,
                               description="Move key to start: d.movefirst(key) [odict/codict only]")

    runner.benchmark_and_print('movelast', setup_populated, test_movelast,
                               iterations=MACRO_ITERATIONS,
                               description="Move key to end: d.movelast(key) [odict/codict only]")

    runner.benchmark_and_print('as_dict', setup_populated, test_as_dict,
                               iterations=MACRO_ITERATIONS,
                               description="Convert to dict: d.as_dict() [odict/codict only]")

    runner.benchmark_and_print('lh', setup_populated, test_lh_property,
                               description="Get list head: d.lh [odict/codict only]")

    runner.benchmark_and_print('lt', setup_populated, test_lt_property,
                               description="Get list tail: d.lt [odict/codict only]")

    # ========================================================================
    # Summary Statistics
    # ========================================================================
    print("\n" + "=" * 110)
    print("BENCHMARK SUMMARY")
    print("=" * 110)

    # Calculate overall statistics
    if HAS_CODICT and runner.results:
        codict_wins = 0
        codict_losses = 0
        codict_speedups = []

        for method_name, results in runner.results.items():
            for size in SIZES:
                odict_data = results.get(('odict', size))
                codict_data = results.get(('codict', size))

                if odict_data and codict_data:
                    odict_time = odict_data['time_ms']
                    codict_time = codict_data['time_ms']

                    if odict_time > 0:
                        speedup = (odict_time - codict_time) / odict_time * 100
                        codict_speedups.append(speedup)

                        if codict_time < odict_time:
                            codict_wins += 1
                        else:
                            codict_losses += 1

        if codict_speedups:
            avg_speedup = sum(codict_speedups) / len(codict_speedups)
            print(f"\nCodict vs Odict Performance:")
            print(f"  Methods tested: {len(codict_speedups)}")
            print(f"  Codict faster: {codict_wins} times")
            print(f"  Codict slower: {codict_losses} times")
            print(f"  Average speedup: {avg_speedup:+.1f}%")
            print(f"  Best speedup: {max(codict_speedups):+.1f}%")
            print(f"  Worst speedup: {min(codict_speedups):+.1f}%")

    print("\n" + "=" * 110)
    print("BENCHMARK COMPLETE")
    print("=" * 110)
    print("\nTo run individual benchmarks, import this module and use BenchmarkRunner directly.")
    print("For detailed analysis, see PERFORMANCE_ANALYSIS.md")


if __name__ == '__main__':
    run()
