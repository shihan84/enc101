"""
Test script for profile-specific SCTE-35 marker directories
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.services.scte35_service import SCTE35Service
from src.services.profile_service import ProfileService

def test_profile_specific_directories():
    """Test profile-specific SCTE-35 directories"""
    print("=" * 60)
    print("Testing Profile-Specific SCTE-35 Directories")
    print("=" * 60)
    
    # Test 1: Default profile
    print("\n[TEST 1] Default Profile")
    print("-" * 60)
    service_default = SCTE35Service(profile_name=None)
    print(f"[OK] Profile: {service_default.profile_name}")
    print(f"[OK] Directory: {service_default.markers_dir}")
    print(f"[OK] State file: {service_default.state_file}")
    print(f"[OK] Last Event ID: {service_default._last_event_id}")
    assert service_default.markers_dir == Path("scte35_final"), "Default directory should be scte35_final"
    assert service_default.profile_name == "default", "Default profile name should be 'default'"
    print("[PASS] Default profile uses correct directory")
    
    # Test 2: Named profile
    print("\n[TEST 2] Named Profile: 'Distributor_SRT'")
    print("-" * 60)
    service_profile1 = SCTE35Service(profile_name="Distributor_SRT")
    print(f"[OK] Profile: {service_profile1.profile_name}")
    print(f"[OK] Directory: {service_profile1.markers_dir}")
    print(f"[OK] State file: {service_profile1.state_file}")
    print(f"[OK] Last Event ID: {service_profile1._last_event_id}")
    expected_dir = Path("scte35_final") / "Distributor_SRT"
    assert service_profile1.markers_dir == expected_dir, f"Profile directory should be {expected_dir}"
    assert service_profile1.profile_name == "Distributor_SRT", "Profile name should match"
    assert service_profile1.markers_dir.exists(), "Profile directory should exist"
    print("[PASS] Named profile uses profile-specific directory")
    
    # Test 3: Another named profile
    print("\n[TEST 3] Named Profile: 'HLS_Output'")
    print("-" * 60)
    service_profile2 = SCTE35Service(profile_name="HLS_Output")
    print(f"[OK] Profile: {service_profile2.profile_name}")
    print(f"[OK] Directory: {service_profile2.markers_dir}")
    print(f"[OK] State file: {service_profile2.state_file}")
    print(f"[OK] Last Event ID: {service_profile2._last_event_id}")
    expected_dir2 = Path("scte35_final") / "HLS_Output"
    assert service_profile2.markers_dir == expected_dir2, f"Profile directory should be {expected_dir2}"
    assert service_profile2.profile_name == "HLS_Output", "Profile name should match"
    assert service_profile2.markers_dir.exists(), "Profile directory should exist"
    print("[PASS] Second profile uses separate directory")
    
    # Test 4: Profile switching
    print("\n[TEST 4] Profile Switching")
    print("-" * 60)
    service = SCTE35Service(profile_name="Test_Profile_1")
    original_dir = service.markers_dir
    original_id = service._last_event_id
    print(f"Initial: Profile={service.profile_name}, Dir={service.markers_dir}, ID={original_id}")
    
    service.set_profile("Test_Profile_2")
    print(f"After switch: Profile={service.profile_name}, Dir={service.markers_dir}, ID={service._last_event_id}")
    assert service.profile_name == "Test_Profile_2", "Profile should switch"
    assert service.markers_dir != original_dir, "Directory should change"
    assert service.markers_dir.exists(), "New directory should exist"
    print("[PASS] Profile switching works correctly")
    
    # Test 5: Independent Event IDs
    print("\n[TEST 5] Independent Event ID Sequences")
    print("-" * 60)
    service1 = SCTE35Service(profile_name="ID_Test_1")
    service2 = SCTE35Service(profile_name="ID_Test_2")
    
    # Get initial IDs from each profile
    id1_initial = service1.get_next_event_id()
    id2_initial = service2.get_next_event_id()
    
    # Save a marker to increment profile 1's state
    service1._save_last_event_id(id1_initial)
    
    # Get next IDs after saving
    id1_next = service1.get_next_event_id()
    id2_next = service2.get_next_event_id()
    
    print(f"Profile 1: Initial={id1_initial}, After save={id1_next}")
    print(f"Profile 2: Initial={id2_initial}, After save={id2_next}")
    
    # Profile 1 should increment, Profile 2 should stay same
    assert id1_next == id1_initial + 1, "Profile 1 should increment after save"
    assert id2_next == id2_initial, "Profile 2 should not change (no save)"
    print("[PASS] Each profile maintains independent event ID sequence")
    
    # Test 6: Profile name sanitization
    print("\n[TEST 6] Profile Name Sanitization")
    print("-" * 60)
    service_special = SCTE35Service(profile_name="Test Profile With Spaces & Special!@#")
    print(f"Original name: 'Test Profile With Spaces & Special!@#'")
    print(f"Directory: {service_special.markers_dir}")
    # Should sanitize to safe filesystem name
    assert " " not in str(service_special.markers_dir), "Spaces should be replaced"
    assert service_special.markers_dir.exists(), "Sanitized directory should exist"
    print("[PASS] Profile names are sanitized for filesystem")
    
    # Test 7: State file persistence
    print("\n[TEST 7] State File Persistence")
    print("-" * 60)
    test_profile = "Persistence_Test"
    service_persist = SCTE35Service(profile_name=test_profile)
    original_id = service_persist._last_event_id
    
    # Generate a marker to increment ID
    next_id = service_persist.get_next_event_id()
    service_persist._save_last_event_id(next_id)
    
    # Create new service instance (simulating app restart)
    service_persist2 = SCTE35Service(profile_name=test_profile)
    loaded_id = service_persist2._last_event_id
    
    print(f"Original ID: {original_id}")
    print(f"Saved ID: {next_id}")
    print(f"Loaded ID: {loaded_id}")
    assert loaded_id == next_id, "State should persist across instances"
    print("[PASS] Event ID state persists correctly")
    
    print("\n" + "=" * 60)
    print("[SUCCESS] ALL TESTS PASSED!")
    print("=" * 60)
    print("\nSummary:")
    print("  [OK] Default profile uses scte35_final/")
    print("  [OK] Named profiles use scte35_final/{profile_name}/")
    print("  [OK] Each profile has independent event ID sequence")
    print("  [OK] Profile switching works correctly")
    print("  [OK] Profile names are sanitized for filesystem")
    print("  [OK] Event ID state persists per profile")
    print("\nProfile-specific SCTE-35 directories are working correctly!")

if __name__ == "__main__":
    try:
        test_profile_specific_directories()
    except Exception as e:
        print(f"\n[FAILED] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

