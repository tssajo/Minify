import sublime, sublime_plugin, re, os, subprocess, platform, ntpath, shlex

PLUGIN_DIR = os.getcwd() if int(sublime.version()) < 3000 else os.path.dirname(__file__)
# on Windows platform run the commands in a shell
RUN_IN_SHELL = sublime.platform() == 'windows'
# if there is no sublime.set_timeout_async method available then run the commands in a separate thread using the threading module
HAS_ASYNC = callable(getattr(sublime, 'set_timeout_async', None))

if sublime.load_settings('Minify.sublime-settings').get('debug_mode'):
	print('Minify: Sublime Platform: ' + str(sublime.platform()))
	print('Minify: Sublime Version: ' + str(sublime.version()))
	print('Minify: Python Version: ' + platform.python_version())
	print('Minify: PLUGIN_DIR: ' + str(PLUGIN_DIR))
	print('Minify: RUN_IN_SHELL: ' + str(RUN_IN_SHELL))
	print('Minify: Sublime Text HAS_ASYNC: ' + str(HAS_ASYNC))

class MinifyUtils():
	def fixStr(self, s):
		return s.encode('utf8') if (type(s).__name__ == 'unicode') else s

	def runProgram(self, cmdToRun):
		if '>' in cmdToRun:
			p = subprocess.Popen(cmdToRun, stderr=subprocess.PIPE, shell=RUN_IN_SHELL)
			output = p.communicate()[1]
		else:
			p = subprocess.Popen(cmdToRun, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=RUN_IN_SHELL)
			output = p.communicate()[0]
		return p.returncode, output

if not HAS_ASYNC:
	import threading

	class RunCmdInOtherThread(MinifyUtils, threading.Thread):
		def __init__(self, cmdToRun):
			self.cmdToRun = cmdToRun
			self.retCode = 1
			self.output = ''
			threading.Thread.__init__(self)

		def run(self):
			self.retCode, self.output = self.runProgram(self.cmdToRun)

class ThreadHandling(MinifyUtils):
	def handle_result(self, cmdToRun, outfile, retCode, output):
		if retCode:
			if output:
				sublime.error_message(' '.join(cmdToRun) + '\r\n\r\n' + output.decode('utf-8'))
		else:
			if sublime.load_settings('Minify.sublime-settings').get('open_file'):
				sublime.active_window().open_file(outfile)

	def handle_thread(self, thread, outfile):
		if thread.is_alive():
			sublime.set_timeout(lambda: self.handle_thread(thread, outfile), 100)
		else:
			self.handle_result(thread.cmdToRun, outfile, thread.retCode, thread.output)

	def run_cmd(self, cmdToRun, outfile):
		if sublime.load_settings('Minify.sublime-settings').get('debug_mode'):
			print('Minify: Output file ' + str(outfile))
			print('Minify: cmdToRun: ' + str(cmdToRun))
		if HAS_ASYNC:
			retCode, output = self.runProgram(cmdToRun)
			self.handle_result(cmdToRun, outfile, retCode, output)
		else:
			thread = RunCmdInOtherThread(cmdToRun)
			thread.start()
			sublime.set_timeout(lambda: self.handle_thread(thread, outfile), 100)

class PluginBase(ThreadHandling):
	def is_enabled(self):
		filename = self.view.file_name()
		return bool(type(filename).__name__ in ('str', 'unicode') and (re.search(r'\.(?:css|js|html?|svg)$', filename) or re.search(r'(\.[^\.]+)$', filename) and re.search(r'/(?:CSS|JavaScript|HTML)\.tmLanguage$', self.view.settings().get('syntax'))))

	def run(self, edit):
		if HAS_ASYNC:
			sublime.set_timeout_async(lambda: self.do_action(), 0)
		else:
			self.do_action()

class MinifyClass(MinifyUtils):
	def minify(self, view):
		inpfile = view.file_name()
		if type(inpfile).__name__ in ('str', 'unicode') and re.search(r'\.[^\.]+$', inpfile):
			if view.is_dirty() and sublime.load_settings('Minify.sublime-settings').get('save_first'):
				view.run_command('save')
				if sublime.load_settings('Minify.sublime-settings').get('auto_minify_on_save'):
					return
			outfile = re.sub(r'(\.[^\.]+)$', r'.min\1', inpfile, 1)
			syntax = view.settings().get('syntax')
			if re.search(r'\.js$', inpfile) or re.search(r'/JavaScript\.tmLanguage$', syntax):
				cmdToRun = shlex.split(self.fixStr(sublime.load_settings('Minify.sublime-settings').get('uglifyjs_command') or 'uglifyjs'))
				cmdToRun.extend([inpfile, '-o', outfile, '-m', '-c'])
				if sublime.load_settings('Minify.sublime-settings').get('source_map'):
					head, tail = ntpath.split(outfile)
					mapfile = tail or ntpath.basename(head)
					cmdToRun.extend(['--source-map', outfile + '.map', '--source-map-url', mapfile + '.map', '--source-map-root', './', '-p', 'relative'])
				if sublime.load_settings('Minify.sublime-settings').get('keep_comments'):
					cmdToRun.extend(['--comments'])
					eo = sublime.load_settings('Minify.sublime-settings').get('comments_to_keep')
					if type(eo).__name__ in ('str', 'unicode'):
						cmdToRun.extend([eo])
			elif re.search(r'\.css$', inpfile) or re.search(r'/CSS\.tmLanguage$', syntax):
				minifier = sublime.load_settings('Minify.sublime-settings').get('cssminifier') or 'clean-css'
				if minifier == 'uglifycss':
					cmdToRun = shlex.split(self.fixStr(sublime.load_settings('Minify.sublime-settings').get('uglifycss_command') or 'uglifycss'))
					eo = sublime.load_settings('Minify.sublime-settings').get('uglifycss_options')
					if type(eo).__name__ in ('str', 'unicode'):
						cmdToRun.extend(shlex.split(self.fixStr(eo)))
					cmdToRun.extend([inpfile, '>', outfile])
				elif minifier == 'yui':
					cmdToRun = shlex.split(self.fixStr(sublime.load_settings('Minify.sublime-settings').get('java_command') or 'java'))
					yui_compressor = sublime.load_settings('Minify.sublime-settings').get('yui_compressor') or 'yuicompressor-2.4.7.jar'
					cmdToRun.extend(['-jar', PLUGIN_DIR + '/bin/' + str(yui_compressor), inpfile, '-o', outfile])
					eo = sublime.load_settings('Minify.sublime-settings').get('yui_charset')
					if type(eo).__name__ in ('str', 'unicode'):
						cmdToRun.extend(['--charset', eo])
					eo = sublime.load_settings('Minify.sublime-settings').get('yui_line_break')
					if type(eo).__name__ in ('int', 'str', 'unicode'):
						cmdToRun.extend(['--line-break', str(eo)])
				else:
					cmdToRun = shlex.split(self.fixStr(sublime.load_settings('Minify.sublime-settings').get('cleancss_command') or 'cleancss'))
					eo = sublime.load_settings('Minify.sublime-settings').get('cleancss_options') or '--s0 -s --skip-rebase'
					if type(eo).__name__ in ('str', 'unicode'):
						cmdToRun.extend(shlex.split(self.fixStr(eo)))
					if sublime.load_settings('Minify.sublime-settings').get('css_source_map'):
						cmdToRun.extend(['--source-map'])
					cmdToRun.extend(['-o', outfile, inpfile])
			elif re.search(r'\.html?$', inpfile) or re.search(r'/HTML\.tmLanguage$', syntax):
				cmdToRun = shlex.split(self.fixStr(sublime.load_settings('Minify.sublime-settings').get('html-minifier_command') or 'html-minifier'))
				eo = sublime.load_settings('Minify.sublime-settings').get('html-minifier_options') or '--remove-comments --remove-comments-from-cdata --collapse-whitespace --conservative-collapse --collapse-boolean-attributes --remove-redundant-attributes --remove-script-type-attributes --remove-style-link-type-attributes --minify-js --minify-css'
				if type(eo).__name__ in ('str', 'unicode'):
					cmdToRun.extend(shlex.split(self.fixStr(eo)))
				cmdToRun.extend(['-o', outfile, inpfile])
			elif re.search(r'\.svg$', inpfile):
				cmdToRun = shlex.split(self.fixStr(sublime.load_settings('Minify.sublime-settings').get('svgo_command') or 'svgo'))
				eo = sublime.load_settings('Minify.sublime-settings').get('svgo_min_options')
				if type(eo).__name__ in ('str', 'unicode'):
					cmdToRun.extend(shlex.split(self.fixStr(eo)))
				cmdToRun.extend([inpfile, outfile])
			else:
				cmdToRun = False
			if cmdToRun:
				print('Minify: Minifying file ' + inpfile)
				self.run_cmd(cmdToRun, outfile)

class BeautifyClass(MinifyUtils):
	def beautify(self, view):
		inpfile = view.file_name()
		if type(inpfile).__name__ in ('str', 'unicode') and re.search(r'\.[^\.]+$', inpfile):
			if sublime.load_settings('Minify.sublime-settings').get('save_first') and view.is_dirty():
				view.run_command('save')
			outfile = re.sub(r'(?:\.min)?(\.[^\.]+)$', r'.beautified\1', inpfile, 1)
			syntax = view.settings().get('syntax')
			if re.search(r'\.js$', inpfile) or re.search(r'/JavaScript\.tmLanguage$', syntax):
				cmdToRun = shlex.split(self.fixStr(sublime.load_settings('Minify.sublime-settings').get('uglifyjs_command') or 'uglifyjs'))
				cmdToRun.extend([inpfile, '-o', outfile, '--comments', 'all', '-b'])
				eo = sublime.load_settings('Minify.sublime-settings').get('uglifyjs_pretty_options')
				if type(eo).__name__ in ('str', 'unicode'):
					cmdToRun.extend(shlex.split(self.fixStr(eo)))
			elif re.search(r'\.css$', inpfile) or re.search(r'/CSS\.tmLanguage$', syntax):
				cmdToRun = shlex.split(self.fixStr(sublime.load_settings('Minify.sublime-settings').get('js-beautify_command') or 'js-beautify'))
				eo = sublime.load_settings('Minify.sublime-settings').get('js-beautify_options')
				if type(eo).__name__ in ('str', 'unicode'):
					cmdToRun.extend(shlex.split(self.fixStr(eo)))
				cmdToRun.extend(['--css', '-o', outfile, inpfile])
			elif re.search(r'\.html?$', inpfile) or re.search(r'/HTML\.tmLanguage$', syntax):
				outfile = re.sub(r'(?:\.min)?(\.[^\.]+)$', r'.pretty\1', inpfile, 1)
				cmdToRun = shlex.split(self.fixStr(sublime.load_settings('Minify.sublime-settings').get('js-beautify_command') or 'js-beautify'))
				eo = sublime.load_settings('Minify.sublime-settings').get('js-beautify_html_options')
				if type(eo).__name__ in ('str', 'unicode'):
					cmdToRun.extend(shlex.split(self.fixStr(eo)))
				cmdToRun.extend(['--html', '-o', outfile, inpfile])
			elif re.search(r'\.svg$', inpfile):
				outfile = re.sub(r'(?:\.min)?(\.[^\.]+)$', r'.pretty\1', inpfile, 1)
				cmdToRun = shlex.split(self.fixStr(sublime.load_settings('Minify.sublime-settings').get('svgo_command') or 'svgo'))
				eo = sublime.load_settings('Minify.sublime-settings').get('svgo_pretty_options')
				if type(eo).__name__ in ('str', 'unicode'):
					cmdToRun.extend(shlex.split(self.fixStr(eo)))
				cmdToRun.extend(['--pretty', inpfile, outfile])
			if cmdToRun:
				print('Minify: Beautifying file ' + inpfile)
				self.run_cmd(cmdToRun, outfile)

class MinifyCommand(PluginBase, MinifyClass, sublime_plugin.TextCommand):
	def do_action(self):
		self.minify(self.view)

class BeautifyCommand(PluginBase, BeautifyClass, sublime_plugin.TextCommand):
	def do_action(self):
		self.beautify(self.view)

class RunAfterSave(ThreadHandling, MinifyClass, sublime_plugin.EventListener):
	def on_post_save(self, view):
		if sublime.load_settings('Minify.sublime-settings').get('auto_minify_on_save'):
			self.minify(view)
