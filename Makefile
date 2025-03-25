NAME = RallymanGTapp

SRC_DIR = sources

SRC = $(SRC_DIR)/main.cpp\
	$(SRC_DIR)/Dice.cpp\
	$(SRC_DIR)/Driver.cpp\
	$(SRC_DIR)/Game.cpp\
	$(SRC_DIR)/Stats.cpp\
	$(SRC_DIR)/Team.cpp\
	$(SRC_DIR)/Tire.cpp\
	$(SRC_DIR)/Track.cpp


OBJ_DIR = objects

OBJ = $(patsubst $(SRC_DIR)/%.cpp, $(OBJ_DIR)/%.o, $(SRC))

COMP = c++

CFLAGS = -Wall -Wextra -Werror -std=c++20 -g

LDLFLAGS = -lsqlite3

all: $(NAME)

$(OBJ_DIR)/%.o: $(SRC_DIR)/%.cpp
		@$(COMP) $(CFLAGS) -c $< -o $@

$(NAME): $(OBJ_DIR) $(OBJ)
		@$(COMP) $(CFLAGS) $(OBJ) -o $(NAME) $(LDLFLAGS)
		@echo "\n\033[0;32mLet's roll!\033[0m\n"

$(OBJ_DIR):
		@mkdir -p $(OBJ_DIR)

clean:
		@rm -f $(OBJ)
		@rm -rf $(OBJ_DIR)

fclean: clean
		@rm -f $(NAME)
		@echo "\n\033[0;31mAll is gone\033[0m\n"

re: fclean all

.PHONY: all clean re fclean