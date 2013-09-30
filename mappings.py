colour_map = { 
               0b000100 : ((0  , 0  , 0, 0   ), "Off"          ), 
               0b000101 : ((255, 0  , 0, 127 ), "Red Low"      ), 
               0b000110 : ((255, 0  , 0, 180 ), "Red Medium"   ), 
               0b000111 : ((255, 0  , 0, 255 ), "Red Full"     ), 
               0b010100 : ((0  , 255, 0, 127 ), "Green Low"    ), 
               0b010101 : ((255, 220, 0, 127 ), "Amber Low"    ), 
               0b010110 : ((255, 150, 0, 127 ), "Amber Medium" ), 
               0b010111 : ((255, 100, 0, 170 ), "Amber 1"      ), 
               0b100100 : ((0  , 255, 0, 180 ), "Green Medium" ), 
               0b100101 : ((200, 127, 0, 170 ), "Amber 2"      ), 
               0b100110 : ((255, 220, 0, 170 ), "Amber 3"      ), 
               0b100111 : ((255, 150, 0, 255 ), "Amber High"   ), 
               0b110100 : ((0  , 255, 0, 255 ), "Green Full"   ), 
               0b110101 : ((255, 127, 0, 170 ), "Amber 4"      ), 
               0b110110 : ((230, 255, 0, 255 ), "Yellow"       ), 
               0b110111 : ((255, 220, 0, 255 ), "Amber Full"   )  
             }	

def getColour(val):
	val &= 0b110011
	val |= 0b000100
	return colour_map[val][0]

def getColourName(val):
	val &= 0b110011
	val |= 0b000100
	return colour_map[val][1]

def colourStrToMIDI(name):
	for key in colour_map:
		if colour_map[key][1] == name:
			return key



osc = {
  "has loop"            : (0, ("loop_len",            ), lambda x: bool(x)),
  "has loop not rec"    : (0, ("loop_len", "state"    ), lambda x: (bool(x[0])) and (x[1] != 2.0)),
  "waiting"             : (0, ("waiting",             ), lambda x: bool(x)),
  "waiting for record"  : (0, ("waiting", "state"     ), lambda x: bool(x[0]) and (x[1] == 1.0)),
  "waiting for overdub" : (0, ("waiting", "state"     ), lambda x: bool(x[0]) and (x[1] == 5.0)),
  "waiting for replace" : (0, ("waiting", "state"     ), lambda x: bool(x[0]) and (x[1] == 8.0)),
  "next state"          : (0, ("next_state",          ), lambda x: bool(x)),
  #"loop restarted"      : (0, ("loop_pos", "loop_len" ), lambda x: ((x[0] >= (x[1] - 0.05)) or x[0] <= 0.2) and bool(x[1])),
  #"cycle restarted"     : (0, ("loop_pos", "cycle_len"), lambda x: (x[0] >= x[1] and x[0] <= x[1] + 0.01) and bool(x[2])),
  "off"                 : (0, ("state",               ), lambda x: x == 0.0 ),
  "waiting to start"    : (0, ("state",               ), lambda x: x == 1.0 ),
  "recording"           : (0, ("state",               ), lambda x: x == 2.0 ),
  "waiting to stop"     : (0, ("state",               ), lambda x: x == 3.0 ),
  "playing"             : (0, ("state",               ), lambda x: x == 4.0 ),
  "overdubbing"         : (0, ("state",               ), lambda x: x == 5.0 ),
  "multiplying"         : (0, ("state",               ), lambda x: x == 6.0 ),
  "inserting"           : (0, ("state",               ), lambda x: x == 7.0 ),
  "replacing"           : (0, ("state",               ), lambda x: x == 8.0 ),
  "delay mode"          : (0, ("state",               ), lambda x: x == 9.0 ),
  "muted"               : (0, ("state",               ), lambda x: x == 10.0),
  "scratching"          : (0, ("state",               ), lambda x: x == 11.0),
  "oneshot"             : (0, ("state",               ), lambda x: x == 12.0),
  "substituting"        : (0, ("state",               ), lambda x: x == 13.0),
  "paused"              : (0, ("state",               ), lambda x: x == 14.0),
  "soloed"              : (0, ("is_soloed",           ), lambda x: bool(x)),
	"position < previous" : (0, ("loop_pos", "loop_pos" ), lambda x: x[0] < x[1]),
  "using common in"     : (0, ("use_common_ins",      ), lambda x: bool(x)),
  "using common out"    : (0, ("use_common_outs",     ), lambda x: bool(x)),
  "global dry"          : (1, ("dry",                 ), lambda x: bool(x)),
  "global wet"          : (1, ("wet"                  ), lambda x: bool(x)),
	"main out"            : (0, ("use_common_outs",     ), lambda x: bool(x)),
	"main in"             : (0, ("use_common_ins",      ), lambda x: bool(x)),
	"mute quantized"      : (0, ("mute_quantized",      ), lambda x: bool(x)),
	"dry"                 : (0, ("dry",                 ), lambda x: bool(x)),
	"sync"                : (0, ("sync",                ), lambda x: bool(x)),
  "rate"                : (0, ("rate",                ), lambda x: x == 1.0),
	"undos available"     : (0, ("undos_avail",         ), lambda x: x),
	"redos available"     : (0, ("redos_avail",         ), lambda x: x),
  #"global tap tempo"    : (1, ("tap_tempo",            ), lambda x: True   )
  "selected loop"       : (1, ("selected_loop_num",    ), lambda x: x   )
					}

ledToMIDI = (
  (176, 104), (176, 105), (176, 106), (176, 107), (176, 108), (176, 109), (176, 110), (176, 111),
  (144,   0), (144,   1), (144,   2), (144,   3), (144,   4), (144,   5), (144,   6), (144,   7), (144,   8),
  (144,  16), (144,  17), (144,  18), (144,  19), (144,  20), (144,  21), (144,  22), (144,  23), (144,  24),
  (144,  32), (144,  33), (144,  34), (144,  35), (144,  36), (144,  37), (144,  38), (144,  39), (144,  40),
  (144,  48), (144,  49), (144,  50), (144,  51), (144,  52), (144,  53), (144,  54), (144,  55), (144,  56),
  (144,  64), (144,  65), (144,  66), (144,  67), (144,  68), (144,  69), (144,  70), (144,  71), (144,  72),
  (144,  80), (144,  81), (144,  82), (144,  83), (144,  84), (144,  85), (144,  86), (144,  87), (144,  88),
  (144,  96), (144,  97), (144,  98), (144,  99), (144, 100), (144, 101), (144, 102), (144, 103), (144, 104),
  (144, 112), (144, 113), (144, 114), (144, 115), (144, 116), (144, 117), (144, 118), (144, 119), (144, 120)
               )

led_midi = list(ledToMIDI)
led_midi.reverse()

coordToMIDI = {}
for j in range(0,8):
	coordToMIDI[(0,j)] = led_midi.pop()
for i in range(1,9):
	for j in range(0,9):
		coordToMIDI[(i,j)] = led_midi.pop()

del led_midi

BLINK = 0b110011

reset = (176, 0, 0);

init_colours = [{ 
		#coordToMIDI[(1,1)] : colourStrToMIDI("Red Full") ,
		#coordToMIDI[(2,1)] : colourStrToMIDI("Red Full") ,
		#coordToMIDI[(3,1)] : colourStrToMIDI("Red Full") ,
		#coordToMIDI[(4,1)] : colourStrToMIDI("Red Full") ,
		#coordToMIDI[(5,1)] : colourStrToMIDI("Red Full") ,
		#coordToMIDI[(6,1)] : colourStrToMIDI("Red Full") ,
		#coordToMIDI[(7,1)] : colourStrToMIDI("Red Full") ,
		#coordToMIDI[(8,1)] : colourStrToMIDI("Red Full") ,

		coordToMIDI[(1,3)] : colourStrToMIDI("Amber High") ,
		coordToMIDI[(2,3)] : colourStrToMIDI("Amber High") ,
		coordToMIDI[(3,3)] : colourStrToMIDI("Amber High") ,
		coordToMIDI[(4,3)] : colourStrToMIDI("Amber High") ,
		coordToMIDI[(5,3)] : colourStrToMIDI("Amber High") ,
		coordToMIDI[(6,3)] : colourStrToMIDI("Amber High") ,
		coordToMIDI[(7,3)] : colourStrToMIDI("Amber High") ,
		coordToMIDI[(8,3)] : colourStrToMIDI("Amber High") ,

		coordToMIDI[(1,4)] : colourStrToMIDI("Amber High") ,
		coordToMIDI[(2,4)] : colourStrToMIDI("Amber High") ,
		coordToMIDI[(3,4)] : colourStrToMIDI("Amber High") ,
		coordToMIDI[(4,4)] : colourStrToMIDI("Amber High") ,
		coordToMIDI[(5,4)] : colourStrToMIDI("Amber High") ,
		coordToMIDI[(6,4)] : colourStrToMIDI("Amber High") ,
		coordToMIDI[(7,4)] : colourStrToMIDI("Amber High") ,
		coordToMIDI[(8,4)] : colourStrToMIDI("Amber High") ,

		}, {}, {}, {}]

init_colours[2] = init_colours[0]

oscToMIDI = [{
		#("global dry"         , coordToMIDI[(0,0)])  :  (-2, colourStrToMIDI("Red Full")           , colourStrToMIDI("Off")),
		#("selected loop"      , coordToMIDI[(0,7)]) :  (-2, colourStrToMIDI("Green Full")          , colourStrToMIDI("Off"), -1, lambda x: x[0] == x[1]),
		("mute quantized"    , coordToMIDI[(0,2)]) :  (0, colourStrToMIDI("Amber Full")    , colourStrToMIDI("Off")),
		("sync"              , coordToMIDI[(0,5)]) :  (0, colourStrToMIDI("Amber Full")    , colourStrToMIDI("Off")),


		#("waiting for record"  , ledToMIDI[1]) : (1, colourStrToMIDI("Yellow")          , colourStrToMIDI("Off")),
		#("waiting to start"  , ledToMIDI[1]) : (1, colourStrToMIDI("Yellow")          , colourStrToMIDI("Off")),
		#("waiting to stop"  , ledToMIDI[1]) : (1, colourStrToMIDI("Yellow")          , colourStrToMIDI("Off")),

		("recording"          , coordToMIDI[(1,0)]) :  (0, colourStrToMIDI("Red Full")             , None),
		("recording"          , coordToMIDI[(2,0)]) :  (1, colourStrToMIDI("Red Full")             , None),
		("recording"          , coordToMIDI[(3,0)]) :  (2, colourStrToMIDI("Red Full")             , None),
		("recording"          , coordToMIDI[(4,0)]) :  (3, colourStrToMIDI("Red Full")             , None),
		("recording"          , coordToMIDI[(5,0)]) :  (4, colourStrToMIDI("Red Full")             , None),
		("recording"          , coordToMIDI[(6,0)]) :  (5, colourStrToMIDI("Red Full")             , None),
		("recording"          , coordToMIDI[(7,0)]) :  (6, colourStrToMIDI("Red Full")             , None),
		("recording"          , coordToMIDI[(8,0)]) :  (7, colourStrToMIDI("Red Full")             , None),

		("waiting for record"          , coordToMIDI[(1,0)]) :  (0, colourStrToMIDI("Red Full") & BLINK    , None),
		("waiting for record"          , coordToMIDI[(2,0)]) :  (1, colourStrToMIDI("Red Full") & BLINK    , None),
		("waiting for record"          , coordToMIDI[(3,0)]) :  (2, colourStrToMIDI("Red Full") & BLINK    , None),
		("waiting for record"          , coordToMIDI[(4,0)]) :  (3, colourStrToMIDI("Red Full") & BLINK    , None),
		("waiting for record"          , coordToMIDI[(5,0)]) :  (4, colourStrToMIDI("Red Full") & BLINK    , None),
		("waiting for record"          , coordToMIDI[(6,0)]) :  (5, colourStrToMIDI("Red Full") & BLINK    , None),
		("waiting for record"          , coordToMIDI[(7,0)]) :  (6, colourStrToMIDI("Red Full") & BLINK    , None),
		("waiting for record"          , coordToMIDI[(8,0)]) :  (7, colourStrToMIDI("Red Full") & BLINK    , None),

		("playing"   , coordToMIDI[(1,0)]) :  (0, colourStrToMIDI("Green Full")           , None),
		("playing"   , coordToMIDI[(2,0)]) :  (1, colourStrToMIDI("Green Full")           , None),
		("playing"   , coordToMIDI[(3,0)]) :  (2, colourStrToMIDI("Green Full")           , None),
		("playing"   , coordToMIDI[(4,0)]) :  (3, colourStrToMIDI("Green Full")           , None),
		("playing"   , coordToMIDI[(5,0)]) :  (4, colourStrToMIDI("Green Full")           , None),
		("playing"   , coordToMIDI[(6,0)]) :  (5, colourStrToMIDI("Green Full")           , None),
		("playing"   , coordToMIDI[(7,0)]) :  (6, colourStrToMIDI("Green Full")           , None),
		("playing"   , coordToMIDI[(8,0)]) :  (7, colourStrToMIDI("Green Full")           , None),

		("muted"   , coordToMIDI[(1,0)]) :  (0, colourStrToMIDI("Green Full")           , None),
		("muted"   , coordToMIDI[(2,0)]) :  (1, colourStrToMIDI("Green Full")           , None),
		("muted"   , coordToMIDI[(3,0)]) :  (2, colourStrToMIDI("Green Full")           , None),
		("muted"   , coordToMIDI[(4,0)]) :  (3, colourStrToMIDI("Green Full")           , None),
		("muted"   , coordToMIDI[(5,0)]) :  (4, colourStrToMIDI("Green Full")           , None),
		("muted"   , coordToMIDI[(6,0)]) :  (5, colourStrToMIDI("Green Full")           , None),
		("muted"   , coordToMIDI[(7,0)]) :  (6, colourStrToMIDI("Green Full")           , None),
		("muted"   , coordToMIDI[(8,0)]) :  (7, colourStrToMIDI("Green Full")           , None),

		("overdubbing"          , coordToMIDI[(1,0)]) :  (0, colourStrToMIDI("Yellow")             , None),
		("overdubbing"          , coordToMIDI[(2,0)]) :  (1, colourStrToMIDI("Yellow")             , None),
		("overdubbing"          , coordToMIDI[(3,0)]) :  (2, colourStrToMIDI("Yellow")             , None),
		("overdubbing"          , coordToMIDI[(4,0)]) :  (3, colourStrToMIDI("Yellow")             , None),
		("overdubbing"          , coordToMIDI[(5,0)]) :  (4, colourStrToMIDI("Yellow")             , None),
		("overdubbing"          , coordToMIDI[(6,0)]) :  (5, colourStrToMIDI("Yellow")             , None),
		("overdubbing"          , coordToMIDI[(7,0)]) :  (6, colourStrToMIDI("Yellow")             , None),
		("overdubbing"          , coordToMIDI[(8,0)]) :  (7, colourStrToMIDI("Yellow")             , None),

		("waiting for overdub"          , coordToMIDI[(1,0)]) :  (0, colourStrToMIDI("Yellow") & BLINK    , None),
		("waiting for overdub"          , coordToMIDI[(2,0)]) :  (1, colourStrToMIDI("Yellow") & BLINK    , None),
		("waiting for overdub"          , coordToMIDI[(3,0)]) :  (2, colourStrToMIDI("Yellow") & BLINK    , None),
		("waiting for overdub"          , coordToMIDI[(4,0)]) :  (3, colourStrToMIDI("Yellow") & BLINK    , None),
		("waiting for overdub"          , coordToMIDI[(5,0)]) :  (4, colourStrToMIDI("Yellow") & BLINK    , None),
		("waiting for overdub"          , coordToMIDI[(6,0)]) :  (5, colourStrToMIDI("Yellow") & BLINK    , None),
		("waiting for overdub"          , coordToMIDI[(7,0)]) :  (6, colourStrToMIDI("Yellow") & BLINK    , None),
		("waiting for overdub"          , coordToMIDI[(8,0)]) :  (7, colourStrToMIDI("Yellow") & BLINK    , None),

		("off"          , coordToMIDI[(1,0)]) :  (0, colourStrToMIDI("Off")             , None),
		("off"          , coordToMIDI[(2,0)]) :  (1, colourStrToMIDI("Off")             , None),
		("off"          , coordToMIDI[(3,0)]) :  (2, colourStrToMIDI("Off")             , None),
		("off"          , coordToMIDI[(4,0)]) :  (3, colourStrToMIDI("Off")             , None),
		("off"          , coordToMIDI[(5,0)]) :  (4, colourStrToMIDI("Off")             , None),
		("off"          , coordToMIDI[(6,0)]) :  (5, colourStrToMIDI("Off")             , None),
		("off"          , coordToMIDI[(7,0)]) :  (6, colourStrToMIDI("Off")             , None),
		("off"          , coordToMIDI[(8,0)]) :  (7, colourStrToMIDI("Off")             , None),

		("has loop"          , coordToMIDI[(1,0)]) :  (0, None             , colourStrToMIDI("Off")),
		("has loop"          , coordToMIDI[(2,0)]) :  (1, None             , colourStrToMIDI("Off")),
		("has loop"          , coordToMIDI[(3,0)]) :  (2, None             , colourStrToMIDI("Off")),
		("has loop"          , coordToMIDI[(4,0)]) :  (3, None             , colourStrToMIDI("Off")),
		("has loop"          , coordToMIDI[(5,0)]) :  (4, None             , colourStrToMIDI("Off")),
		("has loop"          , coordToMIDI[(6,0)]) :  (5, None             , colourStrToMIDI("Off")),
		("has loop"          , coordToMIDI[(7,0)]) :  (6, None             , colourStrToMIDI("Off")),
		("has loop"          , coordToMIDI[(8,0)]) :  (7, None             , colourStrToMIDI("Off")),

		("waiting for replace"          , coordToMIDI[(1,1)]) :  (0, colourStrToMIDI("Red Full")    & BLINK  , None),
		("waiting for replace"          , coordToMIDI[(2,1)]) :  (1, colourStrToMIDI("Red Full")    & BLINK  , None),
		("waiting for replace"          , coordToMIDI[(3,1)]) :  (2, colourStrToMIDI("Red Full")    & BLINK  , None),
		("waiting for replace"          , coordToMIDI[(4,1)]) :  (3, colourStrToMIDI("Red Full")    & BLINK  , None),
		("waiting for replace"          , coordToMIDI[(5,1)]) :  (4, colourStrToMIDI("Red Full")    & BLINK  , None),
		("waiting for replace"          , coordToMIDI[(6,1)]) :  (5, colourStrToMIDI("Red Full")    & BLINK  , None),
		("waiting for replace"          , coordToMIDI[(7,1)]) :  (6, colourStrToMIDI("Red Full")    & BLINK  , None),
		("waiting for replace"          , coordToMIDI[(8,1)]) :  (7, colourStrToMIDI("Red Full")    & BLINK  , None),

		("replacing"          , coordToMIDI[(1,1)]) :  (0, colourStrToMIDI("Red Full")             , colourStrToMIDI("Off")),
		("replacing"          , coordToMIDI[(2,1)]) :  (1, colourStrToMIDI("Red Full")             , colourStrToMIDI("Off")),
		("replacing"          , coordToMIDI[(3,1)]) :  (2, colourStrToMIDI("Red Full")             , colourStrToMIDI("Off")),
		("replacing"          , coordToMIDI[(4,1)]) :  (3, colourStrToMIDI("Red Full")             , colourStrToMIDI("Off")),
		("replacing"          , coordToMIDI[(5,1)]) :  (4, colourStrToMIDI("Red Full")             , colourStrToMIDI("Off")),
		("replacing"          , coordToMIDI[(6,1)]) :  (5, colourStrToMIDI("Red Full")             , colourStrToMIDI("Off")),
		("replacing"          , coordToMIDI[(7,1)]) :  (6, colourStrToMIDI("Red Full")             , colourStrToMIDI("Off")),
		("replacing"          , coordToMIDI[(8,1)]) :  (7, colourStrToMIDI("Red Full")             , colourStrToMIDI("Off")),


		("muted"              , coordToMIDI[(1,2)]) :  (0, colourStrToMIDI("Red Full")    , colourStrToMIDI("Off")),
		("muted"              , coordToMIDI[(2,2)]) :  (1, colourStrToMIDI("Red Full")    , colourStrToMIDI("Off")),
		("muted"              , coordToMIDI[(3,2)]) :  (2, colourStrToMIDI("Red Full")    , colourStrToMIDI("Off")),
		("muted"              , coordToMIDI[(4,2)]) :  (3, colourStrToMIDI("Red Full")    , colourStrToMIDI("Off")),
		("muted"              , coordToMIDI[(5,2)]) :  (4, colourStrToMIDI("Red Full")    , colourStrToMIDI("Off")),
		("muted"              , coordToMIDI[(6,2)]) :  (5, colourStrToMIDI("Red Full")    , colourStrToMIDI("Off")),
		("muted"              , coordToMIDI[(7,2)]) :  (6, colourStrToMIDI("Red Full")    , colourStrToMIDI("Off")),
		("muted"              , coordToMIDI[(8,2)]) :  (7, colourStrToMIDI("Red Full")    , colourStrToMIDI("Off")),

		("position < previous", coordToMIDI[(1,5)]) :  (0, colourStrToMIDI("Red Full")    , colourStrToMIDI("Off")),
		("position < previous", coordToMIDI[(2,5)]) :  (1, colourStrToMIDI("Red Full")    , colourStrToMIDI("Off")),
		("position < previous", coordToMIDI[(3,5)]) :  (2, colourStrToMIDI("Red Full")    , colourStrToMIDI("Off")),
		("position < previous", coordToMIDI[(4,5)]) :  (3, colourStrToMIDI("Red Full")    , colourStrToMIDI("Off")),
		("position < previous", coordToMIDI[(5,5)]) :  (4, colourStrToMIDI("Red Full")    , colourStrToMIDI("Off")),
		("position < previous", coordToMIDI[(6,5)]) :  (5, colourStrToMIDI("Red Full")    , colourStrToMIDI("Off")),
		("position < previous", coordToMIDI[(7,5)]) :  (6, colourStrToMIDI("Red Full")    , colourStrToMIDI("Off")),
		("position < previous", coordToMIDI[(8,5)]) :  (7, colourStrToMIDI("Red Full")    , colourStrToMIDI("Off")),

		("rate", coordToMIDI[(1,7)]) :  (0, colourStrToMIDI("Off")    , colourStrToMIDI("Red Full")),
		("rate", coordToMIDI[(2,7)]) :  (1, colourStrToMIDI("Off")    , colourStrToMIDI("Red Full")),
		("rate", coordToMIDI[(3,7)]) :  (2, colourStrToMIDI("Off")    , colourStrToMIDI("Red Full")),
		("rate", coordToMIDI[(4,7)]) :  (3, colourStrToMIDI("Off")    , colourStrToMIDI("Red Full")),
		("rate", coordToMIDI[(5,7)]) :  (4, colourStrToMIDI("Off")    , colourStrToMIDI("Red Full")),
		("rate", coordToMIDI[(6,7)]) :  (5, colourStrToMIDI("Off")    , colourStrToMIDI("Red Full")),
		("rate", coordToMIDI[(7,7)]) :  (6, colourStrToMIDI("Off")    , colourStrToMIDI("Red Full")),
		("rate", coordToMIDI[(8,7)]) :  (7, colourStrToMIDI("Off")    , colourStrToMIDI("Red Full")),

		("selected loop"      , coordToMIDI[(1,8)]) :  (-2, colourStrToMIDI("Green Full")          , colourStrToMIDI("Off"), 0, lambda x: x[0] == x[1]),
		("selected loop"      , coordToMIDI[(2,8)]) :  (-2, colourStrToMIDI("Green Full")          , colourStrToMIDI("Off"), 1, lambda x: x[0] == x[1]),
		("selected loop"      , coordToMIDI[(3,8)]) :  (-2, colourStrToMIDI("Green Full")          , colourStrToMIDI("Off"), -1, lambda x: x[0] == x[1]),
		#("selected loop"      , coordToMIDI[(3,8)]) :  (-2, colourStrToMIDI("Green Full")          , colourStrToMIDI("Off"), 2, lambda x: x[0] == x[1]),
		#("selected loop"      , coordToMIDI[(4,8)]) :  (-2, colourStrToMIDI("Green Full")          , colourStrToMIDI("Off"), 3, lambda x: x[0] == x[1]),
		#("selected loop"      , coordToMIDI[(5,8)]) :  (-2, colourStrToMIDI("Green Full")          , colourStrToMIDI("Off"), 4, lambda x: x[0] == x[1]),
		#("selected loop"      , coordToMIDI[(6,8)]) :  (-2, colourStrToMIDI("Green Full")          , colourStrToMIDI("Off"), 5, lambda x: x[0] == x[1]),
		#("selected loop"      , coordToMIDI[(7,8)]) :  (-2, colourStrToMIDI("Green Full")          , colourStrToMIDI("Off"), 6, lambda x: x[0] == x[1]),
		##("selected loop"      , coordToMIDI[(8,8)]) :  (-2, colourStrToMIDI("Green Full")          , colourStrToMIDI("Off"), 7, lambda x: x[0] == x[1]),

		#("position < previous", ledToMIDI[ 1]) :  (0, colourStrToMIDI("Red Full")      , colourStrToMIDI("Off")),
		#"reversing"      : (1,  0, colourStrToMIDI("Yellow")     | 0b001100, colourStrToMIDI("Off") | 0b001100),
		#"global dry"     : (2, -2, colourStrToMIDI("Amber Full") | 0b001100, colourStrToMIDI("Off") | 0b001100)
		}, {}, {}, {}]

oscToMIDI[2] = oscToMIDI[0]

dbl_buf = (176, 0)
rapid_up = 146

midiflags = {
	            "default" : 0b0100010,
	            "display" : 0,
	            "update"  : 2,
	            "flash"   : 3,
	            "copy"    : 4
                                    }

bindables = {
"insert":                               ("cmd",  0 ), 
"multiply":                             ("cmd",  0 ),
"mute":                                 ("cmd",  0 ),
"mute_off":                             ("cmd",  0 ), 
"mute_on":                              ("cmd",  0 ), 
"mute_trigger":                         ("cmd",  0 ), 
"oneshot":                              ("cmd",  0 ), 
"overdub":                              ("cmd",  0 ), 
"pause":                                ("cmd",  0 ), 
"pause_off":                            ("cmd",  0 ), 
"pause_on":                             ("cmd",  0 ), 
"record":                               ("cmd",  0 ), 
"record_exclusive":                     ("cmd",  0 ), 
"record_exclusive_next":                ("cmd",  0 ), 
"record_exclusive_prev":                ("cmd",  0 ), 
"record_or_overdub":                    ("cmd",  0 ), 
"record_or_overdub_excl":               ("cmd",  0 ), 
"record_or_overdub_excl_next":          ("cmd",  0 ), 
"record_or_overdub_excl_prev":          ("cmd",  0 ), 
"record_or_overdub_solo":               ("cmd",  0 ), 
"record_or_overdub_solo_next":          ("cmd",  0 ), 
"record_or_overdub_solo_prev":          ("cmd",  0 ), 
"record_or_overdub_solo_trig":          ("cmd",  0 ), 
"record_overdub_end_solo":              ("cmd",  0 ), 
"record_overdub_end_solo_trig":         ("cmd",  0 ), 
"record_solo":                          ("cmd",  0 ), 
"record_solo_next":                     ("cmd",  0 ), 
"record_solo_prev":                     ("cmd",  0 ), 
"redo":                                 ("cmd",  0 ), 
"redo_all":                             ("cmd",  0 ), 
"replace":                              ("cmd",  0 ), 
"reset_sync_pos":                       ("cmd",  0 ), 
"reverse":                              ("cmd",  0 ), 
"scratch":                              ("cmd",  0 ), 
"set_sync_pos":                         ("cmd",  0 ), 
"solo":                                 ("cmd",  0 ), 
"solo_next":                            ("cmd",  0 ), 
"solo_prev":                            ("cmd",  0 ), 
"substitute":                           ("cmd",  0 ), 
"trigger":                              ("cmd",  0 ), 
"undo":                                 ("cmd",  0 ), 
"undo_all":                             ("cmd",  0 ), 
"delay_trigger":                        ("ctrl", 0 ),
"dry":                                  ("ctrl", 0 ),
"fade_samples":                         ("ctrl", 0 ),
"feedback":                             ("ctrl", 0 ),
"input_gain":                           ("ctrl", 0 ),
"input_latency":                        ("ctrl", 0 ),
"jack_timebase_master":                 ("ctrl", 0 ),
"mute_quantized":                       ("ctrl", 0 ),
"output_latency":                       ("ctrl", 0 ),
"overdub_quantized":                    ("ctrl", 0 ),
"pan_1":                                ("ctrl", 0 ),
"pan_2":                                ("ctrl", 0 ),
"pan_3":                                ("ctrl", 0 ),
"pan_4":                                ("ctrl", 0 ),
"pitch_shift":                          ("ctrl", 0 ),
"playback_sync":                        ("ctrl", 0 ),
"quantize":                             ("ctrl", 0 ),
"rate":                                 ("ctrl", 0 ),
"rec_thresh":                           ("ctrl", 0 ),
"redo_is_tap":                          ("ctrl", 0 ),
"relative_sync":                        ("ctrl", 0 ),
"replace_quantized":                    ("ctrl", 0 ),
"round":                                ("ctrl", 0 ),
"round_integer_tempo":                  ("ctrl", 0 ),
"scratch_pos":                          ("ctrl", 0 ),
"stretch_ratio":                        ("ctrl", 0 ),
"sync":                                 ("ctrl", 0 ),
"tempo_stretch":                        ("ctrl", 0 ),
"trigger_latency":                      ("ctrl", 0 ),
"use_common_ins":                       ("ctrl", 0 ),
"use_common_outs":                      ("ctrl", 0 ),
"use_feedback_play":                    ("ctrl", 0 ),
"use_rate":                             ("ctrl", 0 ),
"use_safety_feedback":                  ("ctrl", 0 ),
"wet":                                  ("ctrl", 0 ),
"auto_disable_latency":                 ("ctrl", 1 ),
"eighth_per_cycle":                     ("ctrl", 1 ),
"output_midi_clock":                    ("ctrl", 1 ),
"save_loop":                            ("ctrl", 1 ),
"select_all_loops":                     ("ctrl", 1 ),
"select_next_loop":                     ("ctrl", 1 ),
"select_prev_loop":                     ("ctrl", 1 ),
"selected_loop_num":                    ("ctrl", 1 ),
"send_midi_start_on_trigger":           ("ctrl", 1 ),
"smart_eighths":                        ("ctrl", 1 ),
"sync_source":                          ("ctrl", 1 ),
"tap_tempo":                            ("ctrl", 1 ),
"tempo":                                ("ctrl", 1 ),
"use_midi_start":                       ("ctrl", 1 ),
"use_midi_stop":                        ("ctrl", 1 ),
}                                       

#channel can only be 0
midi_type = {
              (176, "ctrl"): "ccon",
              (176, "cmd"): "cc",
							(144, "cmd"): "on",
							(144, "ctrl"): "on"
						              }              


#/add_midi_binding ss "0 n 1  note record_or_overdub 4  0 1  norm 0 127" ""
#                     "channel type number command loop_index range_min range_max map_type midi_range_min midi_range_max"
midi = ({
            #coordToMIDI[(1,0)] : "0 n " + str(led2midi_map[8][1]) + " note recored_or_overdub 0 0 1 norm 0 127"
            #coordToMIDI[(0,0)] : ("dry", "-2"),
            coordToMIDI[(0,2)] : ("mute_quantized", "-1"),
            coordToMIDI[(4,8)] : ("undo_all", "-3"),
            coordToMIDI[(3,8)] : ("select_all_loops", "-2"),

            #coordToMIDI[(0,5)] : ("sync", "-3"),
            coordToMIDI[(0,0)] : ("sync", "-3"),

            coordToMIDI[(1,0)] : ("record_or_overdub", "0"),
            coordToMIDI[(2,0)] : ("record_or_overdub", "1"),
            coordToMIDI[(3,0)] : ("record_or_overdub", "2"),
            coordToMIDI[(4,0)] : ("record_or_overdub", "3"),
            coordToMIDI[(5,0)] : ("record_or_overdub", "4"),
            coordToMIDI[(6,0)] : ("record_or_overdub", "5"),
            coordToMIDI[(7,0)] : ("record_or_overdub", "6"),
            coordToMIDI[(8,0)] : ("record_or_overdub", "7"),

            coordToMIDI[(1,1)] : ("replace", "0"),
            coordToMIDI[(2,1)] : ("replace", "1"),
            coordToMIDI[(3,1)] : ("replace", "2"),
            coordToMIDI[(4,1)] : ("replace", "3"),
            coordToMIDI[(5,1)] : ("replace", "4"),
            coordToMIDI[(6,1)] : ("replace", "5"),
            coordToMIDI[(7,1)] : ("replace", "6"),
            coordToMIDI[(8,1)] : ("replace", "7"),

            coordToMIDI[(1,2)] : ("mute", "0"),
            coordToMIDI[(2,2)] : ("mute", "1"),
            coordToMIDI[(3,2)] : ("mute", "2"),
            coordToMIDI[(4,2)] : ("mute", "3"),
            coordToMIDI[(5,2)] : ("mute", "4"),
            coordToMIDI[(6,2)] : ("mute", "5"),
            coordToMIDI[(7,2)] : ("mute", "6"),
            coordToMIDI[(8,2)] : ("mute", "7"),

            coordToMIDI[(1,3)] : ("undo", "0"),
            coordToMIDI[(2,3)] : ("undo", "1"),
            coordToMIDI[(3,3)] : ("undo", "2"),
            coordToMIDI[(4,3)] : ("undo", "3"),
            coordToMIDI[(5,3)] : ("undo", "4"),
            coordToMIDI[(6,3)] : ("undo", "5"),
            coordToMIDI[(7,3)] : ("undo", "6"),
            coordToMIDI[(8,3)] : ("undo", "7"),

            coordToMIDI[(1,4)] : ("redo", "0"),
            coordToMIDI[(2,4)] : ("redo", "1"),
            coordToMIDI[(3,4)] : ("redo", "2"),
            coordToMIDI[(4,4)] : ("redo", "3"),
            coordToMIDI[(5,4)] : ("redo", "4"),
            coordToMIDI[(6,4)] : ("redo", "5"),
            coordToMIDI[(7,4)] : ("redo", "6"),
            coordToMIDI[(8,4)] : ("redo", "7"),

            coordToMIDI[(1,5)] : ("reverse", "0"),
            coordToMIDI[(2,5)] : ("reverse", "1"),
            coordToMIDI[(3,5)] : ("reverse", "2"),
            coordToMIDI[(4,5)] : ("reverse", "3"),
            coordToMIDI[(5,5)] : ("reverse", "4"),
            coordToMIDI[(6,5)] : ("reverse", "5"),
            coordToMIDI[(7,5)] : ("reverse", "6"),
            coordToMIDI[(8,5)] : ("reverse", "7"),

            coordToMIDI[(1,6)] : ("trigger", "0"),
            coordToMIDI[(2,6)] : ("trigger", "1"),
            coordToMIDI[(3,6)] : ("trigger", "2"),
            coordToMIDI[(4,6)] : ("trigger", "3"),
            coordToMIDI[(5,6)] : ("trigger", "4"),
            coordToMIDI[(6,6)] : ("trigger", "5"),
            coordToMIDI[(7,6)] : ("trigger", "6"),
            coordToMIDI[(8,6)] : ("trigger", "7"),

            coordToMIDI[(1,7)] : ("rate", "0", "1 0.5"),
            coordToMIDI[(2,7)] : ("rate", "1", "1 0.5"),
            coordToMIDI[(3,7)] : ("rate", "2", "1 0.5"),
            coordToMIDI[(4,7)] : ("rate", "3", "1 0.5"),
            coordToMIDI[(5,7)] : ("rate", "4", "1 0.5"),
            coordToMIDI[(6,7)] : ("rate", "5", "1 0.5"),
            coordToMIDI[(7,7)] : ("rate", "6", "1 0.5"),
            coordToMIDI[(8,7)] : ("rate", "7", "1 0.5"),

            coordToMIDI[(1,8)] : ("selected_loop_num", "0"),
            coordToMIDI[(2,8)] : ("selected_loop_num", "1"),
            #coordToMIDI[(3,8)] : ("selected_loop_num", "2"),
            #coordToMIDI[(4,8)] : ("selected_loop_num", "3"),
            #coordToMIDI[(5,8)] : ("selected_loop_num", "4"),
            #coordToMIDI[(6,8)] : ("selected_loop_num", "5"),
            #coordToMIDI[(7,8)] : ("selected_loop_num", "6"),
            ##coordToMIDI[(8,8)] : ("selected_loop_num", "7"),
	        }, 
					{},
					{
            #coordToMIDI[(1,0)] : "0 n " + str(led2midi_map[8][1]) + " note recored_or_overdub 0 0 1 norm 0 127"
            #coordToMIDI[(0,0)] : ("dry", "-2"),
            coordToMIDI[(0,2)] : ("mute_quantized", "-1"),
            coordToMIDI[(4,8)] : ("undo_all", "-3"),
            coordToMIDI[(3,8)] : ("select_all_loops", "-2"),

            #coordToMIDI[(0,5)] : ("sync", "-3"),
            coordToMIDI[(0,0)] : ("sync", "-3"),

            coordToMIDI[(1,0)] : ("record_or_overdub", "0"),
            coordToMIDI[(2,0)] : ("record_or_overdub", "1"),
            coordToMIDI[(3,0)] : ("record_or_overdub", "2"),
            coordToMIDI[(4,0)] : ("record_or_overdub", "3"),
            coordToMIDI[(5,0)] : ("record_or_overdub", "4"),
            coordToMIDI[(6,0)] : ("record_or_overdub", "5"),
            coordToMIDI[(7,0)] : ("record_or_overdub", "6"),
            coordToMIDI[(8,0)] : ("record_or_overdub", "7"),

            coordToMIDI[(1,1)] : ("replace", "0"),
            coordToMIDI[(2,1)] : ("replace", "1"),
            coordToMIDI[(3,1)] : ("replace", "2"),
            coordToMIDI[(4,1)] : ("replace", "3"),
            coordToMIDI[(5,1)] : ("replace", "4"),
            coordToMIDI[(6,1)] : ("replace", "5"),
            coordToMIDI[(7,1)] : ("replace", "6"),
            coordToMIDI[(8,1)] : ("replace", "7"),

            coordToMIDI[(1,2)] : ("mute", "0"),
            coordToMIDI[(2,2)] : ("mute", "1"),
            coordToMIDI[(3,2)] : ("mute", "2"),
            coordToMIDI[(4,2)] : ("mute", "3"),
            coordToMIDI[(5,2)] : ("mute", "4"),
            coordToMIDI[(6,2)] : ("mute", "5"),
            coordToMIDI[(7,2)] : ("mute", "6"),
            coordToMIDI[(8,2)] : ("mute", "7"),

            coordToMIDI[(1,3)] : ("undo", "0"),
            coordToMIDI[(2,3)] : ("undo", "1"),
            coordToMIDI[(3,3)] : ("undo", "2"),
            coordToMIDI[(4,3)] : ("undo", "3"),
            coordToMIDI[(5,3)] : ("undo", "4"),
            coordToMIDI[(6,3)] : ("undo", "5"),
            coordToMIDI[(7,3)] : ("undo", "6"),
            coordToMIDI[(8,3)] : ("undo", "7"),

            coordToMIDI[(1,4)] : ("redo", "0"),
            coordToMIDI[(2,4)] : ("redo", "1"),
            coordToMIDI[(3,4)] : ("redo", "2"),
            coordToMIDI[(4,4)] : ("redo", "3"),
            coordToMIDI[(5,4)] : ("redo", "4"),
            coordToMIDI[(6,4)] : ("redo", "5"),
            coordToMIDI[(7,4)] : ("redo", "6"),
            coordToMIDI[(8,4)] : ("redo", "7"),

            coordToMIDI[(1,5)] : ("reverse", "0"),
            coordToMIDI[(2,5)] : ("reverse", "1"),
            coordToMIDI[(3,5)] : ("reverse", "2"),
            coordToMIDI[(4,5)] : ("reverse", "3"),
            coordToMIDI[(5,5)] : ("reverse", "4"),
            coordToMIDI[(6,5)] : ("reverse", "5"),
            coordToMIDI[(7,5)] : ("reverse", "6"),
            coordToMIDI[(8,5)] : ("reverse", "7"),

            coordToMIDI[(1,6)] : ("trigger", "0"),
            coordToMIDI[(2,6)] : ("trigger", "1"),
            coordToMIDI[(3,6)] : ("trigger", "2"),
            coordToMIDI[(4,6)] : ("trigger", "3"),
            coordToMIDI[(5,6)] : ("trigger", "4"),
            coordToMIDI[(6,6)] : ("trigger", "5"),
            coordToMIDI[(7,6)] : ("trigger", "6"),
            coordToMIDI[(8,6)] : ("trigger", "7"),

            coordToMIDI[(1,7)] : ("rate", "0", "1 2"),
            coordToMIDI[(2,7)] : ("rate", "1", "1 2"),
            coordToMIDI[(3,7)] : ("rate", "2", "1 2"),
            coordToMIDI[(4,7)] : ("rate", "3", "1 2"),
            coordToMIDI[(5,7)] : ("rate", "4", "1 2"),
            coordToMIDI[(6,7)] : ("rate", "5", "1 2"),
            coordToMIDI[(7,7)] : ("rate", "6", "1 2"),
            coordToMIDI[(8,7)] : ("rate", "7", "1 2"),

            coordToMIDI[(1,8)] : ("selected_loop_num", "0"),
            coordToMIDI[(2,8)] : ("selected_loop_num", "1"),
							
							
							}, {})

