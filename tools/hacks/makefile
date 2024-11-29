EE_LIB = build/hack.a build/battle_subs.a
EE_OBJS = build/hack.o build/battle_subs.o
RB_OBJS = build/init.o 

EE_CFLAGS := -Wno-implicit-function-declaration -Wno-unused-variable -Wno-incompatible-pointer-types -Wno-int-conversion -mabi=eabi -mno-abicalls -mlong32 -fno-builtin-printf 
EE_CXXFLAGS = $(CFLAGS) -fno-exceptions -fno-rtti -mabi=eabi -mno-abicalls -mlong32 -fno-builtin-printf 

all: $(EE_LIB) $(EE_OBJS) $(RB_OBJS)

clean:
	rm -f $(EE_LIB) $(EE_OBJS) $(RB_OBJS)

include Makefile.pref
include Makefile.eeglobal