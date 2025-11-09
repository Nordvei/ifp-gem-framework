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
GEM Lifecycle Manager - Brain-Inspired Developmental Stages

Biologically validated: Neurons develop through critical periods, not pre-programmed.

Research basis:
- "Neurons continue taking up specialized identities after birth"
- "First year postnatal represents peak neuroplasticity"
- "Extended window from 3-7 years retains moderate-high effectiveness"

GEM Translation:
- Initialization (0-100 cycles): High plasticity, explore all tasks
- Specialization (100-500 cycles): Moderate plasticity, focus on strengths
- Refinement (500-2000 cycles): Low plasticity, optimize specialty
- Mature (2000+ cycles): Minimal plasticity, stable expert
"""

from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class DevelopmentalStage:
    """Represents a developmental stage with its characteristics"""
    name: str
    cycles: Tuple[int, float]
    plasticity: float
    behavior: str
    description: str


class GemLifecycleManager:
    """
    Manages GEM development through critical periods.

    Biologically validated: neurons develop, not pre-programmed.
    """

    DEVELOPMENTAL_STAGES = {
        'initialization': DevelopmentalStage(
            name='initialization',
            cycles=(0, 100),
            plasticity=1.0,
            behavior='explore_all_tasks',
            description='Gem tries everything, discovers capabilities'
        ),
        'specialization': DevelopmentalStage(
            name='specialization',
            cycles=(100, 500),
            plasticity=0.5,
            behavior='focus_on_strengths',
            description='Gem narrows focus to top-performing tasks'
        ),
        'refinement': DevelopmentalStage(
            name='refinement',
            cycles=(500, 2000),
            plasticity=0.2,
            behavior='optimize_specialty',
            description='Gem perfects specialized skills'
        ),
        'mature': DevelopmentalStage(
            name='mature',
            cycles=(2000, float('inf')),
            plasticity=0.05,
            behavior='stable_expert',
            description='Gem locked into role, minimal adaptation'
        )
    }

    def __init__(self):
        """Initialize lifecycle manager"""
        self.gems_lifecycle = {}  # gem_id -> lifecycle data

    def register_gem(self, gem_id: str, initial_cycle_count: int = 0):
        """
        Register a new gem for lifecycle tracking.

        Args:
            gem_id: Unique identifier for the gem
            initial_cycle_count: Starting cycle count (default 0 for new gems)
        """
        self.gems_lifecycle[gem_id] = {
            'cycle_count': initial_cycle_count,
            'current_stage': self._determine_stage(initial_cycle_count),
            'stage_history': [],
            'registered_at': datetime.utcnow().isoformat() + 'Z'
        }

        stage = self._determine_stage(initial_cycle_count)
        logger.info(
            f"Registered gem {gem_id} at cycle {initial_cycle_count}, "
            f"stage: {stage}"
        )

    def advance_gem_stage(self, gem_id: str) -> Optional[str]:
        """
        Advance gem through developmental stages.

        Args:
            gem_id: Gem identifier

        Returns:
            Current stage name, or None if gem not registered
        """
        if gem_id not in self.gems_lifecycle:
            logger.warning(f"Gem {gem_id} not registered in lifecycle manager")
            return None

        # Increment cycle count
        self.gems_lifecycle[gem_id]['cycle_count'] += 1
        cycle_count = self.gems_lifecycle[gem_id]['cycle_count']

        # Determine new stage
        old_stage = self.gems_lifecycle[gem_id]['current_stage']
        new_stage = self._determine_stage(cycle_count)

        # Record stage transition
        if old_stage != new_stage:
            self.gems_lifecycle[gem_id]['stage_history'].append({
                'from_stage': old_stage,
                'to_stage': new_stage,
                'at_cycle': cycle_count,
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            })
            logger.info(
                f"Gem {gem_id} transitioned: {old_stage} -> {new_stage} "
                f"at cycle {cycle_count}"
            )

        self.gems_lifecycle[gem_id]['current_stage'] = new_stage
        return new_stage

    def get_current_stage(self, gem_id: str) -> Optional[DevelopmentalStage]:
        """
        Get current developmental stage for a gem.

        Args:
            gem_id: Gem identifier

        Returns:
            DevelopmentalStage object, or None if gem not registered
        """
        if gem_id not in self.gems_lifecycle:
            return None

        stage_name = self.gems_lifecycle[gem_id]['current_stage']
        return self.DEVELOPMENTAL_STAGES[stage_name]

    def get_plasticity(self, gem_id: str) -> float:
        """
        Get current plasticity level for a gem.

        Plasticity determines learning rate:
        - 1.0 (initialization): Maximum learning
        - 0.5 (specialization): Moderate learning
        - 0.2 (refinement): Low learning
        - 0.05 (mature): Minimal learning

        Args:
            gem_id: Gem identifier

        Returns:
            Plasticity level (0.0-1.0), or 0.0 if gem not registered
        """
        stage = self.get_current_stage(gem_id)
        return stage.plasticity if stage else 0.0

    def get_behavior_mode(self, gem_id: str) -> Optional[str]:
        """
        Get current behavior mode for a gem.

        Modes:
        - 'explore_all_tasks': Try everything (initialization)
        - 'focus_on_strengths': Narrow to top capabilities (specialization)
        - 'optimize_specialty': Perfect the specialty (refinement)
        - 'stable_expert': Locked into role (mature)

        Args:
            gem_id: Gem identifier

        Returns:
            Behavior mode string, or None if gem not registered
        """
        stage = self.get_current_stage(gem_id)
        return stage.behavior if stage else None

    def get_cycle_count(self, gem_id: str) -> int:
        """Get total cycle count for a gem"""
        if gem_id not in self.gems_lifecycle:
            return 0
        return self.gems_lifecycle[gem_id]['cycle_count']

    def get_stage_history(self, gem_id: str) -> list:
        """Get stage transition history for a gem"""
        if gem_id not in self.gems_lifecycle:
            return []
        return self.gems_lifecycle[gem_id]['stage_history']

    def allow_retraining(self, gem_id: str, reason: str = "manual_override"):
        """
        Reset gem to initialization stage for retraining.

        Use case: System needs change after maturity, gem needs new role.

        Args:
            gem_id: Gem identifier
            reason: Reason for retraining (for audit trail)
        """
        if gem_id not in self.gems_lifecycle:
            logger.warning(f"Cannot retrain unregistered gem {gem_id}")
            return

        old_stage = self.gems_lifecycle[gem_id]['current_stage']

        # Reset to initialization but keep cycle history
        self.gems_lifecycle[gem_id]['stage_history'].append({
            'from_stage': old_stage,
            'to_stage': 'initialization',
            'at_cycle': self.gems_lifecycle[gem_id]['cycle_count'],
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'reason': f'retraining:{reason}'
        })

        # Reset cycle count and stage
        self.gems_lifecycle[gem_id]['cycle_count'] = 0
        self.gems_lifecycle[gem_id]['current_stage'] = 'initialization'

        logger.warning(
            f"Gem {gem_id} reset to initialization for retraining. "
            f"Reason: {reason}"
        )

    def get_lifecycle_summary(self, gem_id: str) -> Dict:
        """
        Get complete lifecycle summary for a gem.

        Returns:
            Dictionary with lifecycle metrics, or empty dict if not registered
        """
        if gem_id not in self.gems_lifecycle:
            return {}

        stage = self.get_current_stage(gem_id)

        return {
            'gem_id': gem_id,
            'cycle_count': self.get_cycle_count(gem_id),
            'current_stage': stage.name if stage else 'unknown',
            'plasticity': stage.plasticity if stage else 0.0,
            'behavior_mode': stage.behavior if stage else 'unknown',
            'stage_description': stage.description if stage else 'unknown',
            'transitions': len(self.get_stage_history(gem_id)),
            'registered_at': self.gems_lifecycle[gem_id]['registered_at']
        }

    def _determine_stage(self, cycle_count: int) -> str:
        """Determine developmental stage based on cycle count"""
        for stage_name, stage_config in self.DEVELOPMENTAL_STAGES.items():
            start, end = stage_config.cycles
            if start <= cycle_count < end:
                return stage_name
        return 'mature'

    def get_all_gems_status(self) -> Dict[str, Dict]:
        """
        Get status of all registered gems.

        Returns:
            Dictionary mapping gem_id to lifecycle summary
        """
        return {
            gem_id: self.get_lifecycle_summary(gem_id)
            for gem_id in self.gems_lifecycle
        }
