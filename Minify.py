import sublime, sublime_plugin, re, os, subprocess

DEBUG = True

if DEBUG:
	print('Sublime Platform: ' + str(sublime.platform()))
	print('Sublime Version: ' + str(sublime.version()))

# find out this plugin's directory
if int(sublime.version()) >= 3000:
	PLUGIN_DIR = os.path.dirname(__file__)
else:
	PLUGIN_DIR = os.getcwd()
if DEBUG:
	print('PLUGIN_DIR: ' + str(PLUGIN_DIR))

# on Windows platform run the commands in shell
RUN_CMD_IN_SHELL = sublime.platform() == 'windows'
if DEBUG:
	print('RUN_CMD_IN_SHELL: ' + str(RUN_CMD_IN_SHELL))

# if there is no sublime.set_timeout_async method available then run the commands in a separate thread using the threading module
HAS_ASYNC_TIMEOUT = callable(getattr(sublime, 'set_timeout_async', None))
if DEBUG:
	print('HAS_ASYNC_TIMEOUT: ' + str(HAS_ASYNC_TIMEOUT))

if not HAS_ASYNC_TIMEOUT:
	import threading

	class RunCmdInOtherThread(threading.Thread):

		def __init__(self, cmdToRun):
			self.cmdToRun = cmdToRun
			self.result = 1
			threading.Thread.__init__(self)

		def run(self):
			self.result = subprocess.call(self.cmdToRun, shell=RUN_CMD_IN_SHELL)


class MinifyCommand(sublime_plugin.TextCommand):

	def is_enabled(self):
		filename = self.view.file_name()
		return bool(filename and (len(filename) > 0) and not (re.search('\.(?:js|css|svg)$', filename) is None))

	def handle_thread(self, thread, outfile):
		if thread.is_alive():
			sublime.set_timeout(lambda: self.handle_thread(thread, outfile), 100)
		else:
			if not thread.result:
				sublime.active_window().open_file(outfile)

	def doit(self):
		inpfile = self.view.file_name()
		if inpfile and (len(inpfile) > 0):
			if sublime.load_settings('Minify.sublime-settings').get('save_first') and self.view.is_dirty():
				self.view.run_command('save')
			if not (re.search('\.js$', inpfile) is None):
				outfile = re.sub(r'(\.js)$', r'.min\1', inpfile, 1)
				cmd = sublime.load_settings('Minify.sublime-settings').get('uglifyjs_command') or 'uglifyjs';
				cmdToRun = [cmd, inpfile, '-c', '-m']
				if sublime.load_settings('Minify.sublime-settings').get('keep_comments'):
					cmdToRun.extend(['--comments'])
					comments = sublime.load_settings('Minify.sublime-settings').get('comments_to_keep')
					if comments:
						cmdToRun.extend([str(comments)])
				cmdToRun.extend(['-o', outfile])
			elif not (re.search('\.css$', inpfile) is None):
				outfile = re.sub(r'(\.css)$', r'.min\1', inpfile, 1)
				cmd = sublime.load_settings('Minify.sublime-settings').get('java_command') or 'java';
				cmdToRun = [cmd, '-jar', PLUGIN_DIR + '/bin/' + str(sublime.load_settings('Minify.sublime-settings').get('yui_compressor')), inpfile, '-o', outfile]
				cs = sublime.load_settings('Minify.sublime-settings').get('yui_charset')
				if cs:
					cmdToRun.extend(['--charset', str(cs)])
				lb = sublime.load_settings('Minify.sublime-settings').get('yui_line_break')
				if not (type(lb) is bool):
					cmdToRun.extend(['--line-break', str(lb)])
			elif not (re.search('\.svg$', inpfile) is None):
				outfile = re.sub(r'(\.svg)$', r'.min\1', inpfile, 1)
				cmd = sublime.load_settings('Minify.sublime-settings').get('svgo_command') or 'svgo';
				cmdToRun = [cmd]
				if sublime.load_settings('Minify.sublime-settings').get('svgo_min_options'):
					svgo_options = sublime.load_settings('Minify.sublime-settings').get('svgo_min_options')
					if svgo_options:
						cmdToRun.extend([str(svgo_options)])
				cmdToRun.extend([inpfile, outfile])
			else:
				cmdToRun = False
			if cmdToRun:
				print('Minifying file ' + str(inpfile))
				if DEBUG:
					print('Output file ' + str(outfile))
					print('cmdToRun: ' + str(cmdToRun))
				if HAS_ASYNC_TIMEOUT:
					result = subprocess.call(cmdToRun, shell=RUN_CMD_IN_SHELL)
					if not result:
						sublime.active_window().open_file(outfile)
				else:
					thread = RunCmdInOtherThread(cmdToRun)
					thread.start()
					sublime.set_timeout(lambda: self.handle_thread(thread, outfile), 100)

	def run(self, edit):
		if HAS_ASYNC_TIMEOUT:
			sublime.set_timeout_async(lambda: self.doit(), 0)
		else:
			self.doit()


class BeautifyCommand(sublime_plugin.TextCommand):

	def is_enabled(self):
		# First, is this actually a file on the file system?
		filename = self.view.file_name()
		return bool(filename and (len(filename) > 0) and not (re.search('\.(?:js|css|svg)$', filename) is None))

	def handle_thread(self, thread, outfile):
		if thread.is_alive():
			sublime.set_timeout(lambda: self.handle_thread(thread, outfile), 100)
		else:
			if not thread.result:
				sublime.active_window().open_file(outfile)

	def doit(self):
		inpfile = self.view.file_name()
		if inpfile and (len(inpfile) > 0):
			if sublime.load_settings('Minify.sublime-settings').get('save_first') and self.view.is_dirty():
				self.view.run_command('save')
			if not (re.search('\.js$', inpfile) is None):
				outfile = re.sub(r'(?:\.min)?(\.js)$', r'.beautified\1', inpfile, 1)
				cmd = sublime.load_settings('Minify.sublime-settings').get('uglifyjs_command') or 'uglifyjs';
				cmdToRun = [cmd, inpfile, '-b', '-o', outfile, '--comments', 'all']
			elif not (re.search('\.css$', inpfile) is None):
				outfile = re.sub(r'(?:\.min)?(\.css)$', r'.beautified\1', inpfile, 1)
				cmd = sublime.load_settings('Minify.sublime-settings').get('js-beautify_command') or 'js-beautify';
				cmdToRun = [cmd]
				bo = sublime.load_settings('Minify.sublime-settings').get('js-beautify_options')
				if bo:
					cmdToRun.extend([str(bo)])
				cmdToRun.extend([inpfile, '-o', outfile])
			elif not (re.search('\.svg$', inpfile) is None):
				outfile = re.sub(r'(?:\.min)?(\.svg)$', r'.pretty\1', inpfile, 1)
				cmd = sublime.load_settings('Minify.sublime-settings').get('svgo_command') or 'svgo';
				cmdToRun = [cmd, '--pretty']
				if sublime.load_settings('Minify.sublime-settings').get('svgo_pretty_options'):
					svgo_options = sublime.load_settings('Minify.sublime-settings').get('svgo_pretty_options')
					if svgo_options:
						cmdToRun.extend([str(svgo_options)])
				cmdToRun.extend([inpfile, outfile])
			if cmdToRun:
				print('Beautifying file ' + str(inpfile))
				if DEBUG:
					print('Output file ' + str(outfile))
					print('cmdToRun: ' + str(cmdToRun))
				if HAS_ASYNC_TIMEOUT:
					result = subprocess.call(cmdToRun, shell=RUN_CMD_IN_SHELL)
					if not result:
						sublime.active_window().open_file(outfile)
				else:
					thread = RunCmdInOtherThread(cmdToRun)
					thread.start()
					sublime.set_timeout(lambda: self.handle_thread(thread, outfile), 100)

	def run(self, edit):
		if HAS_ASYNC_TIMEOUT:
			sublime.set_timeout_async(lambda: self.doit(), 0)
		else:
			self.doit()
