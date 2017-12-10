from Game import *
from Gui import *
import global_var

root = Board()

# ENGINE MECHANISM
root.game.fen_parse(START_FEN)

# GUI MECHANISM
root.gui_fen_parse(START_FEN)
root.gui.mainloop()

