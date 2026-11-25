"""Illustrative monthly pilot economics; not financial or pricing advice."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Scenario:
    monthly_tasks: int
    adoption: float
    minutes_before: float
    minutes_after: float  # Includes review and correction time.
    hourly_cost: float
    cash_realization: float
    cost_per_adopted_task: float
    monthly_fixed_cost: float


def calculate(s: Scenario) -> dict:
    if s.monthly_tasks < 0 or not 0 <= s.adoption <= 1 or not 0 <= s.cash_realization <= 1:
        raise ValueError("invalid volume, adoption or cash realization")
    if any(value < 0 for value in (s.minutes_before, s.minutes_after, s.hourly_cost,
                                   s.cost_per_adopted_task, s.monthly_fixed_cost)):
        raise ValueError("cost and time inputs cannot be negative")
    adopted = s.monthly_tasks * s.adoption
    hours_saved = adopted * (s.minutes_before - s.minutes_after) / 60
    time_value = hours_saved * s.hourly_cost
    incremental_cost = s.monthly_fixed_cost + adopted * s.cost_per_adopted_task
    return {"adopted_tasks": adopted, "hours_saved": hours_saved,
            "time_value": time_value, "incremental_cost": incremental_cost,
            "estimated_cash_impact": time_value * s.cash_realization - incremental_cost}


if __name__ == "__main__":
    base = dict(monthly_tasks=1000, minutes_before=8, minutes_after=5,
                hourly_cost=60, cash_realization=.25, cost_per_adopted_task=.10,
                monthly_fixed_cost=800)
    for name, adoption in [("保守", .25), ("基准", .5), ("乐观", .8)]:
        result = calculate(Scenario(adoption=adoption, **base))
        print(f"{name}: 任务 {result['adopted_tasks']:.0f}, 节约 {result['hours_saved']:.1f} 小时, "
              f"时间价值 {result['time_value']:.0f} 元, 现金影响 {result['estimated_cash_impact']:.0f} 元")
