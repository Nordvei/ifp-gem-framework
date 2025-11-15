# ============================================================================
# Intelligent Framework Platform (IFP)
# ============================================================================
# Copyright © 2025 BAYGERYCH IFP NORGE (Org. 936546730)
# All Rights Reserved - Patent Filed: NO 20251414 (November 15, 2025)
# ============================================================================

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
Inhibitory GEM - Resource Governor

Inspired by GABAergic neurons: "brakes" that prevent system overload.

Research basis:
- "GABAergic inhibitory neurons act like 'brakes' to calm excessive activity"
- "E/I imbalance causes hyperexcitability in autism/ADHD"
- Brain needs regulatory neurons, not just worker neurons

GEM Translation:
- Monitors system "excitability" (resource usage)
- Applies "brakes" when system approaches overload
- Prevents resource exhaustion, thrashing, cascading failures
- Essential for system stability (like GABA for brain stability)
"""

from base_gem import BaseGem
from typing import Dict, List, Optional
from datetime import datetime
import time
import logging

logger = logging.getLogger(__name__)


class ResourceGovernorGem(BaseGem):
    """
    Inhibitory GEM - acts like GABAergic neurons.

    Prevents system "hyperexcitability" (resource exhaustion).
    Does not do work - only regulates other gems.
    """

    def __init__(self, name: str = "resource_governor"):
        """
        Initialize resource governor gem.

        Args:
            name: Gem name (default: "resource_governor")
        """
        super().__init__(name=name)

        self.role = 'inhibitory'  # Not a worker gem
        self.specialization = 'resource_governance'

        # Monitoring configuration
        self.monitoring_interval = 30  # seconds
        self.running = False

        # Excitability thresholds (0.0-1.0)
        self.thresholds = {
            'low': 0.6,       # Start gentle braking
            'medium': 0.75,   # Moderate braking
            'high': 0.9       # Aggressive braking
        }

        # Excitability calculation weights
        self.weights = {
            'cpu': 0.3,
            'memory': 0.2,
            'active_gems': 0.2,
            'task_queue': 0.3
        }

        # Brake history
        self.brake_history = []
        self.max_brake_history = 1000

        logger.info(f"Initialized {self.name} (inhibitory gem)")

    def calculate_system_excitability(self, system_metrics: Dict) -> float:
        """
        Measure system "excitability" (overload risk).

        Like measuring neural firing rate in brain.

        Args:
            system_metrics: Dictionary with system metrics:
                - cpu_percent: CPU usage (0-100)
                - memory_percent: Memory usage (0-100)
                - active_gems: Number of active gems
                - task_queue_depth: Pending tasks

        Returns:
            Excitability score (0.0 = calm, 1.0 = critical)
        """
        # Normalize metrics to 0-1 range
        cpu_usage = system_metrics.get('cpu_percent', 0) / 100.0
        memory_usage = system_metrics.get('memory_percent', 0) / 100.0
        active_gems = min(system_metrics.get('active_gems', 0) / 10.0, 1.0)  # Assume max 10
        task_queue = min(system_metrics.get('task_queue_depth', 0) / 100.0, 1.0)  # Assume max 100

        # Weighted excitability score
        excitability = (
            cpu_usage * self.weights['cpu'] +
            memory_usage * self.weights['memory'] +
            active_gems * self.weights['active_gems'] +
            task_queue * self.weights['task_queue']
        )

        return min(excitability, 1.0)

    def determine_brake_level(self, excitability: float) -> str:
        """
        Determine brake severity based on excitability.

        Args:
            excitability: Excitability score (0.0-1.0)

        Returns:
            Brake level: 'none', 'low', 'medium', or 'high'
        """
        if excitability >= self.thresholds['high']:
            return 'high'
        elif excitability >= self.thresholds['medium']:
            return 'medium'
        elif excitability >= self.thresholds['low']:
            return 'low'
        else:
            return 'none'

    def apply_inhibitory_actions(self, brake_level: str,
                                 excitability: float,
                                 system_metrics: Dict,
                                 gem_coordinator) -> List[Dict]:
        """
        Apply brakes based on severity.

        Like GABA reducing neural firing rate.

        Args:
            brake_level: 'none', 'low', 'medium', or 'high'
            excitability: Current excitability score
            system_metrics: Current system metrics
            gem_coordinator: Interface to control other gems

        Returns:
            List of actions taken
        """
        actions_taken = []

        if brake_level == 'none':
            return actions_taken

        timestamp = datetime.utcnow().isoformat() + 'Z'

        # LOW: Gentle braking
        if brake_level == 'low':
            actions = [
                {
                    'action': 'reduce_task_intake',
                    'params': {'rate': 0.8},
                    'description': 'Slow task intake to 80% rate'
                },
                {
                    'action': 'suggest_optimization',
                    'params': {},
                    'description': 'Suggest resource optimization'
                }
            ]

        # MEDIUM: Moderate braking
        elif brake_level == 'medium':
            actions = [
                {
                    'action': 'limit_concurrent_gems',
                    'params': {'max_active': 5},
                    'description': 'Limit active gems to 5'
                },
                {
                    'action': 'increase_task_delay',
                    'params': {'multiplier': 1.5},
                    'description': 'Increase task delay by 50%'
                },
                {
                    'action': 'drop_low_priority',
                    'params': {},
                    'description': 'Drop low-priority tasks'
                }
            ]

        # HIGH: Aggressive braking
        else:  # 'high'
            actions = [
                {
                    'action': 'pause_non_critical_gems',
                    'params': {},
                    'description': 'Pause non-critical gems'
                },
                {
                    'action': 'reject_new_tasks',
                    'params': {},
                    'description': 'Reject all new tasks temporarily'
                },
                {
                    'action': 'increase_task_delay',
                    'params': {'multiplier': 3.0},
                    'description': 'Triple task delay'
                },
                {
                    'action': 'alert_human',
                    'params': {'severity': 'critical'},
                    'description': 'Alert human - system near critical overload'
                }
            ]

        # Execute actions (implementation depends on gem_coordinator interface)
        for action_spec in actions:
            result = self._execute_action(action_spec, gem_coordinator)
            actions_taken.append({
                'timestamp': timestamp,
                'brake_level': brake_level,
                'excitability': excitability,
                'action': action_spec['action'],
                'description': action_spec['description'],
                'result': result
            })

        # Record brake event
        self._record_brake_event(brake_level, excitability, system_metrics, actions_taken)

        logger.info(
            f"Applied {brake_level} brake: {len(actions_taken)} actions, "
            f"excitability: {excitability:.2%}"
        )

        return actions_taken

    def run_monitoring_loop(self, system_monitor, gem_coordinator):
        """
        Continuous monitoring loop (like GABAergic neurons).

        Args:
            system_monitor: Interface to get system metrics
            gem_coordinator: Interface to control other gems
        """
        self.running = True
        logger.info(f"{self.name} monitoring loop started (interval: {self.monitoring_interval}s)")

        while self.running:
            try:
                # Get current system metrics
                system_metrics = system_monitor.get_metrics()

                # Calculate excitability
                excitability = self.calculate_system_excitability(system_metrics)

                # Determine brake level
                brake_level = self.determine_brake_level(excitability)

                # Apply brakes if needed
                if brake_level != 'none':
                    self.apply_inhibitory_actions(
                        brake_level,
                        excitability,
                        system_metrics,
                        gem_coordinator
                    )

                # Sleep until next check
                time.sleep(self.monitoring_interval)

            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.monitoring_interval)

    def stop_monitoring(self):
        """Stop monitoring loop"""
        self.running = False
        logger.info(f"{self.name} monitoring loop stopped")

    def get_brake_effectiveness_metrics(self) -> Dict:
        """
        Calculate brake effectiveness metrics.

        Returns:
            Dictionary with effectiveness metrics
        """
        if not self.brake_history:
            return {
                'total_brakes': 0,
                'brake_rate': 0.0,
                'prevented_incidents': 0,
                'false_brakes': 0
            }

        total_brakes = len(self.brake_history)

        # Count by level
        brake_counts = {
            'low': sum(1 for b in self.brake_history if b['brake_level'] == 'low'),
            'medium': sum(1 for b in self.brake_history if b['brake_level'] == 'medium'),
            'high': sum(1 for b in self.brake_history if b['brake_level'] == 'high')
        }

        # Estimate effectiveness (simplified - real implementation would track outcomes)
        prevented_incidents = brake_counts['medium'] + brake_counts['high']

        return {
            'total_brakes': total_brakes,
            'brake_counts': brake_counts,
            'prevented_incidents': prevented_incidents,
            'avg_excitability': sum(b['excitability'] for b in self.brake_history) / total_brakes
        }

    def _execute_action(self, action_spec: Dict, gem_coordinator) -> str:
        """
        Execute a brake action.

        Args:
            action_spec: Action specification
            gem_coordinator: Gem coordinator interface

        Returns:
            Result status
        """
        # This is a stub - real implementation would call gem_coordinator methods
        action_name = action_spec['action']

        logger.info(f"Executing brake action: {action_name}")

        # Placeholder - real implementation would:
        # - Call gem_coordinator.pause_gems()
        # - Call gem_coordinator.reject_tasks()
        # - Call alerting system
        # etc.

        return 'success'

    def _record_brake_event(self, brake_level: str, excitability: float,
                           system_metrics: Dict, actions_taken: List[Dict]):
        """Record brake event for analysis"""
        event = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'brake_level': brake_level,
            'excitability': excitability,
            'system_metrics': system_metrics,
            'actions_count': len(actions_taken)
        }

        self.brake_history.append(event)

        # Trim history
        if len(self.brake_history) > self.max_brake_history:
            self.brake_history = self.brake_history[-self.max_brake_history:]

    def get_status(self) -> Dict:
        """Get resource governor status"""
        base_status = super().get_status()

        base_status['governor'] = {
            'running': self.running,
            'monitoring_interval': self.monitoring_interval,
            'thresholds': self.thresholds,
            'brake_history_size': len(self.brake_history),
            'effectiveness': self.get_brake_effectiveness_metrics()
        }

        return base_status
