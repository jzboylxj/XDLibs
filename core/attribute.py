# coding: utf-8


def setNotKeyableAttributes(nodes,
                            attributes=["tx", "ty", "tz",
                                        "ro", "rx", "ry", "rz",
                                        "sx", "sy", "sz",
                                        "v"]):
    """Set not keyable attributes of a node.

    By defaul will set not keyable the rotation, scale and translation.

    Arguments:
        node(dagNode): The node with the attributes to set keyable.
        attributes (list of str): The list of the attributes to set not keyable
    """

    if not isinstance(nodes, list):
        nodes = [nodes]

    for attr_name in attributes:
        for node in nodes:
            node.setAttr(attr_name, lock=False, keyable=False, cb=True)
