Minify Package for Sublime Text
===============================

Overview
--------
The `Minify Package` for Sublime Text can create a minified version of a currently open JavaScript or CSS file.

The plugin generates new files with the extensions `.min.js` or `.min.css`.

Compared to other minifier packages for ST, this one is very light: The plugin itself is less than 130 lines of Python code.
Also, once installed, this Package do not need Internet access to do its job, it works offline.

This Package has been tested with both Sublime Text 2 and Sublime Text 3 and should work fine on all platforms.

It uses the excellent [UglifyJS 2](https://github.com/mishoo/UglifyJS2) program to minify JavaScript files.
While `YUI Compressor` is utilized to minify CSS files. (`YUI Compressor` is used for CSS file minification only.)

It can also create a beautified version of the currently open JavaScript file. This can be useful in case you're
looking at a file which was previously minified and the original / uncompressed version of the file is unavailable.

Requirements
------------
You need to have Sublime Text 2 or Sublime Text 3 installed, obviously.

Since this Package uses UglifyJS 2 and UglifyJS runs in Node, you must have [Nodejs](http://nodejs.org/) installed on your system.
Once you have Nodejs installed, you should install UglifyJS 2. It is recommended to install it globally with the following command:

`npm install uglify-js -g`

After this the `uglifyjs` command should be available in your system PATH.

For CSS file minification, this package uses `YUI Compressor` and it is running in Java so you must have Java installed on your system
and it is recommended to have the `java` command available in your system PATH.

If you do not have these commands available in your system PATH then alternatively, you can specify custom locations for both
the `uglifyjs` and `java` commands in the User Settings of this Package.

IMPORTANT NOTE FOR MAC USERS!
If javascript minification does not work, the most likely reason is: Sublime Text does not search for executable files under
the /usr/local/bin directory regardless of your system PATH setting (ST uses its own PATH settings). To solve this issue you can
create a symlink:

`cd /usr/bin && sudo ln -s /usr/local/bin/node node`

Also, on OSX you must specify the full path to the `uglifyjs` executable by creating a `Settings -- User` file for Minify which should
include at least the following setting:

    "uglifyjs_command": "/usr/local/bin/uglifyjs"

Installation
------------
You may install the `Minify` Sublime Text Package via the excellent [Package Control](https://sublime.wbond.net/) package manager
and this is the recommended way to install it.

Alternatively, you may install the `Minify Package` by using git:

*MacOSX*

    git clone git://github.com/tssajo/Minify.git ~/Library/Application\ Support/Sublime\ Text\ 2/Packages/Minify

Note: Replace "Sublime\ Text\ 2" with "Sublime\ Text\ 3" in the above command if you are using Sublime Text 3

*Windows*

    git clone git://github.com/tssajo/Minify.git %APPDATA%\Sublime Text 2\Packages\Minify

Note: Replace "Sublime Text 2" with "Sublime Text 3" in the above command if you are using Sublime Text 3

How to use
----------
Open a `.js` or `.css` file in your Sublime Text editor, then you can:

A.  Use the Context Menu inside the Sublime Text editor window; or

B.  Access the `Minify file` or `Beautify file` commands under Tools / Minify menu in Sublime Text.

C.  The following keyboard shortcuts are also available:

`ctrl + alt + m` ( `super + alt + m` on OSX ) :
	Minifies the current buffer and saves the minified version into the same directory with the
    appropriate .min.js or .min.css file extension, then opens the minified file in a new editor window.

`ctrl + alt + shift + m` ( `super + alt + shift + m` on OSX ) :
	beautifies the current buffer and saves the beautified version into the same directory with the
    appropriate .beautified.js file extension, then opens the beautified file in a new editor window.

TODO
----
Beautifying of CSS files are not supported at the moment.

License
-------
See [LICENSE.md](https://github.com/tssajo/Minify/blob/master/LICENSE.md) file for licensing information.
