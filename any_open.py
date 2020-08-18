r"""
AnyOpen Sublime Plugin.

Sends a sidebar path or current view path to your favorite program.
Multiple entries can be defined and you can limit them to a specific platform or file types.

Licensed under MIT
Copyright (c) 2013-2019 Isaac Muse <isaacmuse@gmail.com>

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
import datetime
import time
import json
import codecs

MENU_PATH = "Packages/User/AnyOpen"
NO_OPEN = "Nothing to open!"
CALL_FAILURE = "SubProcess Error:\n%s"

if sys.platform.startswith('win'):
    _PLATFORM = "windows"
elif sys.platform == "darwin":
    _PLATFORM = "osx"
else:
    _PLATFORM = "linux"


def get_environ(adjust):
    """Get environment and force UTF-8."""

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

    for k, v in adjust.items():
        if v is None:
            if k in env:
                del env[k]
        else:
            env[k] = v

    env['PYTHONIOENCODING'] = 'utf8'
    env['LANG'] = 'en_US.UTF-8'
    env['LC_CTYPE'] = 'en_US.UTF-8'

    return env


class AnyOpen(object):
    """AnyOpen Here."""

    def is_text_cmd(self):
        """Detect if `TextCommand`."""

        return isinstance(self, sublime_plugin.TextCommand)

    def is_win_cmd(self):
        """Detect if `WindowCommand`."""

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
            env_adjust = obj.get('env', {})
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
                current_env = get_environ(env_adjust)
                if sublime.platform() == "windows":
                    startupinfo = subprocess.STARTUPINFO()
                    if hide_window:
                        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    subprocess.Popen(call, startupinfo=startupinfo, env=current_env, shell=is_string)
                else:
                    subprocess.Popen(call, env=current_env, shell=is_string)
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


def reload_menus():
    """Reload."""

    menu = os.path.join(os.path.dirname(sublime.packages_path()), os.path.normpath(MENU_PATH))
    sidebar_path = os.path.join(menu, "Side Bar.sublime-menu")
    context_path = os.path.join(menu, "Context.sublime-menu")
    if not os.path.exists(menu):
        os.makedirs(menu)

    settings = sublime.load_settings('any_open.sublime-settings')
    open_with = settings.get('open_with', {})

    sidebar = []
    context = []
    for k, v in open_with.items():
        for plat in v.get('platform', tuple()):
            if plat in (_PLATFORM, '*'):
                where = v.get('menus', ('sidebar', 'context'))
                if 'sidebar' in where:
                    sidebar.append(
                        {
                            "command": "any_open_folder",
                            "args": {"paths": [], "key": k}
                        }
                    )
                if 'context' in where:
                    context.append(
                        {
                            "command": "any_open_file",
                            "args": {"paths": [], "key": k}
                        }
                    )

    with codecs.open(sidebar_path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(sidebar))

    with codecs.open(context_path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(context))


def plugin_loaded():
    """Trigger a menu refresh if setting file is newer than menu file(s)."""

    settings = sublime.load_settings('any_open.sublime-settings')
    settings.clear_on_change('reload')
    settings.add_on_change('reload', reload_menus)

    menu = os.path.join(os.path.dirname(sublime.packages_path()), os.path.normpath(MENU_PATH))
    if not os.path.exists(menu):
        os.makedirs(menu)

    triggered = False

    sidebar = os.path.join(menu, "Side Bar.sublime-menu")
    context = os.path.join(menu, "Context.sublime-menu")

    if os.path.exists(sidebar):
        mtime = os.path.getmtime(sidebar)
        datetime.datetime.utcfromtimestamp(mtime)
        mtimes = float(os.path.getmtime(sidebar))
    else:
        mtimes = -1

    if os.path.exists(context):
        mtime = os.path.getmtime(context)
        datetime.datetime.utcfromtimestamp(mtime)
        mtimec = float(os.path.getmtime(context))
    else:
        mtimec = -1

    triggered = False
    if float(settings.get('last_update', 0.0)) > float(mtimes):
        settings.set('last_update', float(time.time()))
        triggered = True
    elif float(settings.get('last_update', 0.0)) > float(mtimec):
        settings.set('last_update', float(time.time()))
        triggered = True

    if triggered:
        sublime.save_settings('any_open.sublime-settings')
