import gc
from collections import Counter
import numpy as np
import random

# --- Dummy classes for illustration ---
class BigArrayA:
    def __init__(self):
        self.data = np.random.rand(random.randint(100_000, 1_000_000))

class BigArrayB:
    def __init__(self):
        self.data = np.random.rand(random.randint(50_000, 500_000))

# Create some objects scattered around (not in a single list)
my_arrays = []
for _ in range(30):
    if random.random() < 0.5:
        my_arrays.append(BigArrayA())
    else:
        my_arrays.append(BigArrayB())

# Force garbage collection to get a clean snapshot
gc.collect()
import sys
# --- Inspect all live objects ---
all_objects = gc.get_objects()  # list of all currently alive objects
def get_object_size(obj):
    """Return approximate memory size of object in bytes."""
    # For numpy arrays, count the actual data buffer
    if isinstance(obj, np.ndarray):
        return obj.nbytes
    # For other objects, use sys.getsizeof
    try:
        return sys.getsizeof(obj)
    except TypeError:
        return 0

# Sort all objects by size, descending
objects_sorted_by_size = sorted(all_objects, key=get_object_size, reverse=True)

# Print top 10 largest objects
print("Top 10 largest objects currently alive in memory:")
for i, obj in enumerate(objects_sorted_by_size[:30], 1):
    size = get_object_size(obj)
    print(f"{i}. Type: {type(obj)}, Size: {size / 1e6:.2f} MB")

print(sum([my_array.data.sum() for my_array in my_arrays]))