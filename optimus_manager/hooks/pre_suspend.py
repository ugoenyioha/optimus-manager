import sys
from ..config import load_config
from .. import var
from ..log_utils import set_logger_config, get_logger


def main():

    prev_state = var.load_state()

    if prev_state is None or prev_state["type"] != "done":
        return

    switch_id = prev_state["switch_id"]

    set_logger_config("switch", switch_id)
    logger = get_logger()

    current_mode = prev_state["current_mode"]

    try:
        logger.info("# Pre-suspend hook")

        logger.info("Previous state was: %s", str(prev_state))

        config = load_config()
        switching_option = config["optimus"]["switching"]
        bbswitch_enabled = switching_option == "bbswitch"

        logger.info("Switching option: %s", switching_option)

        if current_mode != "integrated" or not bbswitch_enabled:
            logger.info("Nothing to do")

        else:
            logger.info("Turning bbswitch on")
            with open("/proc/acpi/bbswitch", "w") as f:
                f.write("ON")

        state = {
            "type": "pending_post_resume",
            "switch_id": switch_id,
            "current_mode": current_mode,
            "bbswitch": bbswitch_enabled
        }

        var.write_state(state)

    # pylint: disable=W0703
    except Exception:

        logger.exception("Pre-suspend setup error")

        state = {
            "type": "pre_suspend_failed",
            "switch_id": switch_id,
            "current_mode": current_mode
        }

        var.write_state(state)
        sys.exit(1)

    else:
        logger.info("Pre-suspend hook completed successfully.")


if __name__ == "__main__":
    main()
