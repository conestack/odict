# Python Software Foundation License
"""
Comprehensive benchmark suite for odict implementation.

Compares performance and memory usage of all public API methods across:
- dict (Python built-in)
- OrderedDict (collections.OrderedDict)
- odict (Python implementation from this package)
"""

import argparse
import gc
import sys
import time
import tracemalloc
from collections import OrderedDict

from .odict import odict


# Default Configuration
DEFAULT_SIZES = [1000, 10000, 100000, 1000000]
DEFAULT_MICRO_ITERATIONS = 10000  # For fast operations
DEFAULT_MACRO_ITERATIONS = 1000  # For slow operations
DEFAULT_WARMUP_ITERATIONS = 100


class BenchmarkRunner:
    """Main benchmark runner for all odict methods."""

    def __init__(self, config=None):
        """Initialize benchmark runner with available implementations.

        Args:
            config: Configuration dict with keys:
                - sizes: List of data sizes to test
                - micro_iterations: Number of iterations for fast operations
                - macro_iterations: Number of iterations for slow operations
                - warmup_iterations: Number of warmup iterations
                - baseline: Baseline implementation name ('fastest', 'dict', 'odict', etc.)
                - implementations: List of implementation names to test (or None for all)
        """
        if config is None:
            config = {}

        self.sizes = config.get('sizes', DEFAULT_SIZES)
        self.micro_iterations = config.get('micro_iterations', DEFAULT_MICRO_ITERATIONS)
        self.macro_iterations = config.get('macro_iterations', DEFAULT_MACRO_ITERATIONS)
        self.warmup_iterations = config.get(
            'warmup_iterations', DEFAULT_WARMUP_ITERATIONS
        )
        self.baseline = config.get('baseline', 'fastest')

        # All available implementations
        all_impls = {
            'dict': dict,
            'OrderedDict': OrderedDict,
            'odict': odict,
        }

        # Filter implementations if requested
        requested_impls = config.get('implementations')
        if requested_impls:
            self.implementations = {
                name: cls for name, cls in all_impls.items() if name in requested_impls
            }
        else:
            self.implementations = all_impls

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
            return hasattr(impl_class, method_name) or hasattr(
                impl_class(), method_name
            )

    def benchmark_method(self, method_name, setup_fn, test_fn, iterations=None):
        """
        Benchmark a specific method across all implementations and sizes.

        Args:
            method_name: Name of the method being tested
            setup_fn: Function(impl_class, size) -> test object
            test_fn: Function(obj, size, iterations) -> None
            iterations: Number of times to run the operation (None = use micro_iterations)

        Returns:
            dict: Results keyed by (impl_name, size)
        """
        if iterations is None:
            iterations = self.micro_iterations

        results = {}

        for size in self.sizes:
            for impl_name, impl_class in self.implementations.items():
                # Skip if method not available
                if not self.has_method(impl_class, method_name):
                    continue

                try:
                    # Setup test object
                    test_obj = setup_fn(impl_class, size)

                    # Warmup
                    warmup_obj = setup_fn(impl_class, min(size, 100))
                    test_fn(warmup_obj, min(size, 100), self.warmup_iterations)
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
                        'iterations': iterations,
                    }

                    # Cleanup
                    del test_obj
                    gc.collect()

                except Exception as e:
                    # If benchmark fails, just skip this combination
                    print(
                        f'  [Skipped {impl_name} at size {size}: {e}]', file=sys.stderr
                    )
                    continue

        return results

    def print_table(self, method_name, results, description=''):
        """
        Print formatted results table for a method.

        Args:
            method_name: Name of the method
            results: Results dict from benchmark_method
            description: Optional description of what's being measured
        """
        print(f'\n{"=" * 110}')
        print(f'Method: {method_name}')
        if description:
            print(f'Description: {description}')
        print(f'{"=" * 110}')

        for size in self.sizes:
            # Check if we have any results for this size
            has_results = any(
                (impl, size) in results for impl in self.implementations.keys()
            )
            if not has_results:
                continue

            print(f'\n--- Size: {size:,} objects ---')

            # Determine baseline implementation for this size
            baseline_impl = None
            baseline_time = None
            baseline_mem = None

            if self.baseline == 'fastest':
                # Find fastest implementation
                min_time = float('inf')
                for impl in self.implementations.keys():
                    if (impl, size) in results:
                        impl_time = results[(impl, size)]['time_ms']
                        if impl_time < min_time:
                            min_time = impl_time
                            baseline_impl = impl
                            baseline_time = impl_time
                            baseline_mem = results[(impl, size)]['memory_kb']
            elif self.baseline == 'none':
                # No baseline comparison
                baseline_impl = None
            elif self.baseline in self.implementations:
                # Use specified baseline if available
                baseline_impl = self.baseline
                if (baseline_impl, size) in results:
                    baseline_time = results[(baseline_impl, size)]['time_ms']
                    baseline_mem = results[(baseline_impl, size)]['memory_kb']
                else:
                    baseline_impl = None

            # Print header
            if baseline_impl:
                time_vs_header = f'vs {baseline_impl}'
                mem_vs_header = f'vs {baseline_impl}'
                print(
                    f'{"Implementation":<15} | {"Time (ms)":<12} | {time_vs_header:<12} | {"Memory (KB)":<12} | {mem_vs_header:<12}'
                )
            else:
                print(
                    f'{"Implementation":<15} | {"Time (ms)":<12} | {"Relative":<12} | {"Memory (KB)":<12} | {"Relative":<12}'
                )
            print('-' * 110)

            # Print results for each implementation
            impl_order = ['dict', 'OrderedDict', 'odict']
            # Filter to only implementations we're testing and that exist
            impl_order = [i for i in impl_order if i in self.implementations]

            for impl in impl_order:
                if (impl, size) not in results:
                    print(
                        f'{impl:<15} | {"N/A":<12} | {"-":<12} | {"N/A":<12} | {"-":<12}'
                    )
                    continue

                data = results[(impl, size)]
                time_ms = data['time_ms']
                mem_kb = data['memory_kb']

                # Calculate percentages vs baseline
                if (
                    baseline_impl
                    and baseline_time
                    and impl != baseline_impl
                    and baseline_time > 0
                ):
                    time_pct = ((time_ms - baseline_time) / baseline_time) * 100
                    time_vs = f'{time_pct:+7.1f}%'
                else:
                    time_vs = '-' if baseline_impl else 'baseline'

                if (
                    baseline_impl
                    and baseline_mem
                    and impl != baseline_impl
                    and abs(baseline_mem) > 0.001
                ):
                    mem_pct = ((mem_kb - baseline_mem) / abs(baseline_mem)) * 100
                    mem_vs = f'{mem_pct:+7.1f}%'
                else:
                    mem_vs = '-' if baseline_impl else 'baseline'

                # Mark baseline implementation
                impl_label = impl
                if impl == baseline_impl:
                    impl_label = f'{impl} ★'

                print(
                    f'{impl_label:<15} | {time_ms:>10.3f}ms | {time_vs:<12} | {mem_kb:>10.3f}KB | {mem_vs:<12}'
                )

    def benchmark_and_print(
        self,
        method_name,
        setup_fn,
        test_fn,
        iterations=None,
        description='',
    ):
        """Convenience method to benchmark and immediately print results."""
        print(f'\n[Benchmarking {method_name}...]')
        results = self.benchmark_method(method_name, setup_fn, test_fn, iterations)
        self.results[method_name] = results
        self.print_table(method_name, results, description)


# ============================================================================
# Setup Functions
# ============================================================================


def setup_populated(impl_class, size):
    """Create a populated dict/odict with 'size' items."""
    return impl_class([(str(i), i * 2) for i in range(size)])


def setup_empty(impl_class, size):
    """Create an empty dict/odict."""
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
    """Test has_key(key) - odict only"""
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
    """Test iterkeys() - odict only"""
    for _ in range(iterations):
        for key in obj.iterkeys():
            pass


def test_itervalues(obj, size, iterations):
    """Test itervalues() - odict only"""
    for _ in range(iterations):
        for value in obj.itervalues():
            pass


def test_iteritems(obj, size, iterations):
    """Test iteritems() - odict only"""
    for _ in range(iterations):
        for key, value in obj.iteritems():
            pass


def test_riterkeys(obj, size, iterations):
    """Test riterkeys() - odict only"""
    for _ in range(iterations):
        for key in obj.riterkeys():
            pass


def test_ritervalues(obj, size, iterations):
    """Test ritervalues() - odict only"""
    for _ in range(iterations):
        for value in obj.ritervalues():
            pass


def test_riteritems(obj, size, iterations):
    """Test riteritems() - odict only"""
    for _ in range(iterations):
        for key, value in obj.riteritems():
            pass


def test_rkeys(obj, size, iterations):
    """Test rkeys() - odict only"""
    for _ in range(iterations):
        _ = obj.rkeys()


def test_rvalues(obj, size, iterations):
    """Test rvalues() - odict only"""
    for _ in range(iterations):
        _ = obj.rvalues()


def test_ritems(obj, size, iterations):
    """Test ritems() - odict only"""
    for _ in range(iterations):
        _ = obj.ritems()


# ============================================================================
# Test Functions: Ordered Dict Specific Operations
# ============================================================================


def test_firstkey(obj, size, iterations):
    """Test firstkey() - odict only"""
    for _ in range(iterations):
        _ = obj.firstkey()


def test_lastkey(obj, size, iterations):
    """Test lastkey() - odict only"""
    for _ in range(iterations):
        _ = obj.lastkey()


def test_first_key_property(obj, size, iterations):
    """Test first_key property - odict only"""
    for _ in range(iterations):
        _ = obj.first_key


def test_last_key_property(obj, size, iterations):
    """Test last_key property - odict only"""
    for _ in range(iterations):
        _ = obj.last_key


def test_next_key(obj, size, iterations):
    """Test next_key(key) - odict only"""
    key = str(size // 2) if size > 0 else '0'
    for _ in range(iterations):
        try:
            _ = obj.next_key(key)
        except (KeyError, StopIteration):
            pass


def test_prev_key(obj, size, iterations):
    """Test prev_key(key) - odict only"""
    key = str(size // 2) if size > 0 else '0'
    for _ in range(iterations):
        try:
            _ = obj.prev_key(key)
        except (KeyError, StopIteration):
            pass


def test_sort(obj, size, iterations):
    """Test sort() - odict only"""
    impl_class = type(obj)
    for _ in range(iterations):
        test_obj = impl_class([(str(i), i) for i in range(min(size, 100))])
        test_obj.sort()


def test_alter_key(obj, size, iterations):
    """Test alter_key(old, new) - odict only"""
    impl_class = type(obj)
    for _ in range(iterations):
        test_obj = impl_class([(str(i), i) for i in range(min(size, 100))])
        if len(test_obj) > 0:
            test_obj.alter_key('0', 'renamed_0')


def test_swap(obj, size, iterations):
    """Test swap(a, b) - odict only"""
    impl_class = type(obj)
    for _ in range(iterations):
        test_obj = impl_class([(str(i), i) for i in range(min(size, 100))])
        if len(test_obj) > 1:
            test_obj.swap('0', '1')


def test_insertbefore(obj, size, iterations):
    """Test insertbefore(ref, key, value) - odict only"""
    impl_class = type(obj)
    for _ in range(iterations):
        test_obj = impl_class([(str(i), i) for i in range(min(size, 100))])
        if len(test_obj) > 0:
            test_obj.insertbefore('0', 'new', 999)


def test_insertafter(obj, size, iterations):
    """Test insertafter(ref, key, value) - odict only"""
    impl_class = type(obj)
    for _ in range(iterations):
        test_obj = impl_class([(str(i), i) for i in range(min(size, 100))])
        if len(test_obj) > 0:
            test_obj.insertafter('0', 'new', 999)


def test_insertfirst(obj, size, iterations):
    """Test insertfirst(key, value) - odict only"""
    impl_class = type(obj)
    for _ in range(iterations):
        test_obj = impl_class([(str(i), i) for i in range(min(size, 100))])
        test_obj.insertfirst('new', 999)


def test_insertlast(obj, size, iterations):
    """Test insertlast(key, value) - odict only"""
    impl_class = type(obj)
    for _ in range(iterations):
        test_obj = impl_class([(str(i), i) for i in range(min(size, 100))])
        test_obj.insertlast('new', 999)


def test_movebefore(obj, size, iterations):
    """Test movebefore(ref, key) - odict only"""
    impl_class = type(obj)
    for _ in range(iterations):
        test_obj = impl_class([(str(i), i) for i in range(min(size, 100))])
        if len(test_obj) > 1:
            test_obj.movebefore('0', '1')


def test_moveafter(obj, size, iterations):
    """Test moveafter(ref, key) - odict only"""
    impl_class = type(obj)
    for _ in range(iterations):
        test_obj = impl_class([(str(i), i) for i in range(min(size, 100))])
        if len(test_obj) > 1:
            test_obj.moveafter('0', '1')


def test_movefirst(obj, size, iterations):
    """Test movefirst(key) - odict only"""
    impl_class = type(obj)
    for _ in range(iterations):
        test_obj = impl_class([(str(i), i) for i in range(min(size, 100))])
        if len(test_obj) > 0:
            test_obj.movefirst(str(len(test_obj) - 1))


def test_movelast(obj, size, iterations):
    """Test movelast(key) - odict only"""
    impl_class = type(obj)
    for _ in range(iterations):
        test_obj = impl_class([(str(i), i) for i in range(min(size, 100))])
        if len(test_obj) > 0:
            test_obj.movelast('0')


def test_as_dict(obj, size, iterations):
    """Test as_dict() - odict only"""
    for _ in range(iterations):
        _ = obj.as_dict()


def test_lh_property(obj, size, iterations):
    """Test lh property (list head) - odict only"""
    for _ in range(iterations):
        _ = obj.lh


def test_lt_property(obj, size, iterations):
    """Test lt property (list tail) - odict only"""
    for _ in range(iterations):
        _ = obj.lt


# ============================================================================
# Main Runner
# ============================================================================


def run_comprehensive(config=None):
    """Run comprehensive benchmark suite.

    Args:
        config: Configuration dict (or None for defaults)
    """
    runner = BenchmarkRunner(config)

    print('\n' + '=' * 110)
    print('ODICT COMPREHENSIVE BENCHMARK SUITE')
    print('=' * 110)
    print(f'\nComparing implementations: {", ".join(runner.implementations.keys())}')
    print(f'Test sizes: {", ".join(str(s) for s in runner.sizes)}')
    print(f'Micro-benchmark iterations: {runner.micro_iterations:,}')
    print(f'Macro-benchmark iterations: {runner.macro_iterations:,}')
    print(f'Baseline: {runner.baseline}')
    baseline_note = 'fastest' if runner.baseline == 'fastest' else f'{runner.baseline}'
    print(f'\nNote: Comparisons are relative to {baseline_note}')
    print("      'N/A' means method not available on that implementation")
    print("      '★' marks the baseline implementation")

    # ========================================================================
    # CATEGORY 1: Basic Dictionary Operations
    # ========================================================================
    print('\n' + '=' * 110)
    print('CATEGORY 1: BASIC DICTIONARY OPERATIONS')
    print('=' * 110)

    runner.benchmark_and_print(
        '__getitem__',
        setup_populated,
        test_getitem,
        description="Access item by key: d['key']",
    )

    runner.benchmark_and_print(
        '__setitem__',
        setup_populated,
        test_setitem,
        description="Set item by key: d['key'] = value",
    )

    runner.benchmark_and_print(
        '__delitem__',
        setup_populated,
        test_delitem,
        iterations=runner.macro_iterations,
        description="Delete item by key: del d['key']",
    )

    runner.benchmark_and_print(
        '__contains__',
        setup_populated,
        test_contains,
        description="Check if key exists: 'key' in d",
    )

    runner.benchmark_and_print(
        '__len__',
        setup_populated,
        test_len,
        description='Get dictionary length: len(d)',
    )

    runner.benchmark_and_print(
        'get',
        setup_populated,
        test_get,
        description='Get with default: d.get(key, default)',
    )

    runner.benchmark_and_print(
        'has_key',
        setup_populated,
        test_has_key,
        description='Check if key exists: d.has_key(key) [odict only]',
    )

    runner.benchmark_and_print(
        'keys',
        setup_populated,
        test_keys,
        iterations=runner.macro_iterations,
        description='Get list of keys: d.keys()',
    )

    runner.benchmark_and_print(
        'values',
        setup_populated,
        test_values,
        iterations=runner.macro_iterations,
        description='Get list of values: d.values()',
    )

    runner.benchmark_and_print(
        'items',
        setup_populated,
        test_items,
        iterations=runner.macro_iterations,
        description='Get list of items: d.items()',
    )

    runner.benchmark_and_print(
        'clear',
        setup_populated,
        test_clear,
        iterations=runner.macro_iterations,
        description='Remove all items: d.clear()',
    )

    runner.benchmark_and_print(
        'copy',
        setup_populated,
        test_copy,
        iterations=runner.macro_iterations,
        description='Create shallow copy: d.copy()',
    )

    runner.benchmark_and_print(
        'update',
        setup_populated,
        test_update,
        iterations=runner.macro_iterations,
        description='Update with dict: d.update(other)',
    )

    runner.benchmark_and_print(
        'setdefault',
        setup_populated,
        test_setdefault,
        description='Set if not exists: d.setdefault(key, default)',
    )

    runner.benchmark_and_print(
        'pop',
        setup_populated,
        test_pop,
        iterations=runner.macro_iterations,
        description='Pop key with default: d.pop(key, default)',
    )

    runner.benchmark_and_print(
        'popitem',
        setup_populated,
        test_popitem,
        iterations=runner.macro_iterations,
        description='Pop last item: d.popitem()',
    )

    runner.benchmark_and_print(
        'fromkeys',
        setup_empty,
        test_fromkeys,
        iterations=runner.macro_iterations,
        description='Create from keys: dict.fromkeys(keys, value)',
    )

    # ========================================================================
    # CATEGORY 2: Iteration Operations
    # ========================================================================
    print('\n' + '=' * 110)
    print('CATEGORY 2: ITERATION OPERATIONS')
    print('=' * 110)

    runner.benchmark_and_print(
        '__iter__',
        setup_populated,
        test_iter,
        iterations=runner.macro_iterations,
        description='Forward iteration: for key in d',
    )

    runner.benchmark_and_print(
        '__reversed__',
        setup_populated,
        test_reversed,
        iterations=runner.macro_iterations,
        description='Reverse iteration: for key in reversed(d)',
    )

    runner.benchmark_and_print(
        'iterkeys',
        setup_populated,
        test_iterkeys,
        iterations=runner.macro_iterations,
        description='Iterate keys: for key in d.iterkeys() [odict only]',
    )

    runner.benchmark_and_print(
        'itervalues',
        setup_populated,
        test_itervalues,
        iterations=runner.macro_iterations,
        description='Iterate values: for val in d.itervalues() [odict only]',
    )

    runner.benchmark_and_print(
        'iteritems',
        setup_populated,
        test_iteritems,
        iterations=runner.macro_iterations,
        description='Iterate items: for k,v in d.iteritems() [odict only]',
    )

    runner.benchmark_and_print(
        'riterkeys',
        setup_populated,
        test_riterkeys,
        iterations=runner.macro_iterations,
        description='Reverse iterate keys: d.riterkeys() [odict only]',
    )

    runner.benchmark_and_print(
        'ritervalues',
        setup_populated,
        test_ritervalues,
        iterations=runner.macro_iterations,
        description='Reverse iterate values: d.ritervalues() [odict only]',
    )

    runner.benchmark_and_print(
        'riteritems',
        setup_populated,
        test_riteritems,
        iterations=runner.macro_iterations,
        description='Reverse iterate items: d.riteritems() [odict only]',
    )

    runner.benchmark_and_print(
        'rkeys',
        setup_populated,
        test_rkeys,
        iterations=runner.macro_iterations,
        description='Get reverse keys list: d.rkeys() [odict only]',
    )

    runner.benchmark_and_print(
        'rvalues',
        setup_populated,
        test_rvalues,
        iterations=runner.macro_iterations,
        description='Get reverse values list: d.rvalues() [odict only]',
    )

    runner.benchmark_and_print(
        'ritems',
        setup_populated,
        test_ritems,
        iterations=runner.macro_iterations,
        description='Get reverse items list: d.ritems() [odict only]',
    )

    # ========================================================================
    # CATEGORY 3: Ordered Dict Specific Operations
    # ========================================================================
    print('\n' + '=' * 110)
    print('CATEGORY 3: ORDERED DICT SPECIFIC OPERATIONS')
    print('=' * 110)

    runner.benchmark_and_print(
        'firstkey',
        setup_populated,
        test_firstkey,
        description='Get first key: d.firstkey() [odict only]',
    )

    runner.benchmark_and_print(
        'lastkey',
        setup_populated,
        test_lastkey,
        description='Get last key: d.lastkey() [odict only]',
    )

    runner.benchmark_and_print(
        'first_key',
        setup_populated,
        test_first_key_property,
        description='Get first key property: d.first_key [odict only]',
    )

    runner.benchmark_and_print(
        'last_key',
        setup_populated,
        test_last_key_property,
        description='Get last key property: d.last_key [odict only]',
    )

    runner.benchmark_and_print(
        'next_key',
        setup_populated,
        test_next_key,
        description='Get next key: d.next_key(key) [odict only]',
    )

    runner.benchmark_and_print(
        'prev_key',
        setup_populated,
        test_prev_key,
        description='Get previous key: d.prev_key(key) [odict only]',
    )

    runner.benchmark_and_print(
        'sort',
        setup_populated,
        test_sort,
        iterations=runner.macro_iterations,
        description='Sort by keys: d.sort() [odict only]',
    )

    runner.benchmark_and_print(
        'alter_key',
        setup_populated,
        test_alter_key,
        iterations=runner.macro_iterations,
        description='Rename key: d.alter_key(old, new) [odict only]',
    )

    runner.benchmark_and_print(
        'swap',
        setup_populated,
        test_swap,
        iterations=runner.macro_iterations,
        description='Swap two keys: d.swap(a, b) [odict only]',
    )

    runner.benchmark_and_print(
        'insertbefore',
        setup_populated,
        test_insertbefore,
        iterations=runner.macro_iterations,
        description='Insert before key: d.insertbefore(ref, key, val) [odict only]',
    )

    runner.benchmark_and_print(
        'insertafter',
        setup_populated,
        test_insertafter,
        iterations=runner.macro_iterations,
        description='Insert after key: d.insertafter(ref, key, val) [odict only]',
    )

    runner.benchmark_and_print(
        'insertfirst',
        setup_populated,
        test_insertfirst,
        iterations=runner.macro_iterations,
        description='Insert at start: d.insertfirst(key, val) [odict only]',
    )

    runner.benchmark_and_print(
        'insertlast',
        setup_populated,
        test_insertlast,
        iterations=runner.macro_iterations,
        description='Insert at end: d.insertlast(key, val) [odict only]',
    )

    runner.benchmark_and_print(
        'movebefore',
        setup_populated,
        test_movebefore,
        iterations=runner.macro_iterations,
        description='Move key before ref: d.movebefore(ref, key) [odict only]',
    )

    runner.benchmark_and_print(
        'moveafter',
        setup_populated,
        test_moveafter,
        iterations=runner.macro_iterations,
        description='Move key after ref: d.moveafter(ref, key) [odict only]',
    )

    runner.benchmark_and_print(
        'movefirst',
        setup_populated,
        test_movefirst,
        iterations=runner.macro_iterations,
        description='Move key to start: d.movefirst(key) [odict only]',
    )

    runner.benchmark_and_print(
        'movelast',
        setup_populated,
        test_movelast,
        iterations=runner.macro_iterations,
        description='Move key to end: d.movelast(key) [odict only]',
    )

    runner.benchmark_and_print(
        'as_dict',
        setup_populated,
        test_as_dict,
        iterations=runner.macro_iterations,
        description='Convert to dict: d.as_dict() [odict only]',
    )

    runner.benchmark_and_print(
        'lh',
        setup_populated,
        test_lh_property,
        description='Get list head: d.lh [odict only]',
    )

    runner.benchmark_and_print(
        'lt',
        setup_populated,
        test_lt_property,
        description='Get list tail: d.lt [odict only]',
    )

    # ========================================================================
    # Summary Statistics
    # ========================================================================
    print('\n' + '=' * 110)
    print('BENCHMARK SUMMARY')
    print('=' * 110)

    # Calculate overall statistics for all implementations
    if runner.results and len(runner.implementations) > 1:
        impl_stats = {
            impl: {'wins': 0, 'total': 0, 'avg_time': []}
            for impl in runner.implementations
        }

        for method_name, results in runner.results.items():
            for size in runner.sizes:
                # Find fastest implementation for this method/size combo
                fastest_impl = None
                fastest_time = float('inf')
                available_impls = []

                for impl in runner.implementations:
                    if (impl, size) in results:
                        time_ms = results[(impl, size)]['time_ms']
                        available_impls.append((impl, time_ms))
                        if time_ms < fastest_time:
                            fastest_time = time_ms
                            fastest_impl = impl

                # Track wins and times
                for impl, time_ms in available_impls:
                    impl_stats[impl]['total'] += 1
                    impl_stats[impl]['avg_time'].append(time_ms)
                    if impl == fastest_impl:
                        impl_stats[impl]['wins'] += 1

        print('\nOverall Performance Summary:')
        print(
            f'{"Implementation":<15} | {"Wins":<8} | {"Win Rate":<10} | {"Avg Time":<12}'
        )
        print('-' * 60)

        for impl in ['dict', 'OrderedDict', 'odict']:
            if impl not in impl_stats or impl_stats[impl]['total'] == 0:
                continue
            stats = impl_stats[impl]
            win_rate = (
                (stats['wins'] / stats['total'] * 100) if stats['total'] > 0 else 0
            )
            avg_time = (
                sum(stats['avg_time']) / len(stats['avg_time'])
                if stats['avg_time']
                else 0
            )
            print(
                f'{impl:<15} | {stats["wins"]:<8} | {win_rate:>7.1f}% | {avg_time:>10.3f}ms'
            )

    print('\n' + '=' * 110)
    print('BENCHMARK COMPLETE')
    print('=' * 110)
    print(
        '\nTo run individual benchmarks, import this module and use BenchmarkRunner directly.'
    )


def run_micro(config=None):
    """Run micro-benchmarks with higher iteration counts for detailed performance analysis.

    Args:
        config: Configuration dict (or None for defaults)
    """
    if config is None:
        config = {}

    # Use higher iteration counts for micro-benchmarks
    if 'micro_iterations' not in config:
        config['micro_iterations'] = 100000
    if 'sizes' not in config:
        config['sizes'] = [1000]  # Single size for focused analysis

    runner = BenchmarkRunner(config)

    print('\n' + '=' * 110)
    print('ODICT MICRO-BENCHMARK SUITE')
    print('=' * 110)
    print(f'\nFocused on: {", ".join(runner.implementations.keys())}')
    print(f'Test size: {runner.sizes[0]:,} objects')
    print(f'Iterations: {runner.micro_iterations:,}')

    print('\n1. ITEM ACCESS OPERATIONS (most critical)')
    print('-' * 110)

    runner.benchmark_and_print(
        '__getitem__',
        setup_populated,
        test_getitem,
        description='Direct item access: d["key"]',
    )

    runner.benchmark_and_print(
        'get', setup_populated, test_get, description='Safe get: d.get("key")'
    )

    runner.benchmark_and_print(
        '__contains__',
        setup_populated,
        test_contains,
        description='Membership test: "key" in d',
    )

    runner.benchmark_and_print(
        'has_key', setup_populated, test_has_key, description='has_key() method'
    )

    print('\n2. MODIFICATION OPERATIONS')
    print('-' * 110)

    runner.benchmark_and_print(
        '__setitem__',
        setup_populated,
        test_setitem,
        description='Item assignment: d["key"] = value',
    )

    runner.benchmark_and_print(
        '__delitem__',
        setup_populated,
        test_delitem,
        iterations=runner.macro_iterations,
        description='Item deletion: del d["key"]',
    )

    print('\n3. COLLECTION OPERATIONS')
    print('-' * 110)

    runner.benchmark_and_print(
        '__len__', setup_populated, test_len, description='Length: len(d)'
    )

    runner.benchmark_and_print(
        'keys',
        setup_populated,
        test_keys,
        iterations=runner.macro_iterations,
        description='Get keys: d.keys()',
    )

    runner.benchmark_and_print(
        'values',
        setup_populated,
        test_values,
        iterations=runner.macro_iterations,
        description='Get values: d.values()',
    )

    runner.benchmark_and_print(
        'items',
        setup_populated,
        test_items,
        iterations=runner.macro_iterations,
        description='Get items: d.items()',
    )

    print('\n4. SPECIALIZED OPERATIONS')
    print('-' * 110)

    runner.benchmark_and_print(
        'firstkey',
        setup_populated,
        test_firstkey,
        description='Get first key: d.firstkey()',
    )

    runner.benchmark_and_print(
        'lastkey',
        setup_populated,
        test_lastkey,
        description='Get last key: d.lastkey()',
    )

    runner.benchmark_and_print(
        'first_key',
        setup_populated,
        test_first_key_property,
        description='First key property: d.first_key',
    )

    runner.benchmark_and_print(
        'last_key',
        setup_populated,
        test_last_key_property,
        description='Last key property: d.last_key',
    )

    print('\n5. NAVIGATION OPERATIONS')
    print('-' * 110)

    runner.benchmark_and_print(
        'next_key',
        setup_populated,
        test_next_key,
        iterations=runner.macro_iterations,
        description='Next key: d.next_key(key)',
    )

    runner.benchmark_and_print(
        'prev_key',
        setup_populated,
        test_prev_key,
        iterations=runner.macro_iterations,
        description='Previous key: d.prev_key(key)',
    )

    print('\n' + '=' * 110)
    print('MICRO-BENCHMARK COMPLETE')
    print('=' * 110)


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description='Benchmark suite for odict implementations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run comprehensive benchmarks with defaults
  python -m odict.bench

  # Run with custom sizes and iterations
  python -m odict.bench --sizes 1000,10000 --micro-iterations 50000

  # Compare specific implementations
  python -m odict.bench --implementations dict,odict

  # Use dict as baseline instead of fastest
  python -m odict.bench --baseline dict

  # Run micro-benchmarks with higher iteration counts
  python -m odict.bench --mode micro

  # Run micro-benchmarks for odict only
  python -m odict.bench --mode micro --implementations odict
        """,
    )

    parser.add_argument(
        '--mode',
        choices=['comprehensive', 'micro'],
        default='comprehensive',
        help='Benchmark mode: comprehensive (all methods) or micro (higher iteration counts)',
    )

    parser.add_argument(
        '--sizes',
        type=str,
        default=None,
        help=f'Comma-separated list of test sizes (default: {",".join(map(str, DEFAULT_SIZES))})',
    )

    parser.add_argument(
        '--micro-iterations',
        type=int,
        default=None,
        help=f'Number of iterations for fast operations (default: {DEFAULT_MICRO_ITERATIONS})',
    )

    parser.add_argument(
        '--macro-iterations',
        type=int,
        default=None,
        help=f'Number of iterations for slow operations (default: {DEFAULT_MACRO_ITERATIONS})',
    )

    parser.add_argument(
        '--warmup-iterations',
        type=int,
        default=None,
        help=f'Number of warmup iterations (default: {DEFAULT_WARMUP_ITERATIONS})',
    )

    parser.add_argument(
        '--baseline',
        choices=['fastest', 'dict', 'OrderedDict', 'odict', 'none'],
        default='fastest',
        help='Baseline for comparison: fastest (auto-select), specific impl, or none (no comparison)',
    )

    parser.add_argument(
        '--implementations',
        type=str,
        default=None,
        help='Comma-separated list of implementations to test (default: all available)',
    )

    args = parser.parse_args()

    # Build configuration from arguments
    config = {}

    if args.sizes:
        config['sizes'] = [int(s.strip()) for s in args.sizes.split(',')]

    if args.micro_iterations:
        config['micro_iterations'] = args.micro_iterations

    if args.macro_iterations:
        config['macro_iterations'] = args.macro_iterations

    if args.warmup_iterations:
        config['warmup_iterations'] = args.warmup_iterations

    config['baseline'] = args.baseline

    if args.implementations:
        config['implementations'] = [
            impl.strip() for impl in args.implementations.split(',')
        ]

    # Run appropriate benchmark mode
    if args.mode == 'micro':
        run_micro(config)
    else:
        run_comprehensive(config)


if __name__ == '__main__':
    main()
