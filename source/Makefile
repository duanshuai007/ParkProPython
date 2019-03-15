OBJS    := msgqueue.o
CURDIR  := $(ROOT_DIR)/source

all: $(OBJS)
$(OBJS) : %.o : %.c
	$(CC) -c $^ $(X_FLAGS) $(X_INCDIR) -o $@
