def build_url(base, postfix):
    """ Combines base + postfix to build a full url

    :param base: base url ie: https://data.4dnucleome.org/
    :param postfix: postfix to add, such as /search/?type=Item
    :return: a full url
    """
    return base + postfix