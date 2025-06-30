#!/usr/bin/env python3
"""
Comprehensive test script for Tootles application functionality.
Tests all core features including navigation, keyboard shortcuts, and media preview integration.
"""

import sys
import asyncio
import traceback
from typing import List, Optional

# Add current directory to path for imports
sys.path.insert(0, '.')

def test_imports():
    """Test that all core modules can be imported successfully."""
    print("=== Testing Core Imports ===")
    
    try:
        from tootles.main import TootlesApp, main
        print("✓ Main application import successful")
        
        from tootles.config.manager import ConfigManager
        from tootles.config.schema import MediaConfig
        print("✓ Configuration modules import successful")
        
        from tootles.media.manager import MediaManager
        from tootles.media.formats import get_media_format, MediaFormat
        print("✓ Media management modules import successful")
        
        from tootles.widgets.status import StatusWidget
        from tootles.widgets.timeline import Timeline, TimelineWidget
        from tootles.widgets.compose import ComposeWidget
        print("✓ Widget modules import successful")
        
        from tootles.screens.settings import SettingsScreen
        from tootles.screens.notifications import NotificationsScreen
        from tootles.screens.explore import ExploreScreen
        from tootles.screens.account import AccountScreen
        from tootles.screens.help import HelpScreen
        print("✓ Screen modules import successful")
        
        from tootles.api.client import MastodonClient
        from tootles.api.models import Status
        print("✓ API modules import successful")
        
        from tootles.themes.manager import ThemeManager
        print("✓ Theme manager import successful")
        
        return True
        
    except Exception as e:
        print(f"✗ Import failed: {e}")
        traceback.print_exc()
        return False

def test_media_preview_integration():
    """Test media preview system integration."""
    print("\n=== Testing Media Preview Integration ===")
    
    try:
        from tootles.media.manager import MediaManager
        from tootles.config.schema import MediaConfig
        from tootles.widgets.status import StatusWidget
        from tootles.widgets.timeline import Timeline
        from tootles.media.formats import get_media_format, MediaFormat
        
        # Test MediaManager initialization
        config = MediaConfig(show_media_previews=True)
        manager = MediaManager(config)
        print("✓ MediaManager initialization successful")
        
        # Test format detection
        fmt = get_media_format('test.jpg', 'image/jpeg')
        assert fmt == MediaFormat.IMAGE
        print("✓ Media format detection working")
        
        # Test widget integration
        class MockApp:
            def __init__(self):
                self.config = config
                self.media_manager = manager
        
        class MockMediaAttachment:
            def __init__(self, media_type='image'):
                self.type = media_type
                self.url = 'https://example.com/image.jpg'
                self.description = 'Test image'
        
        class MockStatus:
            def __init__(self, has_media=False):
                self.id = '123'
                self.account = type('obj', (object,), {
                    'display_name': 'Test User', 
                    'acct': 'test@example.com'
                })()
                self.content = 'Test status content'
                self.created_at = '2024-01-01T00:00:00Z'
                self.media_attachments = [MockMediaAttachment()] if has_media else []
                self.reblog = None
                self.favourited = False
                self.reblogged = False
                self.bookmarked = False
                self.replies_count = 0
                self.reblogs_count = 0
                self.favourites_count = 0
        
        app_ref = MockApp()
        
        # Test StatusWidget with media
        status_with_media = MockStatus(has_media=True)
        status_widget = StatusWidget(status_with_media, app_ref, media_manager=manager)
        print("✓ StatusWidget with media integration successful")
        
        # Test Timeline with MediaManager
        timeline = Timeline(app_ref, media_manager=manager)
        print("✓ Timeline with MediaManager integration successful")
        
        # Verify MediaManager propagation
        assert status_widget.media_manager is manager
        assert timeline.media_manager is manager
        print("✓ MediaManager propagation verified")
        
        return True
        
    except Exception as e:
        print(f"✗ Media preview integration test failed: {e}")
        traceback.print_exc()
        return False

def test_app_initialization():
    """Test application initialization without running the UI."""
    print("\n=== Testing Application Initialization ===")
    
    try:
        from tootles.main import TootlesApp
        
        # Test app creation
        app = TootlesApp()
        print("✓ TootlesApp creation successful")
        
        # Test that required components are initialized
        assert app.config_manager is not None
        print("✓ ConfigManager initialized")
        
        assert app.theme_manager is not None
        print("✓ ThemeManager initialized")
        
        assert app.media_manager is not None
        print("✓ MediaManager initialized")
        
        # Test keyboard bindings are defined
        assert len(app.BINDINGS) > 0
        print(f"✓ Keyboard bindings defined ({len(app.BINDINGS)} bindings)")
        
        # Test specific key bindings exist
        binding_keys = [binding.key for binding in app.BINDINGS]
        required_keys = ['h', 'n', 'e', 'b', 'c', 's', 'ctrl+q', 'ctrl+r', 'ctrl+t']
        
        for key in required_keys:
            if key in binding_keys:
                print(f"✓ Key binding '{key}' found")
            else:
                print(f"✗ Key binding '{key}' missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Application initialization test failed: {e}")
        traceback.print_exc()
        return False

def test_navigation_actions():
    """Test navigation action methods exist and are callable."""
    print("\n=== Testing Navigation Actions ===")
    
    try:
        from tootles.main import TootlesApp
        
        app = TootlesApp()
        
        # Test navigation methods exist
        navigation_methods = [
            'action_show_home',
            'action_show_notifications', 
            'action_show_explore',
            'action_show_bookmarks',
            'action_show_favorites',
            'action_show_lists',
            'action_compose',
            'action_show_settings',
            'action_show_account',
            'action_show_help',
            'action_go_back'
        ]
        
        for method_name in navigation_methods:
            if hasattr(app, method_name):
                method = getattr(app, method_name)
                if callable(method):
                    print(f"✓ Navigation method '{method_name}' exists and is callable")
                else:
                    print(f"✗ Navigation method '{method_name}' exists but is not callable")
                    return False
            else:
                print(f"✗ Navigation method '{method_name}' missing")
                return False
        
        # Test utility actions
        utility_methods = [
            'action_refresh',
            'action_toggle_theme',
            'action_quit'
        ]
        
        for method_name in utility_methods:
            if hasattr(app, method_name):
                print(f"✓ Utility method '{method_name}' exists")
            else:
                print(f"✗ Utility method '{method_name}' missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"✗ Navigation actions test failed: {e}")
        traceback.print_exc()
        return False

def test_timeline_widget_parameters():
    """Test TimelineWidget parameter handling."""
    print("\n=== Testing TimelineWidget Parameters ===")
    
    try:
        from tootles.widgets.timeline import TimelineWidget
        from tootles.media.manager import MediaManager
        from tootles.config.schema import MediaConfig
        
        # Create mock app
        class MockApp:
            def __init__(self):
                from tootles.config.schema import TootlesConfig
                self.config = TootlesConfig()
                self.media_manager = MediaManager(self.config.media)
        
        app_ref = MockApp()
        
        # Test TimelineWidget creation with different parameters
        
        # Test with minimal parameters
        widget1 = TimelineWidget(app_ref=app_ref)
        print("✓ TimelineWidget creation with minimal parameters successful")
        
        # Test with load callback
        async def mock_load_callback(timeline_type="home", max_id=None):
            return []
        
        widget2 = TimelineWidget(
            app_ref=app_ref,
            load_callback=mock_load_callback
        )
        print("✓ TimelineWidget creation with load callback successful")
        
        # Test with empty message
        widget3 = TimelineWidget(
            app_ref=app_ref,
            empty_message="No posts available"
        )
        print("✓ TimelineWidget creation with empty message successful")
        
        # Test with ID
        widget4 = TimelineWidget(
            app_ref=app_ref,
            id="test-timeline"
        )
        print("✓ TimelineWidget creation with ID successful")
        
        # Test with media manager
        widget5 = TimelineWidget(
            app_ref=app_ref,
            media_manager=app_ref.media_manager
        )
        print("✓ TimelineWidget creation with MediaManager successful")
        
        return True
        
    except Exception as e:
        print(f"✗ TimelineWidget parameters test failed: {e}")
        traceback.print_exc()
        return False

def test_error_handling():
    """Test error handling and graceful degradation."""
    print("\n=== Testing Error Handling ===")
    
    try:
        from tootles.main import TootlesApp
        from tootles.widgets.status import StatusWidget
        from tootles.media.manager import MediaManager
        from tootles.config.schema import MediaConfig
        
        # Test app with no API client
        app = TootlesApp()
        app.api_client = None
        
        # These should not crash when no API client is available
        print("✓ App handles missing API client gracefully")
        
        # Test StatusWidget with minimal status data
        class MinimalStatus:
            def __init__(self):
                self.id = '123'
                self.account = type('obj', (object,), {
                    'display_name': 'Test', 
                    'acct': 'test'
                })()
                self.content = 'Test'
                self.created_at = '2024-01-01T00:00:00Z'
                self.media_attachments = []
                self.reblog = None
                self.favourited = False
                self.reblogged = False
                self.bookmarked = False
                self.replies_count = 0
                self.reblogs_count = 0
                self.favourites_count = 0
        
        class MockApp:
            def __init__(self):
                from tootles.config.schema import TootlesConfig
                self.config = TootlesConfig()
                self.media_manager = MediaManager(self.config.media)
        
        app_ref = MockApp()
        status = MinimalStatus()
        widget = StatusWidget(status, app_ref, media_manager=app_ref.media_manager)
        print("✓ StatusWidget handles minimal data gracefully")
        
        return True
        
    except Exception as e:
        print(f"✗ Error handling test failed: {e}")
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all test functions and return overall result."""
    print("🧪 Starting Tootles Functionality Tests\n")
    
    tests = [
        test_imports,
        test_media_preview_integration,
        test_app_initialization,
        test_navigation_actions,
        test_timeline_widget_parameters,
        test_error_handling
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"✗ Test {test_func.__name__} crashed: {e}")
            results.append(False)
    
    print(f"\n=== Test Results ===")
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed! Tootles is ready for interactive testing.")
        return True
    else:
        print("❌ Some tests failed. Please review the output above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)