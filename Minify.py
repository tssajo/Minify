import sublime, sublime_plugin, re, os, subprocess

class MinifyCommand(sublime_plugin.TextCommand):

	def is_enabled(self):
		# First, is this actually a file on the file system?
		filename = self.view.file_name()
		return bool(filename and (len(filename) > 0) and not (re.search('\.(css|js)$', filename) is None))

	def run(self, edit):
		sublime.set_timeout_async(lambda: self.doit(), 0)

	def doit(self):
		inpfile = self.view.file_name()
		if (inpfile and (len(inpfile) > 0)):
			if (sublime.load_settings('Minify.sublime-settings').get('save_first') and self.view.is_dirty()):
				self.view.run_command('save')
			if (not (re.search('\.js$', inpfile) is None)):
				outfile = re.sub(r'(\.js)$', r'.min\1', inpfile, 1)
				cmd = sublime.load_settings('Minify.sublime-settings').get('uglifyjs_command') or 'uglifyjs';
				print('Minifying file ' + str(inpfile))
				result = subprocess.call([cmd, inpfile, '-c', '-m', '-o', outfile], shell=True)
			elif (not (re.search('\.css$', inpfile) is None)):
				outfile = re.sub(r'(\.css)$', r'.min\1', inpfile, 1)
				cmd = sublime.load_settings('Minify.sublime-settings').get('java_command') or 'java';
				print('Minifying file ' + str(inpfile))
				result = subprocess.call([cmd, '-jar', os.path.dirname(__file__) + '/bin/yuicompressor-2.4.7.jar', inpfile, '-o', outfile, '--charset', 'utf-8', '--line-break', '250'], shell=True)
			else:
				result = 0
			if (not result):
				sublime.active_window().open_file(outfile)

class BeautifyCommand(sublime_plugin.TextCommand):

	def is_enabled(self):
		# First, is this actually a file on the file system?
		filename = self.view.file_name()
		return bool(filename and (len(filename) > 0) and not (re.search('\.js$', filename) is None))

	def run(self, edit):
		sublime.set_timeout_async(lambda: self.doit(), 0)

	def doit(self):
		inpfile = self.view.file_name()
		if (inpfile and (len(inpfile) > 0)):
			if (sublime.load_settings('Minify.sublime-settings').get('save_first') and self.view.is_dirty()):
				self.view.run_command('save')
			if (not (re.search('\.js$', inpfile) is None)):
				outfile = re.sub(r'(?:\.min)?(\.js)$', r'.beautified\1', inpfile, 1)
				cmd = sublime.load_settings('Minify.sublime-settings').get('uglifyjs_command') or 'uglifyjs';
				print('Beautifying file ' + str(inpfile))
				result = subprocess.call([cmd, inpfile, '-b', '-o', outfile], shell=True)
			else:
				result = 0
			if (not result):
				sublime.active_window().open_file(outfile)
