import sublime, sublime_plugin, re, os, subprocess, threading # threading is only needed for ST2

if (int(sublime.version()) >= 3000):
	PLUGIN_DIR = os.path.dirname(__file__)
else:
	PLUGIN_DIR = os.getcwd()

HAS_ASYNC_TIMEOUT = bool(hasattr(sublime.__class__, 'set_timeout_async') and callable(getattr(sublime.__class__, 'set_timeout_async')))

class MinifyCommand(sublime_plugin.TextCommand):

	def is_enabled(self):
		# First, is this actually a file on the file system?
		filename = self.view.file_name()
		return bool(filename and (len(filename) > 0) and not (re.search('\.(?:css|js)$', filename) is None))

	def handle_thread(self, thread, outfile):
		if (thread.is_alive()):
			sublime.set_timeout(lambda: self.handle_thread(thread, outfile), 100)
		else:
			if (not thread.result):
				sublime.active_window().open_file(outfile)

	def doit(self):
		inpfile = self.view.file_name()
		if (inpfile and (len(inpfile) > 0)):
			if (sublime.load_settings('Minify.sublime-settings').get('save_first') and self.view.is_dirty()):
				self.view.run_command('save')
			if (not (re.search('\.js$', inpfile) is None)):
				outfile = re.sub(r'(\.js)$', r'.min\1', inpfile, 1)
				cmd = sublime.load_settings('Minify.sublime-settings').get('uglifyjs_command') or 'uglifyjs';
				cmdToRun = [cmd, inpfile, '-c', '-m', '-o', outfile]
			elif (not (re.search('\.css$', inpfile) is None)):
				outfile = re.sub(r'(\.css)$', r'.min\1', inpfile, 1)
				cmd = sublime.load_settings('Minify.sublime-settings').get('java_command') or 'java';
				cmdToRun = [cmd, '-jar', PLUGIN_DIR + '/bin/yuicompressor-2.4.7.jar', inpfile, '-o', outfile, '--charset', 'utf-8', '--line-break', '250']
			else:
				cmdToRun = False
			if (cmdToRun):
				print('Minifying file ' + str(inpfile))
				if (HAS_ASYNC_TIMEOUT):
					result = subprocess.call(cmdToRun, shell=True)
					if (not result):
						sublime.active_window().open_file(outfile)
				else:
					thread = RunCmdInOtherThread(cmdToRun)
					thread.start()
					sublime.set_timeout(lambda: self.handle_thread(thread, outfile), 100)

	def run(self, edit):
		if (HAS_ASYNC_TIMEOUT):
			sublime.set_timeout_async(lambda: self.doit(), 0)
		else:
			self.doit()



class BeautifyCommand(sublime_plugin.TextCommand):

	def is_enabled(self):
		# First, is this actually a file on the file system?
		filename = self.view.file_name()
		return bool(filename and (len(filename) > 0) and not (re.search('\.js$', filename) is None))

	def handle_thread(self, thread, outfile):
		if (thread.is_alive()):
			sublime.set_timeout(lambda: self.handle_thread(thread, outfile), 100)
		else:
			if (not thread.result):
				sublime.active_window().open_file(outfile)

	def doit(self):
		inpfile = self.view.file_name()
		if (inpfile and (len(inpfile) > 0)):
			if (sublime.load_settings('Minify.sublime-settings').get('save_first') and self.view.is_dirty()):
				self.view.run_command('save')
			if (not (re.search('\.js$', inpfile) is None)):
				outfile = re.sub(r'(?:\.min)?(\.js)$', r'.beautified\1', inpfile, 1)
				cmd = sublime.load_settings('Minify.sublime-settings').get('uglifyjs_command') or 'uglifyjs';
				cmdToRun = [cmd, inpfile, '-b', '-o', outfile]
				print('Beautifying file ' + str(inpfile))
				if (HAS_ASYNC_TIMEOUT):
					result = subprocess.call(cmdToRun, shell=True)
					if (not result):
						sublime.active_window().open_file(outfile)
				else:
					thread = RunCmdInOtherThread(cmdToRun)
					thread.start()
					sublime.set_timeout(lambda: self.handle_thread(thread, outfile), 100)

	def run(self, edit):
		if (HAS_ASYNC_TIMEOUT):
			sublime.set_timeout_async(lambda: self.doit(), 0)
		else:
			self.doit()



# To run the shell command in a separate thread in ST2. This is not needed in ST3 because ST3 has the sublime.set_timeout_async method.
class RunCmdInOtherThread(threading.Thread):

	def __init__(self, cmdToRun):
		self.cmdToRun = cmdToRun
		self.result = 1
		threading.Thread.__init__(self)

	def run(self):
		self.result = subprocess.call(self.cmdToRun, shell=True)
