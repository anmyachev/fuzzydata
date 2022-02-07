import time
from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic, Dict

from fuzzydata.core.artifact import Artifact

T = TypeVar('T')


class Operation(Generic[T], ABC):

    def __init__(self, sources: List[Artifact], new_label: str, op: str, args: Dict):
        self.sources = sources
        self.new_label = new_label
        self.dest_schema_map = None
        self.op = getattr(self, op)
        self.args = args

        # Operation Timings
        self.start_time = None
        self.end_time = None

    @abstractmethod
    def sample(self, frac: float) -> T:
        self.dest_schema_map = self.sources[0].schema_map
        pass

    @abstractmethod
    def groupby(self, group_columns: List[str], agg_columns: List[str], agg_function: str) -> T:
        output_cols = group_columns+agg_columns
        self.dest_schema_map = dict(filter(lambda x: x[0] in output_cols, self.sources[0].schema_map.items()))
        pass

    @abstractmethod
    def project(self, output_cols: List[str]) -> T:
        self.dest_schema_map = dict(filter(lambda x: x[0] in output_cols, self.sources[0].schema_map.items()))
        pass

    @abstractmethod
    def select(self, condition: str) -> T:
        self.dest_schema_map = self.sources[0].schema_map
        pass

    @abstractmethod
    def merge(self, key_col: List[str]) -> T:
        self.dest_schema_map = {**self.sources[0].schema_map, **self.sources[1].schema_map}
        pass

    @abstractmethod
    def pivot(self, index_cols: List[str], columns: List[str], value_col: List[str], agg_func: str) -> T:
        # Destination Schema Map should be generated by operation!
        pass

    def execute(self) -> None:
        self.start_time = time.perf_counter()
        result = self.op(**self.args)
        self.end_time = time.perf_counter()
        return result

    def get_execution_time(self):
        return self.end_time - self.start_time

    def to_dict(self) -> dict:
        return {
            'sources': [s.label for s in self.sources],
            'new_label': self.new_label,
            'op': self.op.__name__,
            'args': self.args
        }
