def view_at(
    state: State, layout_x: float, layout_y: float
) -> tuple[Window | None, Surface | None, float, float]:
    maybe_node = state.scene.tree.node.node_at(
        layout_x,
        layout_y,
    )
    if maybe_node is None or maybe_node[0].type != SceneNodeType.BUFFER:
        return None, None, 0, 0

    node, sx, sy = maybe_node
    scene_buffer = SceneBuffer.from_node(node)
    if scene_buffer is None:
        return None, None, 0, 0
    scene_surface = SceneSurface.from_buffer(scene_buffer)
    if scene_surface is None:
        return None, None, 0, 0

    surface = scene_surface.surface
    tree = cast(SceneTree, node.parent)

    # Find the node corresponding to the view at the root of this tree
    while tree.node.data is not None:
        tree = cast(SceneTree, tree.node.parent)

    return tree.node.data, surface, sx, sy
