import os
import re
import envs
from detection import get_login_managers


class LoginManagerError(Exception):
    pass


def configure_login_managers(mode):

    login_managers = get_login_managers()

    if len(login_managers) == 0:
        msg = "No supported login manager detected. Please manually configure" \
              "your login manager to use the display setup script at %s. If you" \
              "use xinit, add this script to your .xinitrc" % envs.XSETUP_PATH
        print(msg)
        return

    for manager_name in login_managers:

        if manager_name == "sddm":
            _configure_sddm(mode)


def _configure_sddm(mode):

    CONF_PATH = "/etc/sddm.conf"
    CONF_PATH = "sddm.conf"  # TESTING

    if not os.path.isfile(CONF_PATH):

        sddm_conf_text = "[X11]\n" \
                         "DisplayCommand=%s\n" % envs.XSETUP_PATH

        try:
            with open(CONF_PATH, 'w') as f:
                f.write(sddm_conf_text)
        except IOError:
            raise LoginManagerError("Cannot open or write to %s" % CONF_PATH)

    else:

        try:
            with open(CONF_PATH, 'r') as f:
                content = f.read()
        except IOError:
            raise LoginManagerError("%s exists but cannot be read from." % CONF_PATH)

        idx_start_section = content.find("[X11]")

        # No [X11] section found
        if idx_start_section == -1:

            print("No [X11]")

            new_section_text = "[X11]\n" \
                               "DisplayCommand=%s\n" % envs.XSETUP_PATH

            new_content = content + "\n" + new_section_text

        # [X11] section found
        else:

            res = re.search("\n\\[.+\\]\n", content[idx_start_section+len("[X11]"):])

            if res:
                idx_end_section = res.start(0) + idx_start_section
            else:
                idx_end_section = len(content)

            res = re.findall("DisplayCommand=.+\n", content[idx_start_section:idx_end_section])

            if res:
                raise LoginManagerError("DisplayCommand is already set in %s !" % CONF_PATH)

            else:

                cmd_text = "DisplayCommand=%s\n" % envs.XSETUP_PATH
                new_content = content[:idx_end_section] + "\n" + cmd_text + content[idx_end_section:]

        try:
            with open(CONF_PATH, 'w') as f:
                f.write(new_content)
        except IOError:
            raise LoginManagerError("Cannot open or write to %s" % CONF_PATH)
