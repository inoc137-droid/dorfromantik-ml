from dorfromantik.tiles import rotate_edges, TILES


def test_rotation_6_is_identity():
    e = TILES[0].edges
    assert rotate_edges(e, 6) == e
    assert rotate_edges(e, 0) == e

print(test_rotation_6_is_identity())
