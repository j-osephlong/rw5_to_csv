SKIP_LINES_WITH_PREFIXES = ["G0", "G1", "G2", "G3"]


def group_lines_into_command_blocks(lines: list[str]) -> list[list[str]]:
    """Group file lines into command blocks."""
    commands: list[list[str]] = []
    active_command = []

    """
    group lines in blocks of lines making up a command
    it's assumed that a command starts with a non-comment line, includes all following comment lines
    and ends before the next non comment line

    Example:
        GPS _____________________________   // Command starts
        --blahs blah blah
        --blahs blah blah blah
        --blah                              // Command ends
        GPS ____________________________    // New command starts

    Some lines start with prefixes that we want to ignore and not interrupt the record that they're within

    Example:
        GPS _____________________________   // Command starts
        --blahs blah blah
        G0 blah blah                        // Skip this line (prefix == G0)
        G1 blah blah                        // Skip this line
        G2 blah blah                        // Skip this line
        --blahs blah blah blah
        --blah                              // Command ends
        GPS ____________________________    // New command starts
    """

    stripped_lines = [line.strip() for line in lines]

    for line in stripped_lines:
        # skips lines with specific prefixes, act line they're not even there.
        if any(line.startswith(prefix) for prefix in SKIP_LINES_WITH_PREFIXES):
            continue

        line_is_comment = line.startswith("--")
        # If theres an active command and this line isn't comment
        #   Finish active command, start new command
        if len(active_command) > 0 and line_is_comment is False:
            commands.append(active_command)
            active_command = []

        # Append current line to active_command
        active_command.append(line)

    if len(active_command) > 0:
        commands.append(active_command)

    return commands
