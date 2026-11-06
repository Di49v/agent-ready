"""
Base class for adversarial AI buyer personas (Section A6 / B3.5).
Defines lifecycle hooks, event emission telemetry, and deterministic execution contracts.
"""
import abc
import logging
import time
from typing import Any, Callable, Dict, List, Literal, Optional
from pydantic import BaseModel, Field

from app.schemas.contracts import RunEvent
from app.services.swarm_engine import LaneResult

logger = logging.getLogger("agentready.personas")


class BasePersona(abc.ABC):
    """
    Abstract Base Class for an adversarial AI buyer persona test dummy.
    Each persona targets a specific Invariant Rule using either a deterministic
    scripted state machine or a live LLM interaction loop.
    """

    persona_id: str
    name: str
    lane: int
    rule_number: int
    rule_name: str
    attack_vector: str
    driven_by: Literal["fixed_script", "live_llm"] = "fixed_script"
    wave: int = 1

    def __init__(self) -> None:
        self.state_history: List[str] = []
        self._current_state: str = "INITIALIZED"

    @property
    def current_state(self) -> str:
        return self._current_state

    def set_state(self, state: str) -> None:
        """Transitions persona to a new state machine node."""
        self._current_state = state
        self.state_history.append(state)

    def _now(self) -> str:
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    async def emit_event(
        self,
        event_list: List[RunEvent],
        event_callback: Optional[Callable[[RunEvent], None]],
        run_id: str,
        event_type: str,
        actor: str,
        action: str,
        status: str,
        amount: Optional[str] = None,
        paypal_id: Optional[str] = None,
        rule_hit: Optional[int] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> RunEvent:
        """Helper to append and stream a typed RunEvent."""
        event = RunEvent(
            event=event_type,  # type: ignore
            run_id=run_id,
            timestamp=self._now(),
            lane=self.lane,
            persona_id=self.persona_id,
            actor=actor,
            action=action,
            status=status,
            amount=amount,
            paypal_id=paypal_id,
            rule_hit=rule_hit or self.rule_number,
            data=data or {},
        )
        event_list.append(event)
        if event_callback:
            try:
                event_callback(event)
            except Exception as e:
                logger.warning("Event callback failed in %s: %s", self.persona_id, e)
        return event

    @abc.abstractmethod
    async def execute(
        self,
        shop: Any,
        run_id: str,
        events: List[RunEvent],
        event_callback: Optional[Callable[[RunEvent], None]] = None,
    ) -> LaneResult:
        """
        Executes the persona's attack state machine against the target shop.
        Returns a structured LaneResult and populates events list.
        """
        raise NotImplementedError

