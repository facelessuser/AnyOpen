[![Build][github-ci-image]][github-ci-link]
![License][license-image]
# AnyOpen

Send a file or folder to your favorite program. Works in sidebar context menus or view context menus.

## Configuring

Multiple entries can be defined and you can limit them to a specific platform and even file extensions.

```js
    "open_with": {
        "osx_gimp": {
            "caption": "Gimp Here…",
            "cmd": ["/Applications/Gimp.app/Contents/MacOS/gimp-2.8", "${PATH}"],
            "platform": ["osx"],
            "exclude_folders": true,
            "filter": [".png", ".bmp", ".gif", ".jpg", ".jpeg", ".xcf"]
        },
        "win_grep": {
            "caption": "Grep Here…",
            "cmd": "\"C:\\Program Files\\grepWin\\grepWin.exe\" /searchpath:\"${PATH}\"",
            "platform": ["windows"]
        },
        "win_rummage": {
            "caption": "Rummage Here…",
            "cmd": ["c:\\Python35\\pythonw.exe", "-m", "rummage", "--path", "${PATH}"],
            "platform": ["windows"]
        },
        "osx_rummage": {
            "caption": "Rummage Here…",
            "cmd": ["rummage", "--path", "${PATH}"],
            "platform": ["osx"]
        }
    }
```

Commands can either be specified as an array of parameters, or as a string. Arrays directly create the process, while
strings are executed as shell commands (what you specify is sent directly to your systems shell). While in most cases
this may not matter, sometimes it does. Especially on Windows.

### Environment

You can modify the environment if desired via the `env` key. Any key value pair provided will be copied to the
environment when the command is run. If the value is set to `null`, the key will be removed entirely.

```js
    "open_with": {
        "win_rummage":
        {
            "caption": "Rummage Here…",
            "cmd":
            [
                "pythonw",
                "-m",
                "rummage",
                "--path",
                "${PATH}"
            ],
            "env": {
                "__COMPAT_LAYER": null
            },
            "platform":
            [
                "windows"
            ]
        }
    }
```

With that said, the plugin generally expects the environment to be in `UTF-8`, so changing that is not advisable as that
will most likely be overwritten regardless.

### Filtering

Since paths can differ for different operating systems (especially on Windows), you must specify the `platform` for the
command.  You can specify `windows`, `osx`, and/or `linux`. The `platform` key is an array and you can specify multiple
platforms if needed.

If placing entry in `Side Bar.sublime-menu`, you may have a need to exclude folders.  When defining your entry add the
option `exclude_folders` and set it to `true`, and it will not show up in the side bar context menu.

If you only need to show the menu on certain file types, add the `filter` parameter and give it an array of extensions.
Specify them as lowercase as when the file is compared, it will be forced to lowercase.


```js
    "osx_gimp": {
        "caption": "Gimp Here…",
        "cmd": ["/Applications/Gimp.app/Contents/MacOS/gimp-2.8", "${PATH}"],
        "platform": ["osx"],
        "exclude_folders": true,
        "filter": [".png", ".bmp", ".gif", ".jpg", ".jpeg", ".xcf"]
    },
```

By default, AnyOpen will place entries in both the side bar menu and the file context menu.  If you need to limit the
command to one or the other, simply specify `sidebar` and/or `context` in in the `menus` array like so
`"menus": ["sidebar"]`.

### Shell Commands

```js
    "win": {
        "caption": "Grep Here…",
        "cmd": "\"C:\\Program Files\\grepWin\\grepWin.exe\" /searchpath:\"${PATH}\"",
        "platform": ["windows"]
    },
```

In the example above, you will notice [`grepWin`](http://stefanstools.sourceforge.net/grepWin.html) (a Windows
application) is specified as a shell command. This is because `grepWin` will not parse spaces in the option
`/searchpath:` if we create the process directly using the array format. And there is no real way to escape the spaces
so they pass in normally. For this program, the command must be run via a shell command, or indirectly through a batch
file.

When running a shell command, AnyOpen expects that the `${PATH}` parameter will be enclosed in double quotes and will
    escape double quotes in the path when injecting the file or folder path into a shell command. When specified as an
    array of parameters, you do not have to quote `${PATH}`.

`grepWin` may be a special case. In most cases, you can just use the array format (especially on macOS and Linux).  If
you prefer the shell format, you can do that on any platform as well.

### Windows Hiding the Console

Depending on how you call your application, a console might appear. This can occur if you are calling your application
indirectly through a batch file or something similar. In this case, a batch file may spawn your actual process, and
hiding the batch file may be all you need. If this is the case, you can use the option `hide_window` and set it to
`true`.

```js
    "win": {
        "caption": "Open Here…",
        "cmd": ["c:\\MyPath\\open.bat", "${PATH}"],
        "hide_window": true,
        "platform": ["windows"]
    },
```

## License

Licensed under MIT
Copyright (c) 2013-2020 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

[github-ci-image]: https://github.com/facelessuser/sublime-markdown-popups/workflows/build/badge.svg?branch=master&event=push
[github-ci-link]: https://github.com/facelessuser/sublime-markdown-popups/actions?query=workflow%3Abuild+branch%3Amaster
[license-image]: https://img.shields.io/badge/license-MIT-blue.svg?labelColor=333333
