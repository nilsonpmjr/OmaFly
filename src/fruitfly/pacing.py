"""Operational CPU budget; never chooses an animal behaviour."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Budget:
    active_period: float = .04
    resting_period: float = .10
    worker_cpu_fraction: float = .02

    def deadline(self,started,finished,cpu_seconds,moving):
        period=self.active_period if moving else self.resting_period
        # Reserve idle time even on a slow device. A late frame never causes a catch-up loop.
        rest=max(.002,cpu_seconds*(1/self.worker_cpu_fraction-1))
        return max(started+period,finished+rest)
