#!/usr/bin/env python3
"""
LegiSync Test Runner
Runs all test suites and generates a comprehensive report
"""
import sys
import subprocess
import os
from datetime import datetime

class TestRunner:
    """Comprehensive test runner for LegiSync"""
    
    def __init__(self):
        self.results = {
            'backend_unit': {'status': 'not_run', 'details': ''},
            'backend_integration': {'status': 'not_run', 'details': ''},
            'backend_openstates': {'status': 'not_run', 'details': ''},
            'frontend_unit': {'status': 'not_run', 'details': ''},
            'api_health': {'status': 'not_run', 'details': ''}
        }
    
    def run_backend_tests(self):
        """Run backend Python tests"""
        print("🔧 Running backend tests...")
        
        # Change to backend directory
        os.chdir('/Users/ccfegenbush/Documents/git/legisync/backend')
        
        try:
            # Run pytest for unit tests
            result = subprocess.run(
                ['python', '-m', 'pytest', 'tests/', '-v', '--tb=short'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                self.results['backend_unit']['status'] = 'passed'
                self.results['backend_unit']['details'] = f"✅ All tests passed\n{result.stdout}"
            else:
                self.results['backend_unit']['status'] = 'failed'
                self.results['backend_unit']['details'] = f"❌ Tests failed\n{result.stderr}\n{result.stdout}"
                
        except subprocess.TimeoutExpired:
            self.results['backend_unit']['status'] = 'timeout'
            self.results['backend_unit']['details'] = '⏰ Tests timed out'
        except Exception as e:
            self.results['backend_unit']['status'] = 'error'
            self.results['backend_unit']['details'] = f'🚨 Error running tests: {e}'
    
    def run_integration_tests(self):
        """Run integration tests"""
        print("🔗 Running integration tests...")
        
        try:
            result = subprocess.run(
                ['python', 'test_integration.py'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.results['backend_integration']['status'] = 'passed'
                self.results['backend_integration']['details'] = f"✅ Integration tests passed\n{result.stdout}"
            else:
                self.results['backend_integration']['status'] = 'failed'
                self.results['backend_integration']['details'] = f"❌ Integration tests failed\n{result.stderr}\n{result.stdout}"
                
        except subprocess.TimeoutExpired:
            self.results['backend_integration']['status'] = 'timeout'
            self.results['backend_integration']['details'] = '⏰ Integration tests timed out'
        except Exception as e:
            self.results['backend_integration']['status'] = 'error'
            self.results['backend_integration']['details'] = f'🚨 Error: {e}'
    
    def run_openstates_tests(self):
        """Run OpenStates API tests"""
        print("🏛️ Running OpenStates API tests...")
        
        try:
            result = subprocess.run(
                ['python', 'test_openstates.py'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if "PASSED" in result.stdout and "FAILED" not in result.stdout:
                self.results['backend_openstates']['status'] = 'passed'
                self.results['backend_openstates']['details'] = f"✅ OpenStates tests passed\n{result.stdout}"
            else:
                self.results['backend_openstates']['status'] = 'failed'
                self.results['backend_openstates']['details'] = f"❌ OpenStates tests failed\n{result.stdout}\n{result.stderr}"
                
        except subprocess.TimeoutExpired:
            self.results['backend_openstates']['status'] = 'timeout'
            self.results['backend_openstates']['details'] = '⏰ OpenStates tests timed out'
        except Exception as e:
            self.results['backend_openstates']['status'] = 'error'
            self.results['backend_openstates']['details'] = f'🚨 Error: {e}'
    
    def run_frontend_tests(self):
        """Run frontend tests"""
        print("🎨 Running frontend tests...")
        
        # Change to frontend directory
        os.chdir('/Users/ccfegenbush/Documents/git/legisync/frontend')
        
        try:
            result = subprocess.run(
                ['npm', 'test', '--', '--passWithNoTests', '--watchAll=false'],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                self.results['frontend_unit']['status'] = 'passed'
                self.results['frontend_unit']['details'] = f"✅ Frontend tests passed\n{result.stdout}"
            else:
                self.results['frontend_unit']['status'] = 'failed'
                self.results['frontend_unit']['details'] = f"❌ Frontend tests failed\n{result.stderr}\n{result.stdout}"
                
        except subprocess.TimeoutExpired:
            self.results['frontend_unit']['status'] = 'timeout'
            self.results['frontend_unit']['details'] = '⏰ Frontend tests timed out'
        except Exception as e:
            self.results['frontend_unit']['status'] = 'error'
            self.results['frontend_unit']['details'] = f'🚨 Error: {e}'
    
    def test_api_health(self):
        """Test live API health"""
        print("🏥 Testing live API health...")
        
        try:
            import requests
            
            # Test local API if running
            try:
                response = requests.get('http://localhost:8000/health', timeout=5)
                if response.status_code == 200:
                    self.results['api_health']['status'] = 'passed'
                    self.results['api_health']['details'] = f"✅ Local API healthy: {response.json()}"
                else:
                    raise Exception(f"API returned {response.status_code}")
            except:
                # Test production API
                try:
                    response = requests.get('https://legisync.onrender.com/health', timeout=10)
                    if response.status_code == 200:
                        self.results['api_health']['status'] = 'passed'
                        self.results['api_health']['details'] = f"✅ Production API healthy: {response.json()}"
                    else:
                        self.results['api_health']['status'] = 'failed'
                        self.results['api_health']['details'] = f"❌ Production API returned {response.status_code}"
                except Exception as e:
                    self.results['api_health']['status'] = 'failed'
                    self.results['api_health']['details'] = f"❌ No API available: {e}"
                    
        except Exception as e:
            self.results['api_health']['status'] = 'error'
            self.results['api_health']['details'] = f'🚨 Error testing API: {e}'
    
    def generate_report(self):
        """Generate and display comprehensive test report"""
        print("\n" + "=" * 80)
        print("🧪 LegiSync Test Report")
        print("=" * 80)
        print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results.values() if r['status'] == 'passed')
        
        # Summary
        print(f"📊 Summary: {passed_tests}/{total_tests} test suites passed")
        print()
        
        # Detailed results
        status_icons = {
            'passed': '✅',
            'failed': '❌',
            'error': '🚨',
            'timeout': '⏰',
            'not_run': '⚪'
        }
        
        for test_name, result in self.results.items():
            icon = status_icons.get(result['status'], '❓')
            print(f"{icon} {test_name.replace('_', ' ').title()}: {result['status'].upper()}")
            if result['details'] and result['status'] != 'passed':
                # Show first few lines of details for failed tests
                lines = result['details'].split('\n')[:5]
                for line in lines:
                    if line.strip():
                        print(f"   {line}")
                print()
        
        print("=" * 80)
        
        # Overall status
        if passed_tests == total_tests:
            print("🎉 All test suites passed! LegiSync is healthy.")
            return True
        else:
            print(f"⚠️  {total_tests - passed_tests} test suite(s) failed. Review details above.")
            return False
    
    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting LegiSync Test Suite")
        print("=" * 50)
        
        # Run all test categories
        self.run_backend_tests()
        self.run_integration_tests()
        self.run_openstates_tests()
        self.run_frontend_tests()
        self.test_api_health()
        
        # Generate report
        success = self.generate_report()
        
        return success

def main():
    """Main test runner entry point"""
    runner = TestRunner()
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        
        if test_type == 'backend':
            runner.run_backend_tests()
            runner.run_integration_tests()
            runner.run_openstates_tests()
        elif test_type == 'frontend':
            runner.run_frontend_tests()
        elif test_type == 'api':
            runner.test_api_health()
        elif test_type == 'quick':
            runner.run_openstates_tests()
            runner.test_api_health()
        else:
            print(f"Unknown test type: {test_type}")
            print("Available options: backend, frontend, api, quick, or no argument for all")
            return False
    else:
        success = runner.run_all_tests()
        sys.exit(0 if success else 1)
    
    return runner.generate_report()

if __name__ == "__main__":
    main()
