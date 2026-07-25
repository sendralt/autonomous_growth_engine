from helpers.print_style import PrintStyle


def install():
    """Called after plugin is placed in usr/plugins/."""
    PrintStyle(font_color="green").print(
        "Autonomous Growth Engine installed. "
        "Use the Growth button in the sidebar to initialize."
    )


def uninstall():
    """Called before plugin directory is deleted."""
    PrintStyle(font_color="yellow").print("Autonomous Growth Engine uninstalled.")
