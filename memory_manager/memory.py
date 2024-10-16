import time
from typing import List, Optional, Tuple
import random

class MemoryBlock:
    def __init__(self, start: int, size: int, is_free: bool = True, process_id: Optional[int] = None):
        self.start = start
        self.size = size
        self.is_free = is_free
        self.process_id = process_id

class MemoryManager:
    def __init__(self, total_size: int):
        self.total_size = total_size
        self.blocks: List[MemoryBlock] = [MemoryBlock(0, total_size)]
        self.algorithm = "First Fit"
        self.failed_allocations = 0
        self.total_allocations = 0
        self.allocation_history = []
        self.compaction_count = 0

    def allocate(self, size: int, process_id: int) -> Optional[int]:
        start_time = time.time()
        self.total_allocations += 1
        allocation_func = getattr(self, f"_{self.algorithm.lower().replace(' ', '_')}")
        result = allocation_func(size, process_id)
        end_time = time.time()
        if result is None:
            self.failed_allocations += 1
        else:
            self.allocation_history.append((process_id, size, start_time, end_time - start_time))
        return result

    def _first_fit(self, size: int, process_id: int) -> Optional[int]:
        for i, block in enumerate(self.blocks):
            if block.is_free and block.size >= size:
                return self._split_block(i, size, process_id)
        return None

    def _best_fit(self, size: int, process_id: int) -> Optional[int]:
        best_fit = min((block for block in self.blocks if block.is_free and block.size >= size), 
                       key=lambda b: b.size, default=None)
        if best_fit:
            return self._split_block(self.blocks.index(best_fit), size, process_id)
        return None

    def _worst_fit(self, size: int, process_id: int) -> Optional[int]:
        worst_fit = max((block for block in self.blocks if block.is_free and block.size >= size), 
                        key=lambda b: b.size, default=None)
        if worst_fit:
            return self._split_block(self.blocks.index(worst_fit), size, process_id)
        return None

    def _next_fit(self, size: int, process_id: int) -> Optional[int]:
        start_index = getattr(self, '_last_allocation_index', 0)
        for i in range(len(self.blocks)):
            index = (start_index + i) % len(self.blocks)
            if self.blocks[index].is_free and self.blocks[index].size >= size:
                self._last_allocation_index = index
                return self._split_block(index, size, process_id)
        return None
    
    def get_blocks(self) -> List[MemoryBlock]:
        return self.blocks

    def _split_block(self, index: int, size: int, process_id: int) -> int:
        block = self.blocks[index]
        if block.size > size:
            new_block = MemoryBlock(block.start + size, block.size - size)
            self.blocks.insert(index + 1, new_block)
            block.size = size
        block.is_free = False
        block.process_id = process_id
        return block.start

    def deallocate(self, start: int) -> bool:
        for i, block in enumerate(self.blocks):
            if block.start == start and not block.is_free:
                block.is_free = True
                block.process_id = None
                self._merge_free_blocks()
                return True
        return False

    def _merge_free_blocks(self) -> None:
        i = 0
        while i < len(self.blocks) - 1:
            if self.blocks[i].is_free and self.blocks[i+1].is_free:
                self.blocks[i].size += self.blocks[i+1].size
                self.blocks.pop(i+1)
            else:
                i += 1

    def compact_memory(self) -> None:
        allocated_blocks = [b for b in self.blocks if not b.is_free]
        free_space = sum(b.size for b in self.blocks if b.is_free)
        
        allocated_blocks.sort(key=lambda b: b.start)
        
        current_position = 0
        for block in allocated_blocks:
            block.start = current_position
            current_position += block.size
        
        if free_space > 0:
            allocated_blocks.append(MemoryBlock(current_position, free_space, is_free=True))
        
        self.blocks = allocated_blocks
        self.compaction_count += 1

    def get_fragmentation_ratio(self) -> float:
        free_blocks = [b for b in self.blocks if b.is_free]
        if not free_blocks:
            return 0
        return (len(free_blocks) - 1) / len(free_blocks)

    def get_allocation_success_rate(self) -> float:
        if self.total_allocations == 0:
            return 1.0
        return (self.total_allocations - self.failed_allocations) / self.total_allocations

    def get_average_allocation_time(self) -> float:
        if not self.allocation_history:
            return 0
        return sum(alloc[3] for alloc in self.allocation_history) / len(self.allocation_history)

    def simulate_allocations(self, num_allocations: int, min_size: int, max_size: int) -> None:
        for _ in range(num_allocations):
            size = random.randint(min_size, max_size)
            process_id = random.randint(1, 1000)
            self.allocate(size, process_id)

    def get_memory_state(self) -> List[Tuple[int, int, bool, Optional[int]]]:
        return [(b.start, b.size, b.is_free, b.process_id) for b in self.blocks]

    def set_memory_state(self, state: List[Tuple[int, int, bool, Optional[int]]]) -> None:
        self.blocks = [MemoryBlock(start, size, is_free, process_id) for start, size, is_free, process_id in state]

    def set_algorithm(self, algorithm: str) -> None:
        if algorithm in ["First Fit", "Best Fit", "Worst Fit", "Next Fit"]:
            self.algorithm = algorithm