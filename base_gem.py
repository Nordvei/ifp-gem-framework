# IFP (Infinity Folder Project)
#
# Copyright (c) 2025 Andriy Baygerych. All rights reserved.
#
# This software is part of the IFP project, a production-grade observability
# and orchestration platform for autonomous infrastructure monitoring using
# brain-inspired multi-agent systems (GEM framework).
#
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See LICENSE file for details.
#
# For commercial licensing inquiries: info@infinity-folder.no
#
# Patent pending. Additional intellectual property rights reserved.
"""
Base GEM Class - 8-Dimensional Performance Tracking

Inspired by brain's cellular signatures: multi-dimensional profiles
that define cell types.

8 Performance Dimensions:
1. capability_score: Task quality (0.0-1.0)
2. energy_rating: Resource efficiency (0.0-1.0)
3. data_egress: Privacy/bandwidth cost (bytes)
4. api_call_count: External dependency count
5. cache_hit_ratio: Memory efficiency (0.0-1.0)
6. avg_response_time: Speed (seconds)
7. error_rate: Reliability (0.0-1.0)
8. task_completion_rate: Success rate (0.0-1.0)
"""

from typing import Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
import logging
import math

logger = logging.getLogger(__name__)


@dataclass
class GemPerformanceSignature:
    """
    Multi-dimensional performance profile.

    Like brain's cellular signatures - unique combinations
    that define gem capabilities.
    """
    capability_score: float = 0.0  # Task quality
    energy_rating: float = 0.0  # Resource efficiency
    data_egress: int = 0  # Privacy/bandwidth
    api_call_count: int = 0  # External dependency
    cache_hit_ratio: float = 0.0  # Memory efficiency
    avg_response_time: float = 0.0  # Speed
    error_rate: float = 0.0  # Reliability
    task_completion_rate: float = 0.0  # Success rate

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'capability_score': self.capability_score,
            'energy_rating': self.energy_rating,
            'data_egress': self.data_egress,
            'api_call_count': self.api_call_count,
            'cache_hit_ratio': self.cache_hit_ratio,
            'avg_response_time': self.avg_response_time,
            'error_rate': self.error_rate,
            'task_completion_rate': self.task_completion_rate
        }


class BaseGem:
    """
    Base class for all GEMs in the ecosystem.

    Provides:
    - 8-dimensional performance tracking
    - Lifecycle integration
    - Coordination primitives
    - Observability
    """

    def __init__(self, name: Optional[str] = None):
        """
        Initialize base gem.

        Args:
            name: Gem name (generated if not provided)
        """
        self.gem_id = str(uuid4())
        self.name = name or f"gem_{self.gem_id[:8]}"

        # Lifecycle tracking
        self.lifecycle_count = 0
        self.current_stage = 'initialization'
        self.plasticity_level = 1.0

        # Specialization
        self.specialization = None
        self.role = 'excitatory'  # 'excitatory' (worker) or 'inhibitory' (governor)

        # Performance signature
        self.signature = GemPerformanceSignature()

        # Task history
        self.task_history = []
        self.max_history = 1000

        # Coordination
        self.active = True
        self.paused_by = None

        # Timestamps
        self.created_at = datetime.utcnow().isoformat() + 'Z'
        self.last_active_at = self.created_at

        logger.info(f"Initialized {self.name} (id: {self.gem_id})")

    def advance_lifecycle(self):
        """
        Advance gem lifecycle by one cycle.

        Should be called by lifecycle manager, not directly.
        """
        self.lifecycle_count += 1
        self.last_active_at = datetime.utcnow().isoformat() + 'Z'

    def update_signature(self, metrics: Dict):
        """
        Update performance signature with new metrics.

        Args:
            metrics: Dictionary of performance metrics
        """
        # Update signature fields if present in metrics
        for field_name in self.signature.__dataclass_fields__:
            if field_name in metrics:
                setattr(self.signature, field_name, metrics[field_name])

    def record_task_result(self, task_type: str, success: bool,
                          duration: float, metadata: Optional[Dict] = None):
        """
        Record task execution result.

        Args:
            task_type: Type of task executed
            success: Whether task succeeded
            duration: Task duration in seconds
            metadata: Optional additional data
        """
        result = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'task_type': task_type,
            'success': success,
            'duration': duration,
            'metadata': metadata or {}
        }

        self.task_history.append(result)

        # Trim history if too long
        if len(self.task_history) > self.max_history:
            self.task_history = self.task_history[-self.max_history:]

        # Update signature metrics based on task result
        self._update_signature_from_task(task_type, success, duration)

    def get_signature_vector(self) -> List[float]:
        """
        Get signature as normalized vector for similarity comparison.

        Returns:
            8-dimensional normalized vector
        """
        return [
            self.signature.capability_score,
            self.signature.energy_rating,
            self.signature.data_egress / 1_000_000,  # Normalize to MB
            self.signature.api_call_count / 100,  # Normalize to 0-1 range
            self.signature.cache_hit_ratio,
            min(self.signature.avg_response_time / 10, 1.0),  # Cap at 10s
            self.signature.error_rate,
            self.signature.task_completion_rate
        ]

    def compute_signature_distance(self, other_gem: 'BaseGem') -> float:
        """
        Measure similarity to another gem.

        Uses Euclidean distance on normalized signatures.
        Like measuring cellular signature similarity in brain atlas research.

        Args:
            other_gem: Gem to compare with

        Returns:
            Distance metric (0.0 = identical, higher = more different)
        """
        self_vector = self.get_signature_vector()
        other_vector = other_gem.get_signature_vector()

        distance = sum(
            (a - b) ** 2
            for a, b in zip(self_vector, other_vector)
        )

        return math.sqrt(distance)

    def find_similar_gems(self, all_gems: List['BaseGem'],
                         threshold: float = 0.3) -> List['BaseGem']:
        """
        Identify gems with similar cellular signatures.

        Similar gems can:
        - Collaborate on tasks
        - Replace each other (redundancy)
        - Form specialized "neighborhoods" (like brain regions)

        Args:
            all_gems: List of all gems to compare with
            threshold: Maximum distance to consider similar

        Returns:
            List of similar gems
        """
        similar = []

        for gem in all_gems:
            if gem.gem_id == self.gem_id:
                continue

            distance = self.compute_signature_distance(gem)
            if distance < threshold:
                similar.append(gem)

        return similar

    def pause(self, paused_by: str, reason: str):
        """
        Pause gem execution.

        Used by ResourceGovernor to apply "brakes".

        Args:
            paused_by: Identifier of pauser (e.g., 'resource_governor')
            reason: Reason for pause
        """
        self.active = False
        self.paused_by = paused_by

        logger.info(
            f"Gem {self.name} paused by {paused_by}. Reason: {reason}"
        )

    def resume(self):
        """Resume gem execution after pause"""
        self.active = True
        pauser = self.paused_by
        self.paused_by = None

        logger.info(f"Gem {self.name} resumed (was paused by {pauser})")

    def should_execute(self) -> bool:
        """
        Check if gem should execute tasks.

        Returns False if paused by ResourceGovernor.

        Returns:
            True if gem can execute, False if paused
        """
        return self.active

    def get_status(self) -> Dict:
        """
        Get comprehensive gem status.

        Returns:
            Dictionary with all gem state
        """
        return {
            'gem_id': self.gem_id,
            'name': self.name,
            'specialization': self.specialization,
            'role': self.role,
            'active': self.active,
            'paused_by': self.paused_by,
            'lifecycle': {
                'cycle_count': self.lifecycle_count,
                'current_stage': self.current_stage,
                'plasticity_level': self.plasticity_level
            },
            'signature': self.signature.to_dict(),
            'task_count': len(self.task_history),
            'created_at': self.created_at,
            'last_active_at': self.last_active_at
        }

    def _update_signature_from_task(self, task_type: str,
                                   success: bool, duration: float):
        """
        Update signature metrics based on task execution.

        Uses exponential moving average for smooth updates.
        """
        # Task completion rate
        recent_tasks = self.task_history[-100:] if len(self.task_history) >= 100 else self.task_history
        if recent_tasks:
            success_count = sum(1 for t in recent_tasks if t['success'])
            self.signature.task_completion_rate = success_count / len(recent_tasks)

        # Error rate (inverse of success)
        self.signature.error_rate = 1.0 - self.signature.task_completion_rate

        # Average response time (exponential moving average)
        alpha = 0.1  # Smoothing factor
        if self.signature.avg_response_time == 0:
            self.signature.avg_response_time = duration
        else:
            self.signature.avg_response_time = (
                alpha * duration +
                (1 - alpha) * self.signature.avg_response_time
            )

        # Capability score (based on recent success rate)
        if self.signature.task_completion_rate > 0.9:
            self.signature.capability_score = 0.95
        elif self.signature.task_completion_rate > 0.75:
            self.signature.capability_score = 0.85
        elif self.signature.task_completion_rate > 0.5:
            self.signature.capability_score = 0.70
        else:
            self.signature.capability_score = 0.50

    def __repr__(self):
        return (
            f"<{self.__class__.__name__} "
            f"name={self.name} "
            f"specialization={self.specialization} "
            f"stage={self.current_stage}>"
        )
