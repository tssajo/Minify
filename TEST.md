`Minify` for Sublime Text
=========================

Overview
--------
`Minify` for Sublime Text can create a minified version of a currently opened CSS, HTML, JavaScript or SVG file.

The plugin generates a new file with an altered file extension such as `.min.css`, `.min.htm` or `.min.html`, `.min.js`, `.min.svg`.

Compared to other Sublime Text minifier packages `Minify` is very light: the plugin itself is less than 170 lines of Python code.
Once installed `Minify` does not need Internet access to do its job: it works offline.

`Minify` has been tested under both Sublime Text 2 and Sublime Text 3 and it should work fine on all supported platforms (Linux, OS X and Windows).

`Minify` depends on other programs written in Node.js to do its job. Detailed installation instructions for those dependencies are provided below.

Which 3rd party programs are being used by `Minify`
---------------------------------------------------

|            | Minify | Beautify |
| ---------- | ------ | -------- |
| CSS        | [clean-css](https://www.npmjs.com/package/clean-css) or [uglifycss](https://www.npmjs.com/package/uglifycss) | [js-beautify](https://www.npmjs.org/package/js-beautify) |
| HTML       | [html-minifier](https://www.npmjs.com/package/html-minifier) | [html-minifier](https://www.npmjs.com/package/html-minifier) |
| JavaScript | [uglifyjs](https://www.npmjs.com/package/uglifyjs) | [uglifyjs](https://www.npmjs.com/package/uglifyjs) |
| SVG        | [svgo](https://www.npmjs.com/package/svgo) | [svgo](https://www.npmjs.com/package/svgo) |

Installation in Three Easy Steps
--------------------------------

1. Please install Node.js - [see installation instructions](https://github.com/joyent/node/wiki/Installing-Node.js-via-package-manager)

  Notes:

    On Mac OS X I usually use [Homebrew](http://brew.sh/) to install Node.js: First I install Homebrew then I install Node.js with the following command `brew install node`

    On Windows I simply download the [Windows Installer](https://nodejs.org/#download) directly from the nodejs.org web site.

    Please make sure that the command `node` is available in your `PATH`.
    Here is how you can test if the `node` command is available in your `PATH`:
    Open up a shell window (it is called Terminal on OS X and CMD window on Windows) and then issue the following command:
    `node --version`
    If you get a version number displayed then you are probably fine. If you get an error message such as `command not found` or something similar then the `node` command is not available on your system.

2. Install some Node.js CLI apps globally

  `npm install -g clean-css uglifycss js-beautify html-minifier uglify-js svgo`

  Notes:

    If you are never going to work with e.g. SVG files then you can leave out `svgo` from the above command, etc.

    If you already have some or all of the above Node.js CLI apps installed on your computer then you can update them to the latest version with the following command:
    `npm update -g clean-css uglifycss js-beautify html-minifier uglify-js svgo`

3. Install `Minify` for Sublime Text via [Package Control](https://sublime.wbond.net/): https://packagecontrol.io/packages/Minify

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

5. Install Java which is required for `YUI Compressor` (which is needed for CSS minification)

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
