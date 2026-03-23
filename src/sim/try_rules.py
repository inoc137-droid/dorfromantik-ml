from dorfromantik.state import State
from dorfromantik.rules import legal_actions, is_legal_placement


def main():
    s = State()

    tile_id = 0
    actions = legal_actions(s, tile_id)
    print("First move actions:", len(actions), actions[:10])

    # Nimm die erste legale Aktion und platziere sie
    pos, rot = actions[0]
    s.place_tile(pos, tile_id, rot)
    print("Placed tile", tile_id, "at", pos, "rot", rot)

    # Nächstes Tile testen
    tile_id2 = 1
    actions2 = legal_actions(s, tile_id2)
    print("Second move actions:", len(actions2), actions2[:10])

    # Beispiel: explizit eine Position prüfen
    test_pos = (1, 0)
    for r in range(6):
        ok = is_legal_placement(s, test_pos, tile_id2, r)
        print("tile", tile_id2, "at", test_pos, "rot", r, "->", ok)


if __name__ == "__main__":
    main()
