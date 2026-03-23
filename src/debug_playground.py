import dorfromantik.state as state
import dorfromantik.tile_types as tt
import dorfromantik.dsu_update as du

# Board erzeugen
s = state.State()


# Beispieltiles legen
s.place_tile((0, 0), tile_id=0, rot=0)
s.place_tile((1, 0), tile_id=3, rot=2)

# Jetzt das interessante Tile
pos = (0, 1)
tile_id = 5
rot = 1

breakpoint()

s.place_tile(pos, tile_id, rot)

breakpoint()