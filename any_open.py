r"""
AnyOpen Sublime Plugin.

Sends a sidebar path or current view path to your favorite program.
Multiple entries can be defined and you can limit them to a specific platform or file types.

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

You can then define actual commands for the context menu or sidebar context menu:

    Context menu:
    ```js
        {"command": "any_open_file", "args": {"key": "osx"}},
        {"command": "any_open_file", "args": {"key": "win"}},
        {"command": "any_open_file", "args": {"key": "win_rummage"}},
    ```

    Sidebar menu:

    ```js
        {"command": "any_open_folder", "args": {"paths": [], "key": "osx"}},
        {"command": "any_open_folder", "args": {"paths": [], "key": "win"}},
        {"command": "any_open_folder", "args": {"paths": [], "key": "win_rummage"}}
    ```

Licensed under MIT
Copyright (c) 2013-2017 Isaac Muse <isaacmuse@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions
of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
import sublime_plugin
import sublime
import subprocess
import os
import traceback
import sys

NO_OPEN = "Nothing to open!"
CALL_FAILURE = "SubProcess Error:\n%s"

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"


def get_environ():
    """Get environment and force utf-8."""

    import os
    env = {}
    env.update(os.environ)

    if _PLATFORM != 'windows':
        shell = env['SHELL']
        p = subprocess.Popen(
            [shell, '-l', '-c', 'echo "#@#@#${PATH}#@#@#"'],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        result = p.communicate()[0].decode('utf8').split('#@#@#')
        if len(result) > 1:
            bin_paths = result[1].split(':')
            if len(bin_paths):
                env['PATH'] = ':'.join(bin_paths)

    env['PYTHONIOENCODING'] = 'utf8'
    env['LANG'] = 'en_US.UTF-8'
    env['LC_CTYPE'] = 'en_US.UTF-8'

    return env


class AnyOpen(object):
    """AnyOpen Here."""

    def is_text_cmd(self):
        """Detect if TextCommand."""

        return isinstance(self, sublime_plugin.TextCommand)

    def is_win_cmd(self):
        """Detect if WindowCommand."""

        return isinstance(self, sublime_plugin.WindowCommand)

    def fail(self, msg, alert=True):
        """Display failure."""

        if alert:
            sublime.error_message(msg)
        else:
            print("AnyOpen: %s" % msg)

    def get_target(self, paths=None):
        """Get the target."""

        target = None
        fail_msg = NO_OPEN
        if paths:
            target = paths[0]
        elif self.is_text_cmd():
            filename = self.view.file_name()
            if filename is not None and os.path.exists(filename):
                target = filename
            else:
                self.fail(fail_msg)
        else:
            self.fail(fail_msg)
        return target

    def execute(self, target, key):
        """Execute command."""

        call = None
        setting = sublime.load_settings("any_open.sublime-settings").get('open_with', {})
        obj = setting.get(key, None)
        if obj is not None:
            call = obj.get('cmd', [])
            hide_window = obj.get('hide_window', False)
        if call is not None:
            is_string = isinstance(call, str)
            if is_string:
                call = call.replace("${PATH}", target.replace('"', '\"'))
            else:
                index = 0
                for item in call:
                    call[index] = item.replace("${PATH}", target)
                    index += 1
            try:
                if sublime.platform() == "windows":
                    startupinfo = subprocess.STARTUPINFO()
                    if hide_window:
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    subprocess.Popen(call, startupinfo=startupinfo, env=get_environ(), shell=is_string)
                else:
                    subprocess.Popen(call, env=get_environ(), shell=is_string)
            except Exception:
                self.fail("AnyOpen failed to open '%s'" % target, True)
                self.fail(CALL_FAILURE % str(traceback.format_exc()))

    def open_with(self, paths=None, key=None):
        """Call program."""

        if key is None:
            return
        target = self.get_target(paths)
        if target is None:
            return

        self.execute(target, key)


class AnyOpenFileCommand(sublime_plugin.TextCommand, AnyOpen):
    """Open the file."""

    def run(self, edit, key):
        """Run the command."""

        self.open_with(paths=None, key=key)

    def description(self, key=None):
        """Get command description."""

        caption = None
        if key is not None:
            setting = sublime.load_settings("any_open.sublime-settings").get('open_with', {})
            obj = setting.get(key, None)
            if obj is not None:
                caption = obj.get('caption', None)
        return caption

    def is_enabled(self, key=None):
        """Check if command is enabled."""

        enabled = False
        if key is not None:
            setting = sublime.load_settings("any_open.sublime-settings").get('open_with', {})
            obj = setting.get(key, None)
            if key is not None and obj is not None:
                platform = obj.get('platform', [])
                if len(platform):
                    if '*' in platform or sublime.platform() in platform:
                        filename = self.view.file_name()
                        file_filter = tuple(obj.get('filter', []))
                        if not file_filter:
                            enabled = True
                        elif filename is not None and filename.lower().endswith(file_filter):
                            enabled = True
        return enabled

    is_visible = is_enabled


class AnyOpenFolderCommand(sublime_plugin.WindowCommand, AnyOpen):
    """Open the folder."""

    def run(self, paths=None, key=None):
        """Run the command."""

        self.open_with(paths=paths, key=key)

    def description(self, paths=None, key=None):
        """Get command description."""

        caption = None
        if key is not None:
            setting = sublime.load_settings("any_open.sublime-settings").get('open_with', {})
            obj = setting.get(key, None)
            if obj is not None:
                caption = obj.get('caption', None)
        return caption

    def is_enabled(self, paths=None, key=None):
        """Check if command is enabled."""

        enabled = False
        if key is not None:
            setting = sublime.load_settings("any_open.sublime-settings").get('open_with', {})
            obj = setting.get(key, None)
            if key is not None and obj is not None:
                platform = obj.get('platform', [])
                if len(platform):
                    if '*' in platform or sublime.platform() in platform:
                        is_dir = os.path.isdir(paths[0])
                        if is_dir and not obj.get('exclude_folders', False):
                            enabled = True
                        elif not is_dir:
                            filename = paths[0]
                            file_filter = tuple(obj.get('filter', []))
                            if not file_filter:
                                enabled = True
                            elif filename is not None and filename.lower().endswith(file_filter):
                                enabled = True
        return enabled

    is_visible = is_enabled
