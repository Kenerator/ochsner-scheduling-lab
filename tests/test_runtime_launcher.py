"""Installed launcher routing checks; fake transport never qualifies live access."""
import importlib
import io
import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / 'tools' / 'poc-runtime'
CANARY = 'launcher-test-canary'


class RuntimeLauncherTests(unittest.TestCase):
    def runtime(self):
        self.assertTrue((RUNTIME / 'launch.py').is_file(),
                        'Reviewed shared runtime must be installed before qualification')
        sys.path.insert(0, str(RUNTIME))
        self.addCleanup(lambda: sys.path.remove(str(RUNTIME)))
        return importlib.import_module('launch')

    def config(self):
        self.assertTrue((ROOT / 'poc-launch.json').is_file(),
                        'Lab model-first configuration is missing')
        return self.runtime().load_config(ROOT / 'poc-launch.json')

    def test_lab_configuration_retains_model_and_exact_credential_source(self):
        config = self.config()
        self.assertEqual('lab', config['adapter'])
        self.assertEqual('browser', config['default_interface'])
        self.assertEqual('[Env] OPENAI_API_KEY', config['credential']['item'])
        self.assertEqual('gpt-5.4-mini', config['model']['default'])
        self.assertEqual('OPENAI_MODEL', config['model']['environment'])

    def test_installed_runtime_is_bound_to_reviewed_manifest(self):
        import hashlib
        self.runtime()
        path = RUNTIME / 'export-manifest.json'
        self.assertTrue(path.is_file(), 'Reviewed export manifest is missing')
        manifest = json.loads(path.read_text())
        self.assertEqual('20e3dd56747797b35c082d109ac3bb0a7d7b1ebe', manifest['source_revision'])
        self.assertEqual('clean', manifest['source_worktree_state'])
        self.assertEqual(4, len(manifest['files']))
        for relative, digest in manifest['files'].items():
            self.assertEqual(digest, hashlib.sha256((ROOT / relative).read_bytes()).hexdigest())

    def test_default_browser_and_cli_construct_real_interpreter_with_fake_transport(self):
        runtime = self.runtime()
        config = self.config()
        from appointment_assistant import __main__ as cli, ui_adapter
        from appointment_assistant.openai_interpreter import OpenAIInterpreter
        for interface, constructor in [('browser', ui_adapter.create_session), ('cli', cli.create_session)]:
            for arguments, environment, expected in [([], {}, 'gpt-5.4-mini'),
                    ([], {'OPENAI_MODEL': 'environment-model'}, 'environment-model'),
                    (['--model', 'explicit-model'], {'OPENAI_MODEL': 'environment-model'}, 'explicit-model')]:
                with self.subTest(interface=interface, arguments=arguments):
                    request = runtime.resolve_request(config, ['--interface', interface] + arguments, environment)
                    with patch.dict(os.environ, environment, clear=True):
                        specs = importlib.import_module('adapters').process_specs(ROOT, config, request, key=CANARY)
                    model_spec = next(spec for spec in specs if spec.role == 'model')
                    self.assertEqual('openai', model_spec.environment['SCHEDULING_MODE'])
                    self.assertEqual(expected, model_spec.environment['OPENAI_MODEL'])
                    self.assertNotIn(CANARY, ' '.join(model_spec.argv))
                    if interface == 'cli':
                        self.assertEqual('openai', model_spec.argv[model_spec.argv.index('--mode') + 1])
                        self.assertEqual(expected, model_spec.argv[model_spec.argv.index('--model') + 1])
                        self.assertEqual(model_spec.environment['API_BASE'],
                                         model_spec.argv[model_spec.argv.index('--api-base') + 1])
                    else:
                        self.assertIn(str(ROOT / 'apps/lab.py'), model_spec.argv)
                        self.assertEqual('127.0.0.1', model_spec.argv[model_spec.argv.index('--host') + 1])
                    for spec in specs:
                        if spec.role != 'model':
                            self.assertNotIn('OPENAI_API_KEY', spec.environment)
                            self.assertNotIn('BW_SESSION', spec.environment)
                    captured = []
                    action = {'intent': 'provider_lookup', 'fields': dict.fromkeys(
                        ('phone', 'dob', 'zip_code', 'start_date', 'end_date', 'specialty', 'location')),
                        'option_ordinal': None}
                    response = {'status': 'completed', 'output': [{'type': 'message', 'role': 'assistant',
                        'content': [{'type': 'output_text', 'text': json.dumps(action)}]}]}
                    def fake_transport(http_request, timeout):
                        captured.append(json.loads(http_request.data))
                        return io.BytesIO(json.dumps(response).encode())
                    with patch.dict(os.environ, model_spec.environment, clear=True), patch(
                            'appointment_assistant.openai_interpreter.urlopen', fake_transport):
                        session = constructor('openai', model_spec.environment['API_BASE'], expected)
                        self.assertIsInstance(session.interpreter, OpenAIInterpreter)
                        session.interpreter.interpret('Find providers', {})
                    self.assertEqual(expected, captured[0]['model'])
                    self.assertFalse(captured[0]['store'])

    def test_explicit_rehearsal_ignores_inherited_key_and_model(self):
        runtime = self.runtime()
        config = self.config()
        from appointment_assistant.ui_adapter import create_session
        from appointment_assistant.interpretation import RehearsalInterpreter
        request = runtime.resolve_request(config, ['--offline'], {'OPENAI_MODEL': 'private-parent-model'})
        with patch.dict(os.environ, {'OPENAI_API_KEY': CANARY, 'BW_SESSION': 'fake-session'}, clear=True):
            specs = importlib.import_module('adapters').process_specs(ROOT, config, request)
        model = next(spec for spec in specs if spec.role == 'model')
        self.assertEqual('rehearsal', model.environment['SCHEDULING_MODE'])
        self.assertNotIn('OPENAI_API_KEY', model.environment)
        self.assertNotIn('OPENAI_MODEL', model.environment)
        self.assertTrue(all('BW_SESSION' not in spec.environment for spec in specs))
        session = create_session('rehearsal', model.environment['API_BASE'], 'gpt-5.4-mini')
        self.assertIsInstance(session.interpreter, RehearsalInterpreter)

    def test_invalid_model_and_ports_fail_without_fallback(self):
        runtime = self.runtime()
        config = self.config()
        for arguments in [['--model', ' '], ['--model', 'two\nlines'], ['--api-port', '1'],
                          ['--unlimited-today'], ['--unexpected']]:
            with self.subTest(arguments=arguments), self.assertRaises(runtime.LaunchError):
                runtime.resolve_request(config, arguments, {})

    def test_help_and_doctor_do_not_resolve_key_start_children_or_call_model(self):
        import contextlib
        import socket
        runtime = self.runtime()
        with socket.socket() as probe:
            probe.bind(('127.0.0.1', 0))
            port = probe.getsockname()[1]
        with patch('credentials.resolve_key', side_effect=AssertionError('vault accessed')), patch(
                'credentials.helper_executable', return_value='/fake-helper'), patch(
                'processes.run_owned', side_effect=AssertionError('child started')), patch(
                'appointment_assistant.openai_interpreter.urlopen', side_effect=AssertionError('network used')), \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(0, runtime.main(['--help']))
            self.assertEqual(0, runtime.main(['--config', str(ROOT / 'poc-launch.json'),
                '--doctor', '--interface', 'cli', '--api-port', str(port)]))

    def test_foreign_listener_is_preserved_on_port_conflict(self):
        import socket
        runtime = self.runtime()
        config = self.config()
        with socket.socket() as listener:
            listener.bind(('127.0.0.1', 0))
            listener.listen()
            port = listener.getsockname()[1]
            request = runtime.resolve_request(config, ['--interface', 'cli', '--api-port', str(port)], {})
            with self.assertRaises(runtime.LaunchError):
                importlib.import_module('adapters').preflight(ROOT, config, request)
            with socket.create_connection(('127.0.0.1', port), timeout=1):
                self.assertEqual(port, listener.getsockname()[1])

    def test_owned_offline_cli_uses_real_mock_and_exits_on_eof(self):
        import socket
        import subprocess
        with socket.socket() as probe:
            probe.bind(('127.0.0.1', 0))
            port = probe.getsockname()[1]
        environment = dict(os.environ, OPENAI_API_KEY=CANARY, BW_SESSION='fake-session')
        completed = subprocess.run([sys.executable, str(RUNTIME / 'launch.py'), '--offline',
            '--interface', 'cli', '--api-port', str(port)], cwd=ROOT, env=environment,
            input='Which primary care providers are downtown?\n', text=True,
            capture_output=True, timeout=25)
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIn('DETERMINISTIC REHEARSAL', completed.stdout)
        self.assertIn('primary_care', completed.stdout)
        self.assertNotIn(CANARY, completed.stdout + completed.stderr)
        with socket.socket() as probe:
            self.assertNotEqual(0, probe.connect_ex(('127.0.0.1', port)))

    def test_explicit_own_key_binding_never_uses_inherited_or_ochsner_item(self):
        import subprocess
        self.runtime()
        credentials = importlib.import_module('credentials')
        config = json.loads((ROOT / 'poc-launch.json').read_text())
        calls = []
        def fake_helper(argv, **kwargs):
            calls.append((argv, kwargs['env']))
            return subprocess.CompletedProcess(argv, 0, stdout=CANARY, stderr='')
        with patch.dict(os.environ, {'OPENAI_API_KEY': CANARY + '-inherited',
                                     'BW_SESSION': 'fake-session'}, clear=True), patch(
                'credentials.helper_executable', return_value='/fake/trusted-helper'):
            result = credentials.resolve_key(config['credential'], run=fake_helper)
        self.assertEqual(CANARY, result)
        self.assertEqual(1, len(calls))
        self.assertEqual(['/fake/trusted-helper', '[Env] OPENAI_API_KEY', 'notes'], calls[0][0])
        self.assertNotIn('OPENAI_API_KEY', calls[0][1])
        self.assertNotIn('BW_SESSION', calls[0][1])
