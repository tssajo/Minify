Minify Package for Sublime Text
===============================

Overview
--------
The `Minify Package` for Sublime Text can create a minified version of a currently open JavaScript, CSS or SVG file.

The plugin generates new files with the extensions `.min.js` or `.min.css` or `.min.svg`.

Compared to other minifier packages for ST, this one is very light: The plugin itself is less than 170 lines of Python code.
Also, once installed, this Package do not need Internet access to do its job, it works entirely offline.

This Package has been tested with both Sublime Text 2 and Sublime Text 3 and should work fine on all platforms.

The `Minify Package` for ST uses several other programs to do its job.

For minification tasks:

`Minify` uses [UglifyJS 2](https://github.com/mishoo/UglifyJS2) a Nodejs program to minify JavaScript files.

`YUI Compressor` is utilized to minify CSS files. (`YUI Compressor` is used for CSS file minification only.)

[svgo](https://github.com/svg/svgo) Nodejs program is used to minify SVG files.

The Minify package can also beautify files:

For Javascript beautification, it uses `UglifyJS 2`. This can be useful in case you're looking at a file which was previously
minified and the original / uncompressed version of the file is unavailable.

[js-beautify](https://www.npmjs.org/package/js-beautify) is used to beautify CSS files.

`svgo` is used to make SVG files pretty.

Requirements
------------
Before you start, you must have Sublime Text 2 or Sublime Text 3 installed and working properly. Then:

1. Nodejs -- Since this package uses Node for many of its tasks, you must have [Nodejs](http://nodejs.org/) installed on your system.
Once you have Nodejs installed, you need to install the following programs globally for Node:

2. Install `UglifyJS 2` (it is needed for Javascript minification and beautification):
`npm -g install uglify-js`

3. Install `js-beautify` (it is needed for CSS beautification):
`npm -g install js-beautify`

4. Install `svgo` (it is needed for SVG minification and beautification):
`npm -g install svgo`

5. Install Java which is required for `YUI Compressor` (it is needed for CSS minification)

Please make sure the `java` command is available in your system PATH.

If you do not have any of the above commands available in your system PATH then alternatively you can specify custom locations
for those commands in `Settings -- User` of the `Minify Package` ( `Minify.sublime-settings` and NOT `Preferences.sublime-settings` ! )

IMPORTANT NOTE FOR MAC USERS!
-----------------------------
Unfortunately, Sublime Text does not search for executable files under /usr/local/bin directory regardless of your system PATH setting.
(It seems, ST uses its own PATH setting which we cannot change.) Because of this, you probably need to create a symlink on your Mac:

Open a Terminal and issue the following command:

`cd /usr/bin && sudo ln -s /usr/local/bin/node node`

But it is not enough! You also need to add full path for the commands `Minify` uses. After installing the `Minify` package in ST,
please open its default settings ( Preferences -> Package Settings -> Minify -> Settings -- Default ) and copy the contents to the
`Settings -- User` file ( Preferences -> Package Settings -> Minify -> Settings -- User ) then you can customize `Minify` settings there.
Please do not modify `Settings -- Default` because it will be overwritten by the next release of the `Minify` package!

E.g.: To add full path to your `uglifyjs` command, change the appropriate line inside your `Settings -- User` file to

    "uglifyjs_command": "/usr/local/bin/uglifyjs",

Installation
------------
Please install the `Minify` Sublime Text Package via the [Package Control](https://sublime.wbond.net/) package manager.

Alternatively, you may install the `Minify Package` by using git:

*MacOSX*

    git clone git://github.com/tssajo/Minify.git ~/Library/Application\ Support/Sublime\ Text\ 2/Packages/Minify

Note: Replace "Sublime\ Text\ 2" with "Sublime\ Text\ 3" in the above command if you are using Sublime Text 3

*Windows*

    git clone git://github.com/tssajo/Minify.git %APPDATA%\Sublime Text 2\Packages\Minify

Note: Replace "Sublime Text 2" with "Sublime Text 3" in the above command if you are using Sublime Text 3

How to use
----------
Open a `.js` or `.css` or `.svg` file in your Sublime Text editor and you can:

A.  Use the Context Menu inside the Sublime Text editor window; or

B.  Access the `Minify file` or `Beautify file` commands under Tools / Minify menu in Sublime Text.

C.  The following keyboard shortcuts are also available:

`ctrl + alt + m` ( `super + alt + m` on OSX ) :
	Minifies the current buffer and saves the minified version into the same directory with the
    appropriate .min.js or .min.css or .min.svg file extension, then opens the minified file in a new editor window.

`ctrl + alt + shift + m` ( `super + alt + shift + m` on OSX ) :
	beautifies the current buffer and saves the beautified version into the same directory with the
    appropriate .beautified.js or .beautified.css or .pretty.svg file extension, then opens the beautified
    file in a new editor window.

TODO
----
Adding HTML minification feature.

License
-------
See [LICENSE.md](https://github.com/tssajo/Minify/blob/master/LICENSE.md) file for licensing information.
