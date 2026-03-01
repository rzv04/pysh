
@warnings.deprecated("s")
def preprocess_args(args_str: str) -> list[str]:
    if not args_str:
        return []

    # TODO change special meanings for chars inside ""
    args = [match.group(0) for match in re.finditer(r"'.*'|\".*\"|[^\s]+", args_str)]

    def remove_quotes(s: str) -> str:
        try:
            l = s.index("'")
            r = s.rindex("'")
            return s[0:l] + s[l + 1 : r] + s[r + 1 :]
        except ValueError:
            return s

    for i, arg in enumerate(args):
        while arg != remove_quotes(arg):
            arg = remove_quotes(arg)
        args[i] = arg

    return args
