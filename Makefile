CC=gcc
RM=rm

CPATH       := .

OBJS    := source/msgqueue.o

ROOT_DIR    :=  $(shell pwd)
TARGET      := debug
INCDIRS     := include
X_FLAGS     := -g -Wall
X_INCDIR    := $(patsubst %, -I $(ROOT_DIR)/%, $(INCDIRS))

LD_FLAG     := -lssl -lcrypto -lnopoll -lmysqlclient -lpthread

NO_MAKE_DIR := include picture lib python
NO_MAKE     := $(patsubst %, grep -v % |, $(NO_MAKE_DIR))

SUBDIRS     = $(shell ls -l | grep ^d | awk '{print $$9}' | $(NO_MAKE) tr "\n" " ")

export CC X_FLAGS X_INCDIR ROOT_DIR SQL_HEAD_FILE

.PHONY: subdirs $(SUBDIRS)
.PHONY: clean

all:$(SUBDIRS)
	@echo "make all"
	$(CC) -o $(TARGET) $(X_FLAGS) $(X_INCDIR) main.c $(OBJS) lib/libwty.a ${LD_FLAG}

subdirs: $(SUBDIRS)
$(SUBDIRS) :
	@echo "make dir $@"
	@make -s -C $@

clean:
	@$(RM) -rf $(TARGET) $(OBJS)
