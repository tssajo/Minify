import sublime, sublime_plugin, re, os, subprocess

PLUGIN_DIR = os.path.dirname(__file__) if int(sublime.version()) >= 3000 else os.getcwd()

# on Windows platform run the commands in a shell
RUN_IN_SHELL = sublime.platform() == 'windows'

# if there is no sublime.set_timeout_async method available then run the commands in a separate thread using the threading module
HAS_ASYNC = callable(getattr(sublime, 'set_timeout_async', None))

DEBUG = sublime.load_settings('Minify.sublime-settings').get('debug_mode')
if DEBUG:
	print('Minify: Sublime Platform: ' + str(sublime.platform()))
	print('Minify: Sublime Version: ' + str(sublime.version()))
	print('Minify: PLUGIN_DIR: ' + str(PLUGIN_DIR))
	print('Minify: RUN_IN_SHELL: ' + str(RUN_IN_SHELL))
	print('Minify: SublimeText HAS_ASYNC: ' + str(HAS_ASYNC))

if not HAS_ASYNC:
	import threading

	class RunCmdInOtherThread(threading.Thread):

		def __init__(self, cmdToRun):
			self.cmdToRun = cmdToRun
			self.result = 1
			threading.Thread.__init__(self)

		def run(self):
			self.result = subprocess.call(self.cmdToRun, shell=RUN_IN_SHELL)

class MinifyBase():

	def is_enabled(self):
		filename = self.view.file_name()
		return bool(filename and (len(filename) > 0) and not (re.search('\.(?:js|css|html?|svg)$', filename) is None))

	def handle_thread(self, thread, outfile):
		if thread.is_alive():
			sublime.set_timeout(lambda: self.handle_thread(thread, outfile), 100)
		else:
			if not thread.result:
				sublime.active_window().open_file(outfile)

	def run_cmd(self, cmdToRun, outfile):
		if DEBUG:
			print('Minify: Output file ' + str(outfile))
			print('Minify: cmdToRun: ' + str(cmdToRun))
		if HAS_ASYNC:
			result = subprocess.call(cmdToRun, shell=RUN_IN_SHELL)
			if not result:
				sublime.active_window().open_file(outfile)
		else:
			thread = RunCmdInOtherThread(cmdToRun)
			thread.start()
			sublime.set_timeout(lambda: self.handle_thread(thread, outfile), 100)

	def run(self, edit):
		if HAS_ASYNC:
			sublime.set_timeout_async(lambda: self.do_action(), 0)
		else:
			self.do_action()

class MinifyCommand(MinifyBase, sublime_plugin.TextCommand):

	def do_action(self):
		inpfile = self.view.file_name()
		if inpfile and (len(inpfile) > 0):
			if sublime.load_settings('Minify.sublime-settings').get('save_first') and self.view.is_dirty():
				self.view.run_command('save')
			if not (re.search('\.js$', inpfile) is None):
				outfile = re.sub(r'(\.js)$', r'.min\1', inpfile, 1)
				cmd = sublime.load_settings('Minify.sublime-settings').get('uglifyjs_command') or 'uglifyjs'
				cmdToRun = [cmd, inpfile, '-o', outfile, '-m', '-c']
				if sublime.load_settings('Minify.sublime-settings').get('keep_comments'):
					cmdToRun.extend(['--comments'])
					eo = sublime.load_settings('Minify.sublime-settings').get('comments_to_keep')
					if eo:
						cmdToRun.extend([str(eo)])
			elif not (re.search('\.css$', inpfile) is None):
				outfile = re.sub(r'(\.css)$', r'.min\1', inpfile, 1)
				minifier = sublime.load_settings('Minify.sublime-settings').get('cssminifier') or 'clean-css'
				if minifier == 'uglifycss':
					cmd = sublime.load_settings('Minify.sublime-settings').get('uglifycss_command') or 'uglifycss'
					cmdToRun = [cmd]
					eo = sublime.load_settings('Minify.sublime-settings').get('uglifycss_options')
					if eo:
						cmdToRun.extend(str(eo).split())
					cmdToRun.extend([inpfile, '>', outfile])
				elif minifier == 'yui':
					cmd = sublime.load_settings('Minify.sublime-settings').get('java_command') or 'java'
					yui_compressor = str(sublime.load_settings('Minify.sublime-settings').get('yui_compressor') or 'yuicompressor-2.4.7.jar'
					cmdToRun = [cmd, '-jar', PLUGIN_DIR + '/bin/' + yui_compressor), inpfile, '-o', outfile]
					eo = sublime.load_settings('Minify.sublime-settings').get('yui_charset')
					if eo:
						cmdToRun.extend(['--charset', str(eo)])
					eo = sublime.load_settings('Minify.sublime-settings').get('yui_line_break')
					if not (type(eo) is bool):
						cmdToRun.extend(['--line-break', str(eo)])
				else:
					cmd = sublime.load_settings('Minify.sublime-settings').get('cleancss_command') or 'cleancss'
					cmdToRun = [cmd]
					eo = sublime.load_settings('Minify.sublime-settings').get('cleancss_options') or '--s1 -s --skip-rebase'
					if eo:
						cmdToRun.extend(str(eo).split())
					cmdToRun.extend(['-o', outfile, inpfile])
			elif not (re.search('\.html?$', inpfile) is None):
				outfile = re.sub(r'(\.html?)$', r'.min\1', inpfile, 1)
				cmd = sublime.load_settings('Minify.sublime-settings').get('html-minifier_command') or 'html-minifier'
				cmdToRun = [cmd]
				eo = sublime.load_settings('Minify.sublime-settings').get('html-minifier_options') or '--remove-comments --remove-comments-from-cdata --collapse-whitespace --conservative-collapse --collapse-boolean-attributes --remove-redundant-attributes --remove-script-type-attributes --remove-style-link-type-attributes --minify-js --minify-css'
				if eo:
					cmdToRun.extend(str(eo).split())
				cmdToRun.extend(['-o', outfile, inpfile])
			elif not (re.search('\.svg$', inpfile) is None):
				outfile = re.sub(r'(\.svg)$', r'.min\1', inpfile, 1)
				cmd = sublime.load_settings('Minify.sublime-settings').get('svgo_command') or 'svgo'
				cmdToRun = [cmd]
				eo = sublime.load_settings('Minify.sublime-settings').get('svgo_min_options')
				if eo:
					cmdToRun.extend(str(eo).split())
				cmdToRun.extend([inpfile, outfile])
			else:
				cmdToRun = False
			if cmdToRun:
				print('Minify: Minifying file ' + str(inpfile))
				self.run_cmd(cmdToRun, outfile)

class BeautifyCommand(MinifyBase, sublime_plugin.TextCommand):

	def do_action(self):
		inpfile = self.view.file_name()
		if inpfile and (len(inpfile) > 0):
			if sublime.load_settings('Minify.sublime-settings').get('save_first') and self.view.is_dirty():
				self.view.run_command('save')
			if not (re.search('\.js$', inpfile) is None):
				outfile = re.sub(r'(?:\.min)?(\.js)$', r'.beautified\1', inpfile, 1)
				cmd = sublime.load_settings('Minify.sublime-settings').get('uglifyjs_command') or 'uglifyjs'
				cmdToRun = [cmd, inpfile, '-o', outfile, '--comments', 'all', '-b']
				eo = sublime.load_settings('Minify.sublime-settings').get('uglifyjs_pretty_options')
				if eo:
					cmdToRun.extend(str(eo).split())
			elif not (re.search('\.css$', inpfile) is None):
				outfile = re.sub(r'(?:\.min)?(\.css)$', r'.beautified\1', inpfile, 1)
				cmd = sublime.load_settings('Minify.sublime-settings').get('js-beautify_command') or 'js-beautify'
				cmdToRun = [cmd]
				eo = sublime.load_settings('Minify.sublime-settings').get('js-beautify_options')
				if eo:
					cmdToRun.extend(str(eo).split())
				cmdToRun.extend(['--css', '-o', outfile, inpfile])
			elif not (re.search('\.html?$', inpfile) is None):
				outfile = re.sub(r'(?:\.min)?(\.html?)$', r'.pretty\1', inpfile, 1)
				cmd = sublime.load_settings('Minify.sublime-settings').get('js-beautify_command') or 'js-beautify'
				cmdToRun = [cmd]
				eo = sublime.load_settings('Minify.sublime-settings').get('js-beautify_html_options')
				if eo:
					cmdToRun.extend(str(eo).split())
				cmdToRun.extend(['--html', '-o', outfile, inpfile])
			elif not (re.search('\.svg$', inpfile) is None):
				outfile = re.sub(r'(?:\.min)?(\.svg)$', r'.pretty\1', inpfile, 1)
				cmd = sublime.load_settings('Minify.sublime-settings').get('svgo_command') or 'svgo'
				cmdToRun = [cmd]
				eo = sublime.load_settings('Minify.sublime-settings').get('svgo_pretty_options')
				if eo:
					cmdToRun.extend(str(eo).split())
				cmdToRun.extend(['--pretty', inpfile, outfile])
			if cmdToRun:
				print('Minify: Beautifying file ' + str(inpfile))
				self.run_cmd(cmdToRun, outfile)
