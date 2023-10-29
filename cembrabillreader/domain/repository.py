from abc import ABC, abstractmethod

from cembrabillreader.domain.entities import CembraBill


class CembraBillRepository(ABC):
    @abstractmethod
    def load_cembra_bill(
        self, path_to_bill: str, expected_holders: list[str]
    ) -> CembraBill:
        raise NotImplementedError()
