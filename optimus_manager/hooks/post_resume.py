import sys
from .. import var
from ..log_utils import set_logger_config, get_logger


def main():

    prev_state = var.load_state()

    if prev_state is None or prev_state["type"] != "pending_post_resume":
        return

    switch_id = prev_state["switch_id"]

    set_logger_config("switch", switch_id)
    logger = get_logger()

    current_mode = prev_state["current_mode"]

    try:
        logger.info("# Post-resume hook")

        logger.info("Previous state was: %s", str(prev_state))

        bbswitch_enabled = prev_state["bbswitch"]

        if current_mode != "integrated" or not bbswitch_enabled:
            logger.info("Nothing to do")

        else:
            logger.info("Turning bbswitch back off")
            with open("/proc/acpi/bbswitch", "w") as f:
                f.write("OFF")

        state = {
            "type": "done",
            "switch_id": switch_id,
            "current_mode": current_mode,
        }

        var.write_state(state)

    # pylint: disable=W0703
    except Exception:

        logger.exception("Post-resume setup error")

        state = {
            "type": "post_resume_failed",
            "switch_id": switch_id,
            "current_mode": current_mode
        }

        var.write_state(state)
        sys.exit(1)

    else:
        logger.info("Post-resume hook completed successfully.")


if __name__ == "__main__":
    main()
