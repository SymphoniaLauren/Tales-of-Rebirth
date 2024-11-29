# Currently unused
EE_LIB = build/battle_subs.a

# Directories
SRC_DIR := src
BUILD_DIR := build

# Define rwildcard for recursive file searching
rwildcard = $(foreach d,$(wildcard $1/*),$(call rwildcard,$d,$2) $(filter $(subst *,%,$2),$d))

# Gather source files
EE_CPP_SRCS := $(strip $(call rwildcard,$(SRC_DIR),*.cpp))
EE_C_SRCS += $(strip $(call rwildcard,$(SRC_DIR),*.c))
# $(info EE_SRCS: $(EE_SRCS))

# Generate object files
EE_OBJS := $(patsubst $(SRC_DIR)/%.cpp,$(BUILD_DIR)/%.o,$(EE_CPP_SRCS))
EE_OBJS += $(patsubst $(SRC_DIR)/%.c,$(BUILD_DIR)/%.o,$(EE_C_SRCS))
# $(info EE_OBJS: $(EE_OBJS))

# Generate dependency files, so header changes trigger recompile
DEPENDS := $(patsubst $(SRC_DIR)/%.cpp,$(BUILD_DIR)/%.d,$(EE_CPP_SRCS))
DEPENDS += $(patsubst $(SRC_DIR)/%.c,$(BUILD_DIR)/%.d,$(EE_C_SRCS))
# $(info DEPENDS: $(DEPENDS))

# Common compilation flags, mostly ABI setup so we can interop with old SDK
EE_FLAGS := -mabi=eabi -mno-abicalls -mlong32 -fno-builtin-printf 

# Specialized compilation flags
EE_CFLAGS := $(EE_FLAGS) -Wno-implicit-function-declaration -Wno-unused-variable -Wno-incompatible-pointer-types -Wno-int-conversion
EE_CXXFLAGS := $(EE_FLAGS) -fno-exceptions -fno-rtti

# Missing DEPENDS are OK
-include $(DEPENDS)

# Targets
all: $(EE_LIB) $(EE_OBJS)

clean:
	rm -f $(EE_LIB) $(EE_OBJS) $(DEPENDS)

include Makefile.pref
include Makefile.eeglobal