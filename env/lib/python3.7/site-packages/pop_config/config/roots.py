"""
Used to take care of the options that end in `_dir`. The assumption is that
`_dir` options need to be treated differently. They need to verified to exist
and they need to be rooted based on the user, root option etc.
"""
# Import python libs
import os
import re


def apply(hub, ret, raw, cli):
    """
    Take the initial defaults and apply the roots system to set the values
    to be either root or in user dotfiles
    """
    default_root = raw.get(cli, {}).get("CONFIG", {}).get("root_dir")
    root_dir = ret.get(cli, {}).get("root_dir")
    change = False
    if hasattr(os, "geteuid"):
        if not os.geteuid() == 0:
            change = True
    if root_dir and root_dir != default_root:
        change = True
    if change:
        for imp in ret:
            for key, val in ret[imp].items():
                if key == "root_dir":
                    continue
                default_opt = raw[imp].get("CONFIG", {}).get(key, {})
                if (
                    (key.endswith("_dir") or key.endswith("_path"))
                    and val is default_opt.get("default", "")
                    and os.path.isabs(val)
                ):
                    match = re.search(f"{os.sep+imp}($|{os.sep})", val)  # /imp or /imp/
                    if match:
                        # converts /usr/var/log/MATCH to ~/.MATCH/log
                        # and /usr/var/log/MATCH/name to ~/.MATCH/log/name
                        group = match.span()
                        before_match = val[: group[0]]
                        after_match = val[group[1] :]

                        # build up the dir - custom root or ~/?
                        if root_dir:
                            dot_path = [root_dir]
                        else:
                            dot_path = ["~", f".{imp}"]

                        dot_path.append(before_match.split(os.sep)[-1])

                        if after_match:
                            dot_path.append(after_match)

                        # create path
                        tgt = os.path.expanduser(os.sep.join(dot_path))

                        # make sure the path ends in / if it was passed in that way
                        if val.endswith(os.sep) and not tgt.endswith(os.sep):
                            tgt += os.sep

                        ret[imp][key] = tgt

    return ret
