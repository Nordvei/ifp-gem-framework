"""
Adaptive GEM - Environment-Driven Specialization

Inspired by neuroplasticity: "Sensory experience and environmental factors
significantly shape brain development"

Research basis:
- "Experiences after birth—like seeing, hearing, or social interaction—may
  shape brain development far more than previously realized"
- Visual cortex specializes for frequently encountered visual patterns
- Neurons don't pre-decide their role - they discover it through activity

GEM Translation:
- Gems start unspecialized (no fixed role)
- Exposed to all system telemetry patterns
- Track success rates per pattern type
- After sufficient exposure (1000 cycles), discover specialization
- Specialize in patterns most frequently encountered AND highest success rate
"""

from base_gem import BaseGem
from collections import defaultdict
from typing import Dict, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class EnvironmentAdaptiveGem(BaseGem):
    """
    Adaptive GEM - discovers specialization from exposure.

    Biologically validated: neurons specialize based on sensory input,
    not pre-programming.
    """

    def __init__(self, name: Optional[str] = None):
        """
        Initialize adaptive gem (initially unspecialized).

        Args:
            name: Gem name (auto-generated if not provided)
        """
        super().__init__(name=name)

        # Initially unspecialized
        self.specialization = None
        self.specialization_confidence = 0.0

        # Exposure tracking
        self.exposure_history = defaultdict(int)  # pattern_type -> count
        self.capability_scores = defaultdict(float)  # pattern_type -> score

        # Specialization discovery
        self.discovery_threshold = 1000  # Cycles before specialization
        self.specialization_discovered_at = None

        # Behavior mode (changes with lifecycle stage)
        self.accept_all_task_types = True  # Initialization: try everything

        logger.info(
            f"Initialized adaptive gem {self.name} "
            f"(unspecialized, discovery threshold: {self.discovery_threshold})"
        )

    def observe_telemetry(self, telemetry_event: Dict) -> Optional[Dict]:
        """
        Expose gem to system telemetry.

        Like neuron exposed to sensory input.

        Args:
            telemetry_event: Telemetry event dictionary with:
                - type: Event type/pattern
                - data: Event data
                - timestamp: Event timestamp

        Returns:
            Result if gem attempted to handle, None if ignored
        """
        pattern_type = telemetry_event.get('type', 'unknown')

        # Record exposure
        self.exposure_history[pattern_type] += 1

        # Decide whether to handle based on lifecycle stage
        should_handle = self._should_handle_pattern(pattern_type)

        if not should_handle:
            return None

        # Attempt to handle (initially clumsy, improves with practice)
        result = self.attempt_handle(telemetry_event)

        # Update capability scores
        self._update_capability_score(pattern_type, result['success'])

        # Advance lifecycle
        self.advance_lifecycle()

        # Check if ready to discover specialization
        if self.lifecycle_count == self.discovery_threshold and not self.specialization:
            self.discover_specialization()

        return result

    def attempt_handle(self, telemetry_event: Dict) -> Dict:
        """
        Attempt to handle telemetry event.

        Success rate improves with:
        - Experience (lifecycle count)
        - Specialization focus
        - Plasticity level

        Args:
            telemetry_event: Event to handle

        Returns:
            Result dictionary with success/failure
        """
        pattern_type = telemetry_event.get('type')

        # Simulate handling (real implementation would do actual analysis)
        # Success probability based on:
        # 1. Current capability score for this pattern
        # 2. Specialization match
        # 3. Lifecycle stage (plasticity)

        base_success_rate = self.capability_scores.get(pattern_type, 0.3)

        # Bonus if this matches specialization
        if self.specialization == pattern_type:
            base_success_rate += 0.3

        # Plasticity affects learning speed
        base_success_rate = min(base_success_rate, 0.95)

        # Record task
        import random
        success = random.random() < base_success_rate

        self.record_task_result(
            task_type=pattern_type,
            success=success,
            duration=1.0,
            metadata={'event_id': telemetry_event.get('id')}
        )

        return {
            'success': success,
            'pattern_type': pattern_type,
            'confidence': self.capability_scores.get(pattern_type, 0.0)
        }

    def discover_specialization(self):
        """
        Gem discovers what it's naturally good at.

        Based on:
        1. Exposure frequency (most common patterns)
        2. Success rate (highest capability scores)

        Like visual cortex specializing for frequent visual inputs.
        """
        if not self.exposure_history:
            logger.warning(f"{self.name}: No exposure history for specialization")
            return

        # Find most common pattern
        most_common_pattern = max(
            self.exposure_history.items(),
            key=lambda x: x[1]
        )[0]

        # Find highest success rate
        best_capability_pattern = max(
            self.capability_scores.items(),
            key=lambda x: x[1]
        )[0] if self.capability_scores else most_common_pattern

        # Specialize in pattern with both high exposure AND high success
        if most_common_pattern == best_capability_pattern:
            # Perfect match - high exposure and high success
            self.specialization = most_common_pattern
            self.specialization_confidence = self.capability_scores.get(
                most_common_pattern, 0.5
            )
        else:
            # Weighted decision: prefer high success over high exposure
            # (quality over quantity)
            self.specialization = best_capability_pattern
            self.specialization_confidence = self.capability_scores.get(
                best_capability_pattern, 0.5
            )

        self.specialization_discovered_at = datetime.utcnow().isoformat() + 'Z'

        # Update behavior: stop accepting all tasks
        self.accept_all_task_types = False

        logger.info(
            f"🧬 {self.name} discovered specialization: {self.specialization} "
            f"(confidence: {self.specialization_confidence:.2%}, "
            f"exposure: {self.exposure_history[self.specialization]}, "
            f"at cycle: {self.lifecycle_count})"
        )

    def is_relevant_to_specialization(self, pattern_type: str) -> bool:
        """
        Check if pattern is relevant to gem's specialization.

        Args:
            pattern_type: Pattern type to check

        Returns:
            True if relevant, False otherwise
        """
        if not self.specialization:
            return True  # Accept all if not specialized

        # Exact match
        if pattern_type == self.specialization:
            return True

        # Category match (e.g., 'memory_leak' matches 'memory_*')
        if self.specialization.split('_')[0] in pattern_type:
            return True

        return False

    def force_specialization(self, pattern_type: str, confidence: float = 0.8):
        """
        Manually force gem to specialize.

        Use case: Coverage gap - no gem specialized in critical pattern.

        Args:
            pattern_type: Pattern to specialize in
            confidence: Initial confidence level
        """
        self.specialization = pattern_type
        self.specialization_confidence = confidence
        self.specialization_discovered_at = datetime.utcnow().isoformat() + 'Z'
        self.accept_all_task_types = False

        # Initialize capability score
        self.capability_scores[pattern_type] = confidence

        logger.warning(
            f"{self.name} forced to specialize in {pattern_type} "
            f"(confidence: {confidence:.2%}) - manual override"
        )

    def get_exposure_summary(self) -> Dict:
        """
        Get summary of exposure history.

        Returns:
            Dictionary with exposure statistics
        """
        if not self.exposure_history:
            return {
                'total_exposures': 0,
                'unique_patterns': 0,
                'top_patterns': []
            }

        total = sum(self.exposure_history.values())
        top_5 = sorted(
            self.exposure_history.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        return {
            'total_exposures': total,
            'unique_patterns': len(self.exposure_history),
            'top_patterns': [
                {'pattern': p, 'count': c, 'percentage': c/total*100}
                for p, c in top_5
            ]
        }

    def get_capability_summary(self) -> Dict:
        """
        Get summary of capability scores.

        Returns:
            Dictionary with capability statistics
        """
        if not self.capability_scores:
            return {
                'capabilities_count': 0,
                'top_capabilities': []
            }

        top_5 = sorted(
            self.capability_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]

        return {
            'capabilities_count': len(self.capability_scores),
            'top_capabilities': [
                {'pattern': p, 'score': s}
                for p, s in top_5
            ]
        }

    def get_status(self) -> Dict:
        """Get adaptive gem status"""
        base_status = super().get_status()

        base_status['adaptive'] = {
            'specialized': self.specialization is not None,
            'specialization_confidence': self.specialization_confidence,
            'discovered_at': self.specialization_discovered_at,
            'discovery_progress': f"{self.lifecycle_count}/{self.discovery_threshold}",
            'accept_all_tasks': self.accept_all_task_types,
            'exposure_summary': self.get_exposure_summary(),
            'capability_summary': self.get_capability_summary()
        }

        return base_status

    def _should_handle_pattern(self, pattern_type: str) -> bool:
        """
        Decide whether to handle a pattern based on lifecycle stage.

        Returns:
            True if should attempt to handle, False to ignore
        """
        # Initialization stage (0-100): Try everything
        if self.lifecycle_count < 100:
            return True

        # Specialization stage (100-500): Focus on top capabilities
        if self.lifecycle_count < 500:
            # Handle if in top 3 capabilities or not yet tried
            top_3_patterns = sorted(
                self.capability_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
            top_3_names = [p for p, _ in top_3_patterns]

            return (
                pattern_type in top_3_names or
                pattern_type not in self.capability_scores
            )

        # Refinement/Mature stage (500+): Only handle specialization
        return self.is_relevant_to_specialization(pattern_type)

    def _update_capability_score(self, pattern_type: str, success: bool):
        """
        Update capability score based on task result.

        Uses incremental updates:
        - Success: +0.01 per success
        - Failure: -0.005 per failure

        Args:
            pattern_type: Pattern type
            success: Whether task succeeded
        """
        if success:
            self.capability_scores[pattern_type] += 0.01
        else:
            self.capability_scores[pattern_type] -= 0.005

        # Clamp to [0, 1]
        self.capability_scores[pattern_type] = max(
            0.0,
            min(1.0, self.capability_scores[pattern_type])
        )
