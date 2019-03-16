import sublime, sublime_plugin, re, os, subprocess, platform, ntpath, shlex

PLUGIN_DIR = os.getcwd() if int(sublime.version()) < 3000 else os.path.dirname(__file__)
SUBL_ASYNC = callable(getattr(sublime, 'set_timeout_async', None))
USE_SHELL = sublime.platform() == 'windows'
POPEN_ENV = ({'PATH': ':'.join(['/usr/local/bin', os.environ['PATH']])}) if sublime.platform() == 'osx' and os.path.isdir('/usr/local/bin') else None

if sublime.load_settings('Minify.sublime-settings').get('debug_mode'):
	print('Minify: Sublime Platform:' + str(sublime.platform()))
	print('Minify: Sublime Version:' + str(sublime.version()))
	print('Minify: Python Version:' + str(platform.python_version()))
	print('Minify: PLUGIN_DIR:' + str(PLUGIN_DIR))
	print('Minify: SUBL_ASYNC:' + str(SUBL_ASYNC))
	print('Minify: USE_SHELL:' + str(USE_SHELL))
	print('Minify: POPEN_ENV:' + str(POPEN_ENV))

class MinifyUtils():
	def fixStr(self, s):
		return s.encode('utf8') if (type(s).__name__ == 'unicode') else s

	def quoteChrs(self, s):
		return s.replace("(", "^^(").replace(")", "^^)") if USE_SHELL else s

	def runProgram(self, cmd, cwd = False):
		if '>' in cmd:
			p = subprocess.Popen(cmd, stderr=subprocess.PIPE, shell=USE_SHELL, env=POPEN_ENV)
			output = p.communicate()[1]
		else:
			if cwd:
				p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=USE_SHELL, env=POPEN_ENV, cwd=cwd)
			else:
				p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=USE_SHELL, env=POPEN_ENV)
			output = p.communicate()[0]
		return p.returncode, output

	def get_setting(self, key):
		settings = self.view.settings().get('Minify')
		if settings is None or settings.get(key) is None:
			settings = sublime.load_settings('Minify.sublime-settings')
		return settings.get(key)

if not SUBL_ASYNC:
	import threading

	class RunCmdInOtherThread(MinifyUtils, threading.Thread):
		def __init__(self, cmd, cwd = False):
			self.cmd = cmd
			self.retCode = 1
			self.output = ''
			self.cwd = cwd;
			threading.Thread.__init__(self)

		def run(self):
			if not SUBL_ASYNC and self.cwd:
					old_cwd = os.getcwd()
					os.chdir(self.cwd)
			self.retCode, self.output = self.runProgram(self.cmd)
			if not SUBL_ASYNC and self.cwd:
					os.chdir(old_cwd)

class ThreadHandling(MinifyUtils):
	def handle_result(self, cmd, outfile, retCode, output):
		if retCode:
			if output:
				sublime.error_message(' '.join(cmd) + '\r\n\r\n' + output.decode('utf-8'))
		else:
			if self.get_setting('open_file'):
				sublime.active_window().open_file(outfile)

	def handle_thread(self, thread, outfile):
		if thread.is_alive():
			sublime.set_timeout(lambda: self.handle_thread(thread, outfile), 100)
		else:
			self.handle_result(thread.cmd, outfile, thread.retCode, thread.output)

	def run_cmd(self, cmd, outfile, cwd=False):
		if self.get_setting('debug_mode'):
			print('Minify: Output file:' + str(outfile))
			print('Minify: Command:' + str(cmd))
		if SUBL_ASYNC:
			retCode, output = self.runProgram(cmd, cwd)
			self.handle_result(cmd, outfile, retCode, output)
		else:
			thread = RunCmdInOtherThread(cmd, cwd)
			thread.start()
			sublime.set_timeout(lambda: self.handle_thread(thread, outfile), 100)

class PluginBase(ThreadHandling):
	def is_enabled(self):
		filename = self.view.file_name()
		return bool(type(filename).__name__ in ('str', 'unicode') and ((re.search(r'\.(?:css|js|json|html?|svg)$', filename)) or (re.search(r'(\.[^\.]+)$', filename) and re.search(r'/(?:CSS|JavaScript|JSON|HTML)\.tmLanguage$', self.view.settings().get('syntax')))))

	def run(self, edit):
		if SUBL_ASYNC:
			sublime.set_timeout_async(lambda: self.do_action(), 0)
		else:
			self.do_action()

class MinifyClass(MinifyUtils):
	def minify(self):
		inpfile = self.view.file_name()
		cwd = False
		if type(inpfile).__name__ in ('str', 'unicode') and re.search(r'\.[^\.]+$', inpfile):
			if self.view.is_dirty() and self.get_setting('save_first'):
				self.view.run_command('save')
				if self.get_setting('auto_minify_on_save'):
					return
			outfile = re.sub(r'(\.[^\.]+)$', r'.min\1', inpfile, 1)
			syntax = self.view.settings().get('syntax')
			if self.get_setting('debug_mode'):
				print('Minify: Syntax: ' + str(syntax))
			if re.search(r'\.js$', inpfile) or re.search(r'/JavaScript\.tmLanguage$', syntax):
				cmd = self.fixStr(self.get_setting('uglifyjs_command') or 'uglifyjs').split()
				cmd.extend([self.quoteChrs(inpfile), '-o', self.quoteChrs(outfile), '-m', '-c'])
				eo = self.get_setting('uglifyjs_options')
				if type(eo).__name__ in ('str', 'unicode'):
					cmd.extend(self.fixStr(eo).split())
				if self.get_setting('source_map'):
					directory, rfile = ntpath.split(outfile)
					mapfile = rfile or ntpath.basename(directory)
					content = ''
					if self.get_setting('js_map_content'):
						content = ',content="' + (self.quoteChrs(inpfile + '.map') if os.path.isfile(inpfile + '.map') else 'inline') + '"'
					cmd.extend(['--source-map', "url='" + self.quoteChrs(mapfile) + ".map'" + content + ",root='',base='" + self.quoteChrs(directory) + "'"])
				if self.get_setting('keep_comments'):
					cmd.extend(['--comments'])
					eo = self.get_setting('comments_to_keep')
					if type(eo).__name__ in ('str', 'unicode'):
						cmd.extend([eo])
			elif re.search(r'\.json$', inpfile) or re.search(r'/JSON\.tmLanguage$', syntax):
				cmd = self.fixStr(self.get_setting('minjson_command') or 'minjson').split()
				cmd.extend([self.quoteChrs(inpfile), '-o', self.quoteChrs(outfile)])
			elif re.search(r'\.css$', inpfile) or re.search(r'/CSS\.tmLanguage$', syntax):
				minifier = self.get_setting('cssminifier') or 'clean-css'
				if minifier == 'uglifycss':
					cmd = self.fixStr(self.get_setting('uglifycss_command') or 'uglifycss').split()
					eo = self.get_setting('uglifycss_options')
					if type(eo).__name__ in ('str', 'unicode'):
						cmd.extend(self.fixStr(eo).split())
					cmd.extend([self.quoteChrs(inpfile), '>', self.quoteChrs(outfile)])
				elif minifier == 'yui':
					cmd = self.fixStr(self.get_setting('java_command') or 'java').split()
					yui_compressor = self.get_setting('yui_compressor') or 'yuicompressor-2.4.7.jar'
					cmd.extend(['-jar', PLUGIN_DIR + '/bin/' + str(yui_compressor), self.quoteChrs(inpfile), '-o', self.quoteChrs(outfile)])
					eo = self.get_setting('yui_charset')
					if type(eo).__name__ in ('str', 'unicode'):
						cmd.extend(['--charset', eo])
					eo = self.get_setting('yui_line_break')
					if type(eo).__name__ in ('int', 'str', 'unicode'):
						cmd.extend(['--line-break', str(eo)])
				else:
					cmd = self.fixStr(self.get_setting('cleancss_command') or 'cleancss').split()
					eo = self.get_setting('cleancss_options') or '-O2 --skip-rebase'
					if type(eo).__name__ in ('str', 'unicode'):
						cmd.extend(self.fixStr(eo).split())
					if self.get_setting('css_source_map'):
						cmd.extend(['--source-map'])
					cwd = os.path.dirname(outfile)
					cmd.extend(['-o', self.quoteChrs(outfile), self.quoteChrs(inpfile)])
			elif re.search(r'\.html?$', inpfile) or re.search(r'/HTML\.tmLanguage$', syntax):
				cmd = self.fixStr(self.get_setting('html-minifier_command') or 'html-minifier').split()
				eo = self.get_setting('html-minifier_options') or '--collapse-boolean-attributes --collapse-whitespace --html5 --minify-css --minify-js --preserve-line-breaks --process-conditional-comments --remove-comments --remove-empty-attributes --remove-redundant-attributes --remove-script-type-attributes --remove-style-link-type-attributes'
				if type(eo).__name__ in ('str', 'unicode'):
					cmd.extend(self.fixStr(eo).split())
				cmd.extend(['-o', self.quoteChrs(outfile), self.quoteChrs(inpfile)])
			elif re.search(r'\.svg$', inpfile):
				cmd = self.fixStr(self.get_setting('svgo_command') or 'svgo').split()
				eo = self.get_setting('svgo_min_options')
				if type(eo).__name__ in ('str', 'unicode'):
					cmd.extend(self.fixStr(eo).split())
				cmd.extend(['-i', self.quoteChrs(inpfile), '-o', self.quoteChrs(outfile)])
			else:
				cmd = False
			if cmd:
				print('Minify: Minifying file:' + str(inpfile))
				self.run_cmd(cmd, outfile, cwd)

class BeautifyClass(MinifyUtils):
	def beautify(self):
		inpfile = self.view.file_name()
		if type(inpfile).__name__ in ('str', 'unicode') and re.search(r'\.[^\.]+$', inpfile):
			if self.view.is_dirty() and self.get_setting('save_first'):
				self.view.run_command('save')
			outfile = re.sub(r'(?:\.min)?(\.[^\.]+)$', r'.beautified\1', inpfile, 1)
			syntax = self.view.settings().get('syntax')
			if re.search(r'\.js$', inpfile) or re.search(r'/JavaScript\.tmLanguage$', syntax):
				cmd = self.fixStr(self.get_setting('uglifyjs_command') or 'uglifyjs').split()
				cmd.extend([self.quoteChrs(inpfile), '-o', self.quoteChrs(outfile), '--comments', 'all', '-b'])
				eo = self.get_setting('uglifyjs_pretty_options')
				if type(eo).__name__ in ('str', 'unicode'):
					cmd.extend(self.fixStr(eo).split())
			elif re.search(r'\.json$', inpfile) or re.search(r'/JSON\.tmLanguage$', syntax):
				cmd = self.fixStr(self.get_setting('minjson_command') or 'minjson').split()
				cmd.extend([self.quoteChrs(inpfile), '-o', self.quoteChrs(outfile), '-b'])
			elif re.search(r'\.css$', inpfile) or re.search(r'/CSS\.tmLanguage$', syntax):
				cmd = self.fixStr(self.get_setting('js-beautify_command') or 'js-beautify').split()
				eo = self.get_setting('js-beautify_options')
				if type(eo).__name__ in ('str', 'unicode'):
					cmd.extend(self.fixStr(eo).split())
				cmd.extend(['--css', '-o', self.quoteChrs(outfile), self.quoteChrs(inpfile)])
			elif re.search(r'\.html?$', inpfile) or re.search(r'/HTML\.tmLanguage$', syntax):
				outfile = re.sub(r'(?:\.min)?(\.[^\.]+)$', r'.pretty\1', inpfile, 1)
				cmd = self.fixStr(self.get_setting('js-beautify_command') or 'js-beautify').split()
				eo = self.get_setting('js-beautify_html_options')
				if type(eo).__name__ in ('str', 'unicode'):
					cmd.extend(self.fixStr(eo).split())
				cmd.extend(['--html', '-o', self.quoteChrs(outfile), self.quoteChrs(inpfile)])
			elif re.search(r'\.svg$', inpfile):
				outfile = re.sub(r'(?:\.min)?(\.[^\.]+)$', r'.pretty\1', inpfile, 1)
				cmd = self.fixStr(self.get_setting('svgo_command') or 'svgo').split()
				eo = self.get_setting('svgo_pretty_options')
				if type(eo).__name__ in ('str', 'unicode'):
					cmd.extend(self.fixStr(eo).split())
				cmd.extend(['--pretty', '-i', self.quoteChrs(inpfile), '-o', self.quoteChrs(outfile)])
			if cmd:
				print('Minify: Beautifying file:' + str(inpfile))
				self.run_cmd(cmd, outfile)

class MinifyCommand(PluginBase, MinifyClass, sublime_plugin.TextCommand):
	def do_action(self):
		self.minify()

class BeautifyCommand(PluginBase, BeautifyClass, sublime_plugin.TextCommand):
	def do_action(self):
		self.beautify()

class RunAfterSave(ThreadHandling, MinifyClass, sublime_plugin.EventListener):
	def on_post_save(self, view):
		self.view = view
		if self.get_setting('auto_minify_on_save'):
			filename = self.view.file_name()
			syntax = self.view.settings().get('syntax')
			if type(filename).__name__ in ('str', 'unicode') and ((re.search(r'\.(?:css|js|json|html?|svg)$', filename)) or (re.search(r'(\.[^\.]+)$', filename) and re.search(r'/(?:CSS|JavaScript|JSON|HTML)\.tmLanguage$', syntax))):
				searchFName = ''
				searchSyntax = ''
				if 'css' in self.get_setting('allowed_file_types'):
					searchFName += 'css|'
					searchSyntax += 'CSS|'
				if 'js' in self.get_setting('allowed_file_types'):
					searchFName += 'js|'
					searchSyntax += 'JavaScript|'
				if 'json' in self.get_setting('allowed_file_types'):
					searchFName += 'json|'
					searchSyntax += 'JSON|'
				if 'html' in self.get_setting('allowed_file_types'):
					searchFName += 'html?|'
					searchSyntax += 'HTML|'
				if 'svg' in self.get_setting('allowed_file_types'):
					searchFName += 'svg|'
				searchFNameRegEx = r'\.(?:' + searchFName.rstrip('|') + ')$'
				searchSyntaxRegEx = r'/(?:' + searchSyntax.rstrip('|') + ')\.tmLanguage$'
				if re.search(searchFNameRegEx, filename) or (re.search(r'(\.[^\.]+)$', filename) and re.search(searchSyntaxRegEx, syntax)):
					if re.search(r'\.min\.[^\.]+$', filename):
						if self.get_setting('debug_mode'):
							print('Minify: Skipping file ' + filename + ' - already minified')
					else:
						if SUBL_ASYNC:
							sublime.set_timeout_async(lambda: self.minify(), 0)
						else:
							self.minify()
				else:
					if self.get_setting('debug_mode'):
						print('Minify: Skipping file ' + filename + ' - not in allowed_file_types')
