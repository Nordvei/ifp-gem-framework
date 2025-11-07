"""
Unit tests for GEM Lifecycle Manager

Tests developmental stage transitions, plasticity levels,
and critical period behavior.
"""

import pytest
from lifecycle_manager import GemLifecycleManager


class TestGemLifecycleManager:
    """Test suite for lifecycle manager"""

    def setup_method(self):
        """Setup test instance before each test"""
        self.manager = GemLifecycleManager()

    def test_register_new_gem(self):
        """Test registering a new gem"""
        self.manager.register_gem('gem001')

        assert 'gem001' in self.manager.gems_lifecycle
        assert self.manager.get_cycle_count('gem001') == 0
        assert self.manager.get_current_stage('gem001').name == 'initialization'
        assert self.manager.get_plasticity('gem001') == 1.0

    def test_register_gem_with_initial_cycles(self):
        """Test registering gem with existing cycle count"""
        # Register gem starting at specialization stage (200 cycles)
        self.manager.register_gem('gem002', initial_cycle_count=200)

        assert self.manager.get_cycle_count('gem002') == 200
        assert self.manager.get_current_stage('gem002').name == 'specialization'
        assert self.manager.get_plasticity('gem002') == 0.5

    def test_initialization_stage(self):
        """Test initialization stage characteristics (0-100 cycles)"""
        self.manager.register_gem('gem003')

        stage = self.manager.get_current_stage('gem003')
        assert stage.name == 'initialization'
        assert stage.plasticity == 1.0
        assert stage.behavior == 'explore_all_tasks'
        assert stage.cycles == (0, 100)

    def test_specialization_stage(self):
        """Test specialization stage characteristics (100-500 cycles)"""
        self.manager.register_gem('gem004', initial_cycle_count=250)

        stage = self.manager.get_current_stage('gem004')
        assert stage.name == 'specialization'
        assert stage.plasticity == 0.5
        assert stage.behavior == 'focus_on_strengths'
        assert stage.cycles == (100, 500)

    def test_refinement_stage(self):
        """Test refinement stage characteristics (500-2000 cycles)"""
        self.manager.register_gem('gem005', initial_cycle_count=1000)

        stage = self.manager.get_current_stage('gem005')
        assert stage.name == 'refinement'
        assert stage.plasticity == 0.2
        assert stage.behavior == 'optimize_specialty'
        assert stage.cycles == (500, 2000)

    def test_mature_stage(self):
        """Test mature stage characteristics (2000+ cycles)"""
        self.manager.register_gem('gem006', initial_cycle_count=3000)

        stage = self.manager.get_current_stage('gem006')
        assert stage.name == 'mature'
        assert stage.plasticity == 0.05
        assert stage.behavior == 'stable_expert'

    def test_stage_transition_initialization_to_specialization(self):
        """Test transition from initialization to specialization at 100 cycles"""
        self.manager.register_gem('gem007', initial_cycle_count=99)

        # Should be in initialization
        assert self.manager.get_current_stage('gem007').name == 'initialization'

        # Advance to cycle 100
        self.manager.advance_gem_stage('gem007')

        # Should transition to specialization
        assert self.manager.get_current_stage('gem007').name == 'specialization'
        assert self.manager.get_cycle_count('gem007') == 100

        # Check history
        history = self.manager.get_stage_history('gem007')
        assert len(history) == 1
        assert history[0]['from_stage'] == 'initialization'
        assert history[0]['to_stage'] == 'specialization'
        assert history[0]['at_cycle'] == 100

    def test_stage_transition_specialization_to_refinement(self):
        """Test transition from specialization to refinement at 500 cycles"""
        self.manager.register_gem('gem008', initial_cycle_count=499)

        assert self.manager.get_current_stage('gem008').name == 'specialization'

        # Advance to cycle 500
        self.manager.advance_gem_stage('gem008')

        assert self.manager.get_current_stage('gem008').name == 'refinement'
        assert self.manager.get_cycle_count('gem008') == 500

    def test_stage_transition_refinement_to_mature(self):
        """Test transition from refinement to mature at 2000 cycles"""
        self.manager.register_gem('gem009', initial_cycle_count=1999)

        assert self.manager.get_current_stage('gem009').name == 'refinement'

        # Advance to cycle 2000
        self.manager.advance_gem_stage('gem009')

        assert self.manager.get_current_stage('gem009').name == 'mature'
        assert self.manager.get_cycle_count('gem009') == 2000

    def test_multiple_advances(self):
        """Test advancing gem through multiple cycles"""
        self.manager.register_gem('gem010')

        # Advance 150 times
        for _ in range(150):
            self.manager.advance_gem_stage('gem010')

        assert self.manager.get_cycle_count('gem010') == 150
        assert self.manager.get_current_stage('gem010').name == 'specialization'

        # Should have recorded one transition
        history = self.manager.get_stage_history('gem010')
        assert len(history) == 1

    def test_plasticity_decreases_over_lifecycle(self):
        """Test that plasticity decreases as gem matures"""
        plasticities = []

        # Sample plasticity at different lifecycle points
        for cycle in [0, 100, 500, 2000]:
            gem_id = f'gem_plasticity_{cycle}'
            self.manager.register_gem(gem_id, initial_cycle_count=cycle)
            plasticities.append(self.manager.get_plasticity(gem_id))

        # Verify decreasing plasticity: 1.0 -> 0.5 -> 0.2 -> 0.05
        assert plasticities == [1.0, 0.5, 0.2, 0.05]

    def test_behavior_mode_changes(self):
        """Test that behavior mode changes through lifecycle"""
        behaviors = []

        for cycle in [0, 100, 500, 2000]:
            gem_id = f'gem_behavior_{cycle}'
            self.manager.register_gem(gem_id, initial_cycle_count=cycle)
            behaviors.append(self.manager.get_behavior_mode(gem_id))

        expected = [
            'explore_all_tasks',
            'focus_on_strengths',
            'optimize_specialty',
            'stable_expert'
        ]
        assert behaviors == expected

    def test_retraining(self):
        """Test resetting mature gem for retraining"""
        self.manager.register_gem('gem_retrain', initial_cycle_count=3000)

        # Should be mature
        assert self.manager.get_current_stage('gem_retrain').name == 'mature'
        assert self.manager.get_cycle_count('gem_retrain') == 3000

        # Request retraining
        self.manager.allow_retraining('gem_retrain', reason='system_needs_changed')

        # Should be reset to initialization
        assert self.manager.get_current_stage('gem_retrain').name == 'initialization'
        assert self.manager.get_cycle_count('gem_retrain') == 0
        assert self.manager.get_plasticity('gem_retrain') == 1.0

        # History should record retraining
        history = self.manager.get_stage_history('gem_retrain')
        assert any('retraining' in h.get('reason', '') for h in history)

    def test_unregistered_gem_operations(self):
        """Test operations on unregistered gems return None/defaults"""
        assert self.manager.get_current_stage('nonexistent') is None
        assert self.manager.get_plasticity('nonexistent') == 0.0
        assert self.manager.get_behavior_mode('nonexistent') is None
        assert self.manager.get_cycle_count('nonexistent') == 0
        assert self.manager.get_stage_history('nonexistent') == []
        assert self.manager.advance_gem_stage('nonexistent') is None

    def test_lifecycle_summary(self):
        """Test getting complete lifecycle summary"""
        self.manager.register_gem('gem_summary', initial_cycle_count=150)

        # Advance a few times
        for _ in range(10):
            self.manager.advance_gem_stage('gem_summary')

        summary = self.manager.get_lifecycle_summary('gem_summary')

        assert summary['gem_id'] == 'gem_summary'
        assert summary['cycle_count'] == 160
        assert summary['current_stage'] == 'specialization'
        assert summary['plasticity'] == 0.5
        assert summary['behavior_mode'] == 'focus_on_strengths'
        assert 'registered_at' in summary

    def test_all_gems_status(self):
        """Test getting status of all registered gems"""
        # Register multiple gems
        self.manager.register_gem('gem_a', initial_cycle_count=50)
        self.manager.register_gem('gem_b', initial_cycle_count=300)
        self.manager.register_gem('gem_c', initial_cycle_count=1500)

        status = self.manager.get_all_gems_status()

        assert len(status) == 3
        assert 'gem_a' in status
        assert 'gem_b' in status
        assert 'gem_c' in status

        assert status['gem_a']['current_stage'] == 'initialization'
        assert status['gem_b']['current_stage'] == 'specialization'
        assert status['gem_c']['current_stage'] == 'refinement'

    def test_complete_lifecycle_progression(self):
        """Test gem progressing through entire lifecycle"""
        self.manager.register_gem('gem_complete')

        # Track all stages encountered
        stages_seen = set()

        # Advance through 2500 cycles
        for i in range(2500):
            stage = self.manager.get_current_stage('gem_complete')
            stages_seen.add(stage.name)
            self.manager.advance_gem_stage('gem_complete')

        # Should have seen all 4 stages
        assert stages_seen == {'initialization', 'specialization', 'refinement', 'mature'}

        # Should have 3 transitions recorded
        history = self.manager.get_stage_history('gem_complete')
        assert len(history) == 3

        # Final state should be mature
        assert self.manager.get_current_stage('gem_complete').name == 'mature'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
