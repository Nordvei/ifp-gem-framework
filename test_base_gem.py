"""
Unit tests for Base GEM Class

Tests 8-dimensional performance tracking, signature comparison,
and coordination primitives.
"""

import pytest
from base_gem import BaseGem, GemPerformanceSignature


class TestGemPerformanceSignature:
    """Test performance signature dataclass"""

    def test_signature_creation(self):
        """Test creating signature with defaults"""
        sig = GemPerformanceSignature()

        assert sig.capability_score == 0.0
        assert sig.energy_rating == 0.0
        assert sig.data_egress == 0
        assert sig.api_call_count == 0
        assert sig.cache_hit_ratio == 0.0
        assert sig.avg_response_time == 0.0
        assert sig.error_rate == 0.0
        assert sig.task_completion_rate == 0.0

    def test_signature_to_dict(self):
        """Test converting signature to dictionary"""
        sig = GemPerformanceSignature(
            capability_score=0.85,
            energy_rating=0.75,
            data_egress=1024
        )

        sig_dict = sig.to_dict()

        assert sig_dict['capability_score'] == 0.85
        assert sig_dict['energy_rating'] == 0.75
        assert sig_dict['data_egress'] == 1024


class TestBaseGem:
    """Test suite for base gem"""

    def test_gem_initialization(self):
        """Test creating a new gem"""
        gem = BaseGem(name="test_gem")

        assert gem.name == "test_gem"
        assert gem.gem_id is not None
        assert gem.lifecycle_count == 0
        assert gem.current_stage == 'initialization'
        assert gem.plasticity_level == 1.0
        assert gem.specialization is None
        assert gem.role == 'excitatory'
        assert gem.active is True

    def test_gem_auto_name(self):
        """Test gem name auto-generation"""
        gem = BaseGem()

        assert gem.name.startswith('gem_')
        assert len(gem.name) > 4

    def test_advance_lifecycle(self):
        """Test advancing lifecycle count"""
        gem = BaseGem()

        initial_count = gem.lifecycle_count
        gem.advance_lifecycle()

        assert gem.lifecycle_count == initial_count + 1

    def test_update_signature(self):
        """Test updating performance signature"""
        gem = BaseGem()

        gem.update_signature({
            'capability_score': 0.90,
            'energy_rating': 0.80,
            'cache_hit_ratio': 0.75
        })

        assert gem.signature.capability_score == 0.90
        assert gem.signature.energy_rating == 0.80
        assert gem.signature.cache_hit_ratio == 0.75

    def test_record_task_result(self):
        """Test recording task execution results"""
        gem = BaseGem()

        gem.record_task_result(
            task_type='memory_analysis',
            success=True,
            duration=1.5,
            metadata={'detected': 'leak'}
        )

        assert len(gem.task_history) == 1
        assert gem.task_history[0]['task_type'] == 'memory_analysis'
        assert gem.task_history[0]['success'] is True
        assert gem.task_history[0]['duration'] == 1.5

    def test_task_history_trimming(self):
        """Test that task history is trimmed to max size"""
        gem = BaseGem()
        gem.max_history = 10

        # Record 15 tasks
        for i in range(15):
            gem.record_task_result(
                task_type='test',
                success=True,
                duration=1.0
            )

        # Should only keep last 10
        assert len(gem.task_history) == 10

    def test_signature_updates_from_tasks(self):
        """Test that signature updates based on task results"""
        gem = BaseGem()

        # Record 10 successful tasks
        for _ in range(10):
            gem.record_task_result('test', success=True, duration=1.0)

        # Task completion rate should be 100%
        assert gem.signature.task_completion_rate == 1.0
        assert gem.signature.error_rate == 0.0

        # Capability score should be high
        assert gem.signature.capability_score > 0.9

    def test_signature_degradation_on_failures(self):
        """Test signature degrades with task failures"""
        gem = BaseGem()

        # Record mix of successes and failures
        for i in range(10):
            gem.record_task_result(
                'test',
                success=(i % 2 == 0),  # 50% success rate
                duration=1.0
            )

        # Task completion rate should be ~50%
        assert 0.4 < gem.signature.task_completion_rate < 0.6
        assert gem.signature.error_rate > 0.4

    def test_get_signature_vector(self):
        """Test getting signature as normalized vector"""
        gem = BaseGem()

        gem.update_signature({
            'capability_score': 0.85,
            'energy_rating': 0.75,
            'cache_hit_ratio': 0.90,
            'task_completion_rate': 0.88
        })

        vector = gem.get_signature_vector()

        assert len(vector) == 8
        assert vector[0] == 0.85  # capability_score
        assert vector[1] == 0.75  # energy_rating
        assert vector[4] == 0.90  # cache_hit_ratio
        assert vector[7] == 0.88  # task_completion_rate

    def test_compute_signature_distance(self):
        """Test measuring similarity between gems"""
        gem1 = BaseGem(name="gem1")
        gem2 = BaseGem(name="gem2")

        # Make signatures identical
        gem1.update_signature({'capability_score': 0.85, 'energy_rating': 0.75})
        gem2.update_signature({'capability_score': 0.85, 'energy_rating': 0.75})

        # Distance should be zero
        distance = gem1.compute_signature_distance(gem2)
        assert distance == 0.0

    def test_signature_distance_different_gems(self):
        """Test distance between different gems"""
        gem1 = BaseGem(name="gem1")
        gem2 = BaseGem(name="gem2")

        gem1.update_signature({'capability_score': 1.0})
        gem2.update_signature({'capability_score': 0.0})

        # Distance should be non-zero
        distance = gem1.compute_signature_distance(gem2)
        assert distance > 0

    def test_find_similar_gems(self):
        """Test finding gems with similar signatures"""
        gem1 = BaseGem(name="gem1")
        gem2 = BaseGem(name="gem2")  # Similar to gem1
        gem3 = BaseGem(name="gem3")  # Different

        # Make gem2 similar to gem1
        gem1.update_signature({'capability_score': 0.85, 'energy_rating': 0.75})
        gem2.update_signature({'capability_score': 0.86, 'energy_rating': 0.76})
        gem3.update_signature({'capability_score': 0.20, 'energy_rating': 0.15})

        all_gems = [gem1, gem2, gem3]
        similar = gem1.find_similar_gems(all_gems, threshold=0.3)

        # Should find gem2 but not gem3
        assert gem2 in similar
        assert gem3 not in similar

    def test_pause_and_resume(self):
        """Test pausing and resuming gem"""
        gem = BaseGem()

        assert gem.active is True
        assert gem.should_execute() is True

        # Pause gem
        gem.pause(paused_by='resource_governor', reason='system_overload')

        assert gem.active is False
        assert gem.paused_by == 'resource_governor'
        assert gem.should_execute() is False

        # Resume gem
        gem.resume()

        assert gem.active is True
        assert gem.paused_by is None
        assert gem.should_execute() is True

    def test_get_status(self):
        """Test getting comprehensive gem status"""
        gem = BaseGem(name="status_gem")

        gem.specialization = "memory_analysis"
        gem.lifecycle_count = 250
        gem.current_stage = "specialization"

        status = gem.get_status()

        assert status['name'] == "status_gem"
        assert status['specialization'] == "memory_analysis"
        assert status['role'] == "excitatory"
        assert status['active'] is True
        assert status['lifecycle']['cycle_count'] == 250
        assert status['lifecycle']['current_stage'] == "specialization"
        assert 'signature' in status
        assert 'created_at' in status

    def test_gem_repr(self):
        """Test gem string representation"""
        gem = BaseGem(name="repr_gem")
        gem.specialization = "performance"
        gem.current_stage = "refinement"

        repr_str = repr(gem)

        assert 'BaseGem' in repr_str
        assert 'repr_gem' in repr_str
        assert 'performance' in repr_str
        assert 'refinement' in repr_str


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
