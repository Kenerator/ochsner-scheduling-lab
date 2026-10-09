"""Reviewer commands must run real supplied mock state, not hidden intake paths."""
import json,os,subprocess,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class CLITests(unittest.TestCase):
    def run_cli(self,*args):
        return subprocess.run([sys.executable,'-m','appointment_assistant',*args],cwd=ROOT,env={**os.environ,'PYTHONPATH':str(ROOT/'src')},capture_output=True,text=True,timeout=40)
    def test_rehearsal_happy_and_failure_demos_reset_state(self):
        for scenario,want in [('happy_path_booking','completed'),('no_patient_match','completed'),('api_failure','rejected')]:
            with self.subTest(scenario=scenario):
                run=self.run_cli('--mode','rehearsal','--demo',scenario,'--json-summary')
                self.assertEqual(run.returncode,0,run.stderr)
                result=json.loads(run.stdout);self.assertEqual(result['outcome'],want)
                self.assertEqual(result['mode'],'rehearsal');self.assertTrue(result['isolated_reference'])
                self.assertNotIn('555-',run.stdout)
    def test_live_missing_key_is_actionable_without_fallback(self):
        env={**os.environ,'PYTHONPATH':str(ROOT/'src')};env.pop('OPENAI_API_KEY',None)
        run=subprocess.run([sys.executable,'-m','appointment_assistant','--mode','openai','--demo','provider_lookup','--json-summary'],cwd=ROOT,env=env,capture_output=True,text=True,timeout=40)
        self.assertNotEqual(run.returncode,0);self.assertIn('OPENAI_API_KEY',run.stderr)
        self.assertNotIn('rehearsal',run.stdout)
    def test_success_and_failure_aliases(self):
        for scenario in ['success','failure']:
            run=self.run_cli('--mode','rehearsal','--scenario',scenario,'--json-summary')
            self.assertEqual(run.returncode,0,run.stderr)

if __name__=='__main__':unittest.main()
