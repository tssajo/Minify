# `Minify` for Sublime Text

## What is `Minify`

`Minify` for Sublime Text can create a minified version of a currently open CSS, HTML, JavaScript, JSON or SVG file.

`Minify` generates a new file with an altered file extension such as `.min.css`, `.min.html`, `.min.js`, `.min.json`
or `.min.svg`.
It can be easily configured to generate .map files too for minified CSS and JavaScript files.

Compared to other Sublime Text minifier packages `Minify` is very light: the plugin itself is less than 250 lines of
Python code. Once installed `Minify` does not need Internet access to do its job, it works offline.

`Minify` has been tested under both Sublime Text 2 and Sublime Text 3 and it should work fine on all supported
platforms (Linux, Mac OS X and Windows).

`Minify` depends on other programs written in Node.js to do its job. Detailed installation instructions for those
dependencies are provided below.

## Which 3rd party programs are used by `Minify`

|                | Minify | Beautify |
| -------------- |:------:|:--------:|
| **CSS**        | [clean-css](https://www.npmjs.com/package/clean-css) + [clean-css-cli](https://www.npmjs.com/package/clean-css-cli) or [uglifycss](https://www.npmjs.com/package/uglifycss) | [js-beautify --css](https://www.npmjs.org/package/js-beautify) |
| **HTML**       | [html-minifier](https://www.npmjs.com/package/html-minifier) | [js-beautify --html](https://www.npmjs.org/package/js-beautify) |
| **JavaScript** | [uglifyjs](https://www.npmjs.com/package/uglifyjs) | [uglifyjs --beautify](https://www.npmjs.com/package/uglifyjs) |
| **JSON**       | [minjson](https://www.npmjs.com/package/minjson) (uses [uglifyjs](https://www.npmjs.com/package/uglifyjs)) | [minjson](https://www.npmjs.com/package/minjson) (uses [uglifyjs](https://www.npmjs.com/package/uglifyjs)) |
| **SVG**        | [svgo](https://www.npmjs.com/package/svgo) | [svgo --pretty](https://www.npmjs.com/package/svgo) |

## Installation in Three Easy Steps

1. Install `Minify` package for Sublime Text:<br><br>
  a) Install `Minify` via [Package Control](https://packagecontrol.io/) (this is the recommended method) :<br><br>
  First install Package Control - [see installation instructions](https://packagecontrol.io/installation)<br><br>
  Then inside Sublime Text press `ctrl + shift + p` ( `super + shift + p` on Mac OS X ) and find
  `Package Control: Install Package` then press Enter.
  You can search for the `Minify` package by entering its name `Minify`<br><br>
  b) Alternatively, you can install `Minify` from GitHub directly (this is NOT recommended) :<br><br>
  _on Mac OS X:_<br><br>
  `git clone git://github.com/tssajo/Minify.git ~/Library/Application\ Support/Sublime\ Text\ 3/Packages/Minify`<br><br>
  Note: Replace "Sublime\ Text\ 3" with "Sublime\ Text\ 2" in the above command if you are using Sublime Text 2.<br><br>
  _on Windows:_<br><br>
  `git clone git://github.com/tssajo/Minify.git %APPDATA%\Sublime Text 3\Packages\Minify`<br><br>
  Note: Replace "Sublime Text 3" with "Sublime Text 2" in the above command if you are using Sublime Text 2.

2. Install Node.js:<br><br>
  Windows and Mac OS X users should just visit [nodejs.org](https://nodejs.org/) and click on the INSTALL button,<br>
  Linux users can download pre-compiled binary files from [https://nodejs.org/download/](https://nodejs.org/download/)<br><br>
  After successful installation, please make sure that `node` is in your `PATH`, here is how to test it:<br><br>
  Open up a shell window (`Terminal` on Mac OS X, `CMD.exe` on Windows) and issue the following command:<br><br>
  `node --version`<br><br>
  You should see a version number. But if you see an error message such as `command not found` or something similar
  then `node` is not available via your `PATH` and you must fix this!

3. Install required Node.js CLI apps:<br><br>
  From a shell window (`Terminal` on Mac OS X, `CMD.exe` on Windows) issue the following command:<br><br>
  `npm install -g clean-css-cli uglifycss js-beautify html-minifier uglify-js minjson svgo`<br><br>
  Notes:<br><br>
  If you are on Mac OS X and you get an error here then issue the following command from `Terminal`:
  `sudo chown -R $USER /usr/local` and then try to issue the npm install command from above again.<br><br>
  If you are never going to work with e.g. SVG files then you can leave out `svgo` from the above npm
  install command. You can also leave out `uglifycss`, etc.<br><br>
  If you already have some or all of the above Node.js CLI apps installed on your system then it is
  recommended to update them all to the latest version with the following command:<br><br>
  `npm update -g clean-css-cli uglifycss js-beautify html-minifier uglify-js minjson svgo`<br><br>
  Please test that the installed Node.js CLI apps are available via your `PATH`, here is how:<br><br>
  Still from a shell window (`Terminal` on Mac OS X, `CMD.exe` on Windows) issue the following command,
  for example:<br><br>
  `cleancss --version`<br><br>
  You should see a version number. But if you see an error message such as `command not found` or something similar
  then `cleancss` is not available via your `PATH` and you must fix this!<br><br>
  You may want to do this test for all Node.js CLI apps (`cleancss`, `uglifycss`, `js-beautify`, `html-minifier`,
  `uglifyjs`, `minjson` and `svgo`).<br><br>

##How to use `Minify`

Open a `.css` or `.htm` or `.html` or `.js` or `.json` or `.svg` file in your Sublime Text editor and you can

  a) use the Context Menu inside the Sublime Text editor window,

  b) access the `Minify file` or `Beautify file` commands under Tools / Minify menu in Sublime Text,

  c) use one of the following keyboard shortcuts:

  `ctrl + alt + m` ( `super + alt + m` on Mac OS X )

  This minifies the current buffer and saves the minified version into the same directory with the
  appropriate .min.css or .min.htm or .min.html or .min.js or .min.svg file extension
  then it opens the minified file in a new editor window.

  `ctrl + alt + shift + m` ( `super + alt + shift + m` on Mac OS X )

  This beautifies the current buffer and saves the beautified version into the same directory with the appropriate
  .beautified.css or .beautified.htm or .beautified.html or .beautified.js or .pretty.svg file extension
  then it opens the beautified file in a new editor tab.

## User settings

You can put your customized settings here:

*(Preferences > Package Settings > Minify > Settings - User)*

To find out what the possible options are please see:

*(Preferences > Package Settings > Minify > Settings - Default)*

Please do not edit the **Settings - Default** file!!

## Project settings

Also, you can override the default and user settings for individual projects. Just add a "Minify" object to the "settings" object
in the project's .sublime-project file containing your [project specific settings](http://www.sublimetext.com/docs/3/projects.html).

###Example:

```json
{
    "settings": {
        "Minify": {
            "open_file": false,
            "auto_minify_on_save": true,
            "allowed_file_types": [
                "css",
                "js",
                "svg"
            ]
        }
    }
}
```

##License

See [LICENSE.md](https://github.com/tssajo/Minify/blob/master/LICENSE.md) file for licensing information.
