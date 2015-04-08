import sublime, sublime_plugin, re, os, subprocess, platform

PLUGIN_DIR = os.path.dirname(__file__) if int(sublime.version()) >= 3000 else os.getcwd()
# on Windows platform run the commands in a shell
RUN_IN_SHELL = sublime.platform() == 'windows'
# if there is no sublime.set_timeout_async method available then run the commands in a separate thread using the threading module
HAS_ASYNC = callable(getattr(sublime, 'set_timeout_async', None))

if sublime.load_settings('Minify.sublime-settings').get('debug_mode'):
	print('Minify: Sublime Platform: ' + str(sublime.platform()))
	print('Minify: Sublime Version: ' + str(sublime.version()))
	print('Minify: Python v' + platform.python_version())
	print('Minify: PLUGIN_DIR: ' + str(PLUGIN_DIR))
	print('Minify: RUN_IN_SHELL: ' + str(RUN_IN_SHELL))
	print('Minify: Sublime Text HAS_ASYNC: ' + str(HAS_ASYNC))

if not HAS_ASYNC:
	import threading

	class RunCmdInOtherThread(threading.Thread):
		def __init__(self, cmdToRun):
			self.cmdToRun = cmdToRun
			self.result = 1
			self.err = ''
			threading.Thread.__init__(self)

		def run(self):
			p = subprocess.Popen(self.cmdToRun, stderr=subprocess.PIPE, shell=RUN_IN_SHELL)
			self.err = p.communicate()[1]
			self.result = p.returncode

class ThreadHandling():
	def handle_result(self, result, outfile, err, cmdstr):
		if result:
			if err:
				sublime.error_message(cmdstr + '\r\n\r\n' + err.decode('utf-8'))
		else:
			if sublime.load_settings('Minify.sublime-settings').get('open_file'):
				sublime.active_window().open_file(outfile)

	def handle_thread(self, thread, outfile):
		if thread.is_alive():
			sublime.set_timeout(lambda: self.handle_thread(thread, outfile), 100)
		else:
			self.handle_result(thread.result, outfile, thread.err, ' '.join(thread.cmdToRun))

	def run_cmd(self, cmdToRun, outfile):
		if sublime.load_settings('Minify.sublime-settings').get('debug_mode'):
			print('Minify: Output file ' + str(outfile))
			print('Minify: cmdToRun: ' + str(cmdToRun))
		if HAS_ASYNC:
			p = subprocess.Popen(cmdToRun, stderr=subprocess.PIPE, shell=RUN_IN_SHELL)
			err = p.communicate()[1]
			result = p.returncode
			self.handle_result(result, outfile, err, ' '.join(cmdToRun))
		else:
			thread = RunCmdInOtherThread(cmdToRun)
			thread.start()
			sublime.set_timeout(lambda: self.handle_thread(thread, outfile), 100)

class PluginBase(ThreadHandling):
	def is_enabled(self):
		filename = self.view.file_name()
		return bool(filename and (len(filename) > 0) and not (re.search('.+\.(?:js|css|html?|svg)$', filename) is None))

	def run(self, edit):
		if HAS_ASYNC:
			sublime.set_timeout_async(lambda: self.do_action(), 0)
		else:
			self.do_action()

class MinifyClass():
	def minify(self, view):
		inpfile = view.file_name()
		if inpfile and (len(inpfile) > 0):
			if view.is_dirty() and sublime.load_settings('Minify.sublime-settings').get('save_first'):
				view.run_command('save')
				if sublime.load_settings('Minify.sublime-settings').get('auto_minify_on_save'):
					return
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
					yui_compressor = sublime.load_settings('Minify.sublime-settings').get('yui_compressor') or 'yuicompressor-2.4.7.jar'
					cmdToRun = [cmd, '-jar', PLUGIN_DIR + '/bin/' + str(yui_compressor), inpfile, '-o', outfile]
					eo = sublime.load_settings('Minify.sublime-settings').get('yui_charset')
					if eo:
						cmdToRun.extend(['--charset', str(eo)])
					eo = sublime.load_settings('Minify.sublime-settings').get('yui_line_break')
					if not (type(eo) is bool):
						cmdToRun.extend(['--line-break', str(eo)])
				else:
					cmd = sublime.load_settings('Minify.sublime-settings').get('cleancss_command') or 'cleancss'
					cmdToRun = [cmd]
					eo = sublime.load_settings('Minify.sublime-settings').get('cleancss_options') or '--s0 -s --skip-rebase'
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

class BeautifyClass():
	def beautify(self, view):
		inpfile = view.file_name()
		if inpfile and (len(inpfile) > 0):
			if sublime.load_settings('Minify.sublime-settings').get('save_first') and view.is_dirty():
				view.run_command('save')
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
