# AnyOpen

Send a file or folder to your favorite program.

## Overview

Sends a sidebar path or current view path to your favorite program.

## Configuring

Multiple entries can be defined and you can limit them to a specific platform:

```js
    "open_with": {
        "win": {
            "caption": "Grep Here…",
            "cmd": "\"C:\\Program Files\\grepWin\\grepWin.exe\" /searchpath:\"${PATH}\"",
            "platform": ["windows"]
        },
        "win_rummage": {
            "caption": "Rummage Here…",
            "cmd": ["c:\\Python35\\pythonw.exe", "-m", "rummage", "--path", "${PATH}"],
            "platform": ["windows"]
        },
        "osx": {
            "caption": "Rummage Here…",
            "cmd": ["rummage", "--path", "${PATH}"],
            "platform": ["osx"]
        }
    }
```

Commands can either be specified as an array of parameters, or as a string. Arrays directly create the process, while strings are executed as shell commands (what you specify is sent directly to your systems shell). While in most cases this may not matter, sometimes it does. Especially on Windows.

### Windows and the Shell Command

In the example above, you will notice [grepWin](http://stefanstools.sourceforge.net/grepWin.html) (a Windows application) is specified as a shell command. This is because grepWin will not parse spaces in the option `/searchpath:` if we create the process directly. And there is no real way to escape the spaces so they pass in normally. It must be run via a shell command, or indirectly called through a batch file.

When running a shell command, AnyOpen expects that the `${PATH}` parameter will be enclosed in double quotes and will escape double quotes when injecting the file or folder path into a shell command. When specified as an array of parameters, you do not have to quote `${PATH}`.

GrepWin may be a special case. In most cases, you can just use the array format (especially on macOS and Linux).  If you prefer the shell format, you can do that on any platform as well.

### Windows Hiding the Console

Depending on how you call your application, a console might appear. This can occur if you are calling your application indirectly through a batch file or something similar. In this case, a batch file may spawn your actual process, and hiding the batch file may be all you need. If this is the case, you can use the option `hide_window` and set it to `true`.

```js
    "win": {
        "caption": "Open Here…",
        "cmd": ["c:\\MyPath\\open.bat", "${PATH}"],
        "hide_window": true,
        "platform": ["windows"]
    },
```

## Commands

You can then define actual commands for the context menu or sidebar context menu.  You can include as many as you need.

Context menu (`User/Context.sublime-menu`):
```js
    {"command": "any_open_file", "args": {"key": "osx"}},
    {"command": "any_open_file", "args": {"key": "win"}},
    {"command": "any_open_file", "args": {"key": "win_rummage"}},
```

Sidebar menu (`Side Bar.sublime-menu`):

```js
    {"command": "any_open_folder", "args": {"paths": [], "key": "osx"}},
    {"command": "any_open_folder", "args": {"paths": [], "key": "win"}},
    {"command": "any_open_folder", "args": {"paths": [], "key": "win_rummage"}}
```

## License

Licensed under MIT
Copyright (c) 2013-2017 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
